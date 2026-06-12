"""Lint a resolved model. SPEC.md §2.3 step 6.

Five assertions, all on the assembled model (resolver/model.py):

  1. forbidden-token absence — no register `forbidden_tokens` entry appears in a
     `good` example's target, unless covered by an `exceptions` allowlist entry.
  2. example/sense-target presence — every `good` example's target contains at
     least one of its term's sense targets (word_prefix, Gap A 2026-05-29).
  3. example register lint — same forbidden-token rule, framed per SPEC §2.3
     "examples must pass their own register lint" (folded into check 1; a good
     example carrying a forbidden token fails both).
  4. forbidden-token absence in embedded docs — SPEC §2.3 step 6 "Forbidden
     tokens must be absent from embedded docs". Mention-vs-use policy: rationale
     docs legitimately *mention* forbidden tokens when describing rules ("never
     use `du`"), so an occurrence inside an inline code span (backticks) or a
     fenced code block is an allowed mention; only bare-prose occurrences are
     violations. Code spans/fences are blanked with same-length whitespace
     before scanning, so finding line numbers index the original doc. The
     register `exceptions` allowlist applies as in check 1.
  5. rationale-doc presence — every `rationale_index` path must exist (i.e. be
     present in the supplied docs mapping). Dangling refs are hard errors per
     SPEC §2.2; resolver ref-walking covers dotted/uuid/retro ids only, so
     `docs:` paths are enforced here.

Only `good` examples are content-checked. `bad`/`borderline` examples
legitimately carry wrong forms (forbidden tokens, missing sense targets) — that
is their pedagogical point — so linting them would invert the signal.

Doc content arrives as data (`docs` mapping, repo-root-relative path → text),
loaded by the caller (resolver.resolve.load_lint_docs) — lint_model stays pure.
Checks 4-5 run only when a `docs` mapping is supplied.

Output is structured (clear pass/fail) so an agent knows when a locale
conversion is done — SPEC §6.2. `ok` is false iff any error-severity finding
exists; warning/info findings are reported but non-fatal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from resolver.matching import DEFAULT_TARGET_MODE, _casefold, find_spans

FATAL = {"error"}


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    term: str | None = None
    example_id: str | None = None
    token: str | None = None
    doc: str | None = None
    line: int | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "check": self.check,
            "severity": self.severity,
            "message": self.message,
        }
        if self.term is not None:
            out["term"] = self.term
        if self.example_id is not None:
            out["example_id"] = self.example_id
        if self.token is not None:
            out["token"] = self.token
        if self.doc is not None:
            out["doc"] = self.doc
        if self.line is not None:
            out["line"] = self.line
        return out


@dataclass
class LintResult:
    locale: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(f.severity in FATAL for f in self.findings)

    def as_dict(self) -> dict[str, Any]:
        return {
            "locale": self.locale,
            "ok": self.ok,
            "findings": [f.as_dict() for f in self.findings],
        }


def _exception_spans(
    target: str, exceptions: list[dict[str, Any]]
) -> list[tuple[int, int]]:
    """All occurrence spans of every allowlisted exception token in `target`
    (casefolded space, matching find_spans)."""
    spans: list[tuple[int, int]] = []
    for exc in exceptions:
        etok = exc.get("token", "")
        spans.extend(find_spans(target, etok, "substring"))
    return spans


def _hit_allowed(hit: tuple[int, int], exception_spans: list[tuple[int, int]]) -> bool:
    """True iff this forbidden-token hit falls *inside* an allowlisted exception
    occurrence (e.g. the 'du' span inside a 'Duden' span). A standalone 'du'
    elsewhere in the same target is not covered just because 'Duden' appears."""
    hs, he = hit
    return any(es <= hs and he <= ee for es, ee in exception_spans)


_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def _blank_code(text: str) -> str:
    """Copy of `text` with fenced code blocks (``` delimited, fences included)
    and inline code spans replaced by same-length whitespace. Every newline is
    kept, so spans and line numbers computed on the result index the original
    doc. Token occurrences inside code are mentions, not uses (docstring #4)."""
    out: list[str] = []
    fenced = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append(" " * len(line))
        elif fenced:
            out.append(" " * len(line))
        else:
            out.append(_INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


def _lint_docs(
    result: LintResult,
    docs: dict[str, str],
    rationale_index: dict[str, list[str]],
    forbidden: list[dict[str, Any]],
    exceptions: list[dict[str, Any]],
) -> None:
    """Checks 4 + 5: bare-prose forbidden tokens in docs; dangling doc paths."""
    for path in sorted(docs):
        prose = _blank_code(docs[path])
        # find_spans offsets index the casefolded text; count newlines there
        # (casefolding never adds/removes them) so `line` stays exact even
        # when casefolding changes string length (e.g. ß -> ss).
        folded = _casefold(prose)
        exc_spans = _exception_spans(prose, exceptions)
        for ft in forbidden:
            tok = ft.get("token", "")
            mode = ft.get("context", "any")
            for hit in find_spans(prose, tok, mode):
                if _hit_allowed(hit, exc_spans):
                    continue
                result.findings.append(
                    Finding(
                        check="forbidden_token_docs",
                        severity=ft.get("severity", "error"),
                        message=(
                            f"embedded doc contains forbidden token {tok!r} "
                            f"in bare prose"
                        ),
                        token=tok,
                        doc=path,
                        line=folded[: hit[0]].count("\n") + 1,
                    )
                )

    for rule_id, paths in sorted(rationale_index.items()):
        for path in paths:
            if path not in docs:
                result.findings.append(
                    Finding(
                        check="rationale_doc_missing",
                        severity="error",
                        message=(
                            f"rule {rule_id!r} references embedded doc "
                            f"{path!r} which does not exist"
                        ),
                        doc=path,
                    )
                )


def lint_model(model: dict[str, Any], docs: dict[str, str] | None = None) -> LintResult:
    locale = model.get("_meta", {}).get("locale", "?")
    result = LintResult(locale=locale)
    register = model.get("register") or {}
    forbidden = register.get("forbidden_tokens") or []
    exceptions = register.get("exceptions") or []
    glossary = model.get("glossary") or {}

    for term_key, term in glossary.items():
        senses = term.get("senses") or {}
        for ex in term.get("examples") or []:
            if ex.get("verdict") != "good":
                continue
            target = ex.get("target", "")
            ex_id = ex.get("id")

            # Check 1/3: forbidden tokens must be absent from good examples.
            # A hit is suppressed only when it falls inside an allowlisted
            # exception occurrence — not whenever the exception merely appears.
            exc_spans = _exception_spans(target, exceptions)
            for ft in forbidden:
                tok = ft.get("token", "")
                mode = ft.get("context", "any")
                hits = find_spans(target, tok, mode)
                if hits and any(not _hit_allowed(h, exc_spans) for h in hits):
                    result.findings.append(
                        Finding(
                            check="forbidden_token",
                            severity=ft.get("severity", "error"),
                            message=f"good example contains forbidden token {tok!r}",
                            term=term_key,
                            example_id=ex_id,
                            token=tok,
                        )
                    )

            # Check 2: good example must demonstrate at least one sense target.
            if senses and not ex.get("senses"):
                targets = sorted(b.get("target", "") for b in senses.values())
                result.findings.append(
                    Finding(
                        check="sense_target_presence",
                        severity="error",
                        message=(
                            f"good example does not contain any sense target "
                            f"(expected one of {targets}, mode={DEFAULT_TARGET_MODE})"
                        ),
                        term=term_key,
                        example_id=ex_id,
                    )
                )

    # Checks 4 + 5: embedded docs. Skipped when the caller supplies no docs
    # mapping (content arrives as data so lint_model stays pure).
    if docs is not None:
        _lint_docs(
            result, docs, model.get("rationale_index") or {}, forbidden, exceptions
        )

    return result
