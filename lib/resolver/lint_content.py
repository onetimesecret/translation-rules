#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Lint *consumer content* against a locale's resolved register. SPEC.md §6.2.

The sibling of resolver/lint.py. `lint_model` checks the **authority's** own
resolved model (good examples + embedded rationale docs); this checks the
**shipped app content** — onetimesecret `locales/content/<locale>/*.json` — for
the same forbidden register tokens, using the *same* matching engine.

Why this exists (translation-rules#42): the only gate that scanned shipped
content, the app's `validate-register.yml` -> `bin/lint-register`, was a
Phase-0 `LC_ALL=C` byte-grep that only worked for de_AT. It hard-errors on CJK
`substring` rules (ja/ko/zh) and false-positives on word boundaries elsewhere
(Vietnamese `bà` inside `bài`, French `te` inside `Hôte`), so it could not be
pointed at the other ~28 governed locales. This module reuses the resolver's
Unicode-correct, `substring`-capable, exception-honouring matcher instead, so
one engine covers every locale.

What it reuses (no second matcher, by construction):
  - resolver.matching.find_spans   — the four context modes, casefolded + NFC
  - resolver.lint._exception_spans — allowlisted `exceptions` occurrences
  - resolver.lint._hit_allowed     — a hit inside an exception span (du-in-Duden)

Which strings are scanned (deliberate, reviewable policy — SKIP_KEYS):
The register governs **rendered, end-user-facing copy**, so only those string
values are scanned. The content schema's non-rendered keys are skipped:
`source_hash` (a content hash), `renderer` (a render-mode tag), `skip` (a
control flag), `context`/`note` (translator guidance, never shown to users),
and any `_`-prefixed key (metadata blocks such as `_meta`,
`_translation_guidelines`). This both avoids false positives on English
translator notes and reproduces the onetimesecret#3530 baseline exactly
(13 cs / 2 ja / 34 nl = 49). The set is a module constant so it stays a
reviewable decision, not a buried heuristic.

The resolved register is obtained post-inheritance from a derived
`.resolved/<locale>.json` (the shared derive action's output) via
`register_from_resolved` — never re-parsed from raw YAML — so what the gate
enforces is exactly what the authority resolved.

Output is structured ({file, key, token, context, snippet}) with a clear
pass/fail exit (SPEC §6.2), so CI and agents know when a locale's content is
clean. Exit codes mirror bin/lint-register for drop-in CI familiarity:

    0  clean (or the locale carries no forbidden_tokens — nothing to lint)
    1  one or more error-severity forbidden-token hits
    2  usage / config error (bad args, unreadable/registerless resolved JSON)
    3  a content glob expanded to zero files (likely a misconfigured CI path)
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

# Allow running as a script (`python lib/resolver/lint_content.py`) or as a
# module (`from resolver.lint_content import ...`), mirroring resolve.py.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resolver.matching import VALID_MODES, find_spans
from resolver.lint import _exception_spans, _hit_allowed

FATAL = {"error"}

# Content-schema keys whose string values are NOT rendered to end users and so
# are out of register scope (see module docstring). Any `_`-prefixed key is also
# skipped (metadata blocks). Kept as a constant so the scan surface is explicit.
SKIP_KEYS = frozenset({"source_hash", "renderer", "skip", "context", "note"})

# Characters of original text shown on each side of a hit in `snippet`.
SNIPPET_WINDOW = 32


@dataclass
class ContentFinding:
    """One forbidden-token hit in a content string. `key` is the dotted JSON
    path to the offending string value (e.g. `web.login.button.text`); `snippet`
    is a windowed excerpt of the *original* text around the hit."""

    check: str
    severity: str
    file: str
    key: str
    token: str
    context: str
    snippet: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "severity": self.severity,
            "file": self.file,
            "key": self.key,
            "token": self.token,
            "context": self.context,
            "snippet": self.snippet,
        }


@dataclass
class ContentLintResult:
    locale: str
    findings: list[ContentFinding] = field(default_factory=list)
    files_scanned: int = 0
    strings_scanned: int = 0

    @property
    def ok(self) -> bool:
        return not any(f.severity in FATAL for f in self.findings)

    def as_dict(self) -> dict[str, Any]:
        return {
            "locale": self.locale,
            "ok": self.ok,
            "files_scanned": self.files_scanned,
            "strings_scanned": self.strings_scanned,
            "findings": [f.as_dict() for f in self.findings],
        }


def _fold_map(value: str) -> tuple[str, list[int], str]:
    """Return (folded, fold_to_orig, nfc) for `value`.

    `folded` equals resolver.matching._casefold(value) — NFC then casefold — so
    spans from find_spans index into it directly. `fold_to_orig[i]` is the index
    into `nfc` of the original character that produced folded[i], letting a
    folded span be projected back onto the *original* text for a faithful
    snippet even when casefolding changes length (German ß -> ss, ligatures).
    Unicode case folding is a context-free per-code-point mapping, so folding
    char-by-char yields the same string as folding the whole — the offsets line
    up with find_spans by construction."""
    nfc = unicodedata.normalize("NFC", value)
    parts: list[str] = []
    fold_to_orig: list[int] = []
    for i, ch in enumerate(nfc):
        folded_ch = ch.casefold()
        parts.append(folded_ch)
        fold_to_orig.extend([i] * len(folded_ch))
    return "".join(parts), fold_to_orig, nfc


def _snippet(nfc: str, fold_to_orig: list[int], span: tuple[int, int]) -> str:
    """A single-line excerpt of the original (NFC) text around a folded span."""
    fs, fe = span
    start = fold_to_orig[fs]
    end = fold_to_orig[fe - 1] + 1 if fe > fs else start
    lo = max(0, start - SNIPPET_WINDOW)
    hi = min(len(nfc), end + SNIPPET_WINDOW)
    excerpt = nfc[lo:hi].replace("\n", " ").replace("\r", " ").strip()
    return f"{'…' if lo > 0 else ''}{excerpt}{'…' if hi < len(nfc) else ''}"


def iter_content_strings(data: Any, prefix: str = "") -> Iterator[tuple[str, str]]:
    """Yield (dotted_key, string_value) for every rendered string in a content
    document, skipping SKIP_KEYS and `_`-prefixed (metadata) keys. Recurses into
    nested objects and lists; list indices join with `.` like object keys."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key in SKIP_KEYS or key.startswith("_"):
                continue
            yield from iter_content_strings(value, f"{prefix}.{key}" if prefix else key)
    elif isinstance(data, list):
        for i, value in enumerate(data):
            yield from iter_content_strings(
                value, f"{prefix}.{i}" if prefix else str(i)
            )
    elif isinstance(data, str):
        yield prefix, data


def _normalize_register(
    register: dict[str, Any] | None,
) -> tuple[list[dict], list[dict]]:
    """Pull (forbidden_tokens, exceptions) out of a resolved register, defaulting
    each to an empty list (a registerless or token-free locale scans clean)."""
    register = register or {}
    return (
        register.get("forbidden_tokens") or [],
        register.get("exceptions") or [],
    )


def register_from_resolved(resolved: dict[str, Any]) -> dict[str, Any] | None:
    """The `register` block of a derived `.resolved/<locale>.json`. None when the
    locale carries no register (nothing to enforce)."""
    return resolved.get("register")


def lint_value(
    forbidden: list[dict[str, Any]],
    exceptions: list[dict[str, Any]],
    file: str,
    key: str,
    value: str,
) -> list[ContentFinding]:
    """Forbidden-token findings for one content string. A hit is suppressed only
    when it falls inside an allowlisted exception occurrence (du-in-Duden), never
    merely because the exception appears elsewhere in the same string."""
    findings: list[ContentFinding] = []
    exc_spans = _exception_spans(value, exceptions)
    # Built lazily on the first real hit (most strings are clean) and reused
    # across this value's hits. None until needed; a 3-tuple once computed.
    fold: tuple[str, list[int], str] | None = None
    for ft in forbidden:
        token = ft.get("token", "")
        mode = ft.get("context", "any")
        hits = find_spans(value, token, mode)
        for hit in hits:
            if _hit_allowed(hit, exc_spans):
                continue
            if fold is None:
                fold = _fold_map(value)
            _folded, fold_to_orig, nfc = fold
            findings.append(
                ContentFinding(
                    check="forbidden_token_content",
                    severity=ft.get("severity", "error"),
                    file=file,
                    key=key,
                    token=token,
                    context=mode,
                    snippet=_snippet(nfc, fold_to_orig, hit),
                )
            )
    return findings


def lint_content(
    locale: str,
    register: dict[str, Any] | None,
    files: Iterable[tuple[str, Any]],
) -> ContentLintResult:
    """Lint each (file_label, parsed_json) against the resolved register. Pure:
    callers supply already-parsed content so this stays free of I/O."""
    forbidden, exceptions = _normalize_register(register)
    result = ContentLintResult(locale=locale)
    for file_label, data in files:
        result.files_scanned += 1
        if not forbidden:
            continue
        for key, value in iter_content_strings(data):
            result.strings_scanned += 1
            result.findings.extend(
                lint_value(forbidden, exceptions, file_label, key, value)
            )
    return result


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _load_resolved(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise _Usage(f"resolved model not found: {path}") from exc
    except (json.JSONDecodeError, OSError) as exc:
        raise _Usage(f"resolved model is not readable JSON: {path}: {exc}") from exc


class _Usage(Exception):
    """A usage/config error -> exit 2."""


def _check_register_modes(register: dict[str, Any] | None) -> None:
    """Fail as a config error (exit 2), not a traceback, when a forbidden token
    carries an unknown `context`. find_spans would raise ValueError mid-scan on
    a stale/hand-built .resolved file; surface it inside the documented contract
    instead, before scanning."""
    forbidden, _ = _normalize_register(register)
    for ft in forbidden:
        mode = ft.get("context", "any")
        if mode not in VALID_MODES:
            raise _Usage(
                f"forbidden token {ft.get('token', '')!r} has unknown context "
                f"{mode!r}; valid: {sorted(VALID_MODES)}"
            )


def _gh_escape_data(s: str) -> str:
    """Escape a GitHub workflow-command message body (% and line breaks).
    `%` must go first so the inserted escapes are not re-escaped."""
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _gh_escape_prop(s: str) -> str:
    """Escape a GitHub workflow-command property value (e.g. `file=`); these
    additionally reserve ':' and ','."""
    return _gh_escape_data(s).replace(":", "%3A").replace(",", "%2C")


def _expand_globs(root: Path, globs: list[str]) -> list[Path]:
    out: list[Path] = []
    for pattern in globs:
        out.extend(sorted(root.glob(pattern)))
    # De-dup while preserving order (overlapping globs are a CI footgun).
    seen: set[Path] = set()
    deduped: list[Path] = []
    for p in out:
        if p not in seen and p.is_file():
            seen.add(p)
            deduped.append(p)
    return deduped


def _emit_text(result: ContentLintResult, github: bool) -> None:
    for f in result.findings:
        line = (
            f"{f.file}: {f.key}: forbidden token {f.token!r} ({f.context}) "
            f"— {f.snippet}"
        )
        if github:
            print(
                f"::error file={_gh_escape_prop(f.file)}::"
                f"{_gh_escape_data(f'{result.locale}: {line}')}"
            )
        else:
            print(line)
    status = "OK" if result.ok else "FAIL"
    summary = (
        f"{status}: {result.locale} — {len(result.findings)} hit(s) across "
        f"{result.files_scanned} file(s), {result.strings_scanned} string(s) scanned"
    )
    print(summary, file=sys.stderr if not result.ok else sys.stdout)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="lint_content.py",
        description="Lint consumer content against a locale's resolved register.",
    )
    parser.add_argument(
        "--resolved",
        required=True,
        help="Path to the derived .resolved/<locale>.json whose `register` block "
        "supplies forbidden_tokens + exceptions.",
    )
    parser.add_argument(
        "--locale",
        default=None,
        help="Locale label for output (default: inferred from --resolved filename "
        "or the model's _meta.locale).",
    )
    parser.add_argument(
        "--content-root",
        default=".",
        help="Directory the content globs are resolved against (default: cwd).",
    )
    parser.add_argument(
        "globs",
        nargs="+",
        help="One or more globs of content JSON to scan, relative to "
        "--content-root (e.g. 'locales/content/cs/*.json').",
    )
    parser.add_argument(
        "--format",
        choices=("text", "github"),
        default="text",
        help="text (default) or github (::error:: annotations).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the structured result as JSON to stdout instead of text.",
    )
    args = parser.parse_args(argv)

    try:
        resolved_path = Path(args.resolved)
        resolved = _load_resolved(resolved_path)
        register = register_from_resolved(resolved)
        _check_register_modes(register)
        locale = (
            args.locale or resolved.get("_meta", {}).get("locale") or resolved_path.stem
        )

        files = _expand_globs(Path(args.content_root), args.globs)
        if not files:
            print(
                f"error: no files matched: {args.globs} (under {args.content_root})",
                file=sys.stderr,
            )
            print(
                "  (a CI gate that scans nothing silently is worse than no gate; "
                "check the path)",
                file=sys.stderr,
            )
            return 3

        parsed: list[tuple[str, Any]] = []
        for p in files:
            try:
                parsed.append((str(p), json.loads(p.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, OSError) as exc:
                raise _Usage(f"content file is not readable JSON: {p}: {exc}") from exc

        result = lint_content(locale, register, parsed)
    except _Usage as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        _emit_text(result, github=args.format == "github")

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
