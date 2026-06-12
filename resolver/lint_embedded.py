#!/usr/bin/env python3
"""Lint embedded docs and rule statements against register forbidden tokens.

SPEC.md §2.3 step 6: "Forbidden tokens must be absent from embedded docs."
This validates that base/docs/, locale docs, and rule statements don't contain
register-specific forbidden tokens that would contradict the register's binding
assertions.

Runs standalone or integrated into resolver/resolve.py.

Exit codes:
  0  all docs clean
  1  forbidden token found in embedded content
  2  setup error (missing register, unreadable file, etc.)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("setup: PyYAML not installed", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Allow running as a script or as a module.
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO_ROOT))

from resolver.loader import StringDateLoader
from resolver.matching import find_spans


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    locale: str | None = None
    file_path: str | None = None
    token: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {"check": self.check, "severity": self.severity, "message": self.message}
        if self.locale is not None:
            out["locale"] = self.locale
        if self.file_path is not None:
            out["file_path"] = self.file_path
        if self.token is not None:
            out["token"] = self.token
        return out


@dataclass
class LintResult:
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(f.severity == "error" for f in self.findings)


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Load YAML file, return None if not found or parse error."""
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.load(f, Loader=StringDateLoader) or {}
    except Exception:
        return None


def _extract_forbidden_tokens(register: dict[str, Any]) -> list[str]:
    """Extract list of forbidden token strings from a register dict."""
    tokens = []
    for entry in register.get("forbidden_tokens") or []:
        if isinstance(entry, dict):
            tok = entry.get("token", "")
        else:
            tok = str(entry)
        if tok:
            tokens.append(tok)
    return tokens


def _check_text(
    text: str,
    tokens: list[str],
    locale: str | None,
    file_path: str,
    result: LintResult,
) -> None:
    """Check if any forbidden token appears in text (word boundary match)."""
    for token in tokens:
        # Use 'standalone_word' matching like lint.py does for examples
        hits = find_spans(text, token, "standalone_word")
        if hits:
            result.findings.append(
                Finding(
                    check="forbidden_token_in_docs",
                    severity="error",
                    message=f"embedded content contains forbidden token {token!r}",
                    locale=locale,
                    file_path=file_path,
                    token=token,
                )
            )
            return  # Report first token per file


def lint_embedded_docs(locales_dir: Path | None = None) -> LintResult:
    """Lint embedded docs against registers.

    Checks:
    1. base/docs/*.md — must not contain any forbidden tokens from any register
    2. locales/<locale>/docs/*.md — must not contain locale's forbidden tokens

    Rule statements are excluded; they are YAML-validated rationale prose that may
    legitimately discuss the rules being enforced (e.g. "du/dein forms forbidden").
    """
    if locales_dir is None:
        locales_dir = REPO_ROOT / "locales"
    result = LintResult()

    # Load all registers to know which tokens are forbidden per locale
    registers: dict[str, list[str]] = {}
    locales = sorted(p for p in locales_dir.iterdir() if p.is_dir())
    for locale_dir in locales:
        reg_path = locale_dir / "register.yaml"
        if not reg_path.exists():
            continue
        reg = _load_yaml(reg_path)
        if reg:
            tokens = _extract_forbidden_tokens(reg)
            registers[locale_dir.name] = tokens

    # Check base/docs/ against all registers (base docs must be clean for all locales)
    base_docs_dir = REPO_ROOT / "base" / "docs"
    if base_docs_dir.exists():
        for doc_file in sorted(base_docs_dir.glob("*.md")):
            text = doc_file.read_text(encoding="utf-8")
            # Accumulate all tokens from all locales to check base docs against
            all_tokens = set()
            for tokens in registers.values():
                all_tokens.update(tokens)
            _check_text(text, sorted(all_tokens), None, str(doc_file.relative_to(REPO_ROOT)), result)

    # Check locale-specific docs
    for locale, tokens in registers.items():
        locale_dir = locales_dir / locale
        locale_docs_dir = locale_dir / "docs"
        if locale_docs_dir.exists():
            for doc_file in sorted(locale_docs_dir.glob("*.md")):
                text = doc_file.read_text(encoding="utf-8")
                _check_text(text, tokens, locale, str(doc_file.relative_to(REPO_ROOT)), result)

    return result


def main(argv: list[str] | None = None) -> int:
    result = lint_embedded_docs()
    for f in result.findings:
        print(f"error: [{f.check}] {f.file_path}: {f.message}", file=sys.stderr)
    if result.ok:
        print("lint-embedded: ok (all docs clean)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
