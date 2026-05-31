"""Lint a resolved model. SPEC.md §2.3 step 6.

Three assertions, all on the assembled model (resolver/model.py):

  1. forbidden-token absence — no register `forbidden_tokens` entry appears in a
     `good` example's target, unless covered by an `exceptions` allowlist entry.
  2. example/sense-target presence — every `good` example's target contains at
     least one of its term's sense targets (word_prefix, Gap A 2026-05-29).
  3. example register lint — same forbidden-token rule, framed per SPEC §2.3
     "examples must pass their own register lint" (folded into check 1; a good
     example carrying a forbidden token fails both).

Only `good` examples are content-checked. `bad`/`borderline` examples
legitimately carry wrong forms (forbidden tokens, missing sense targets) — that
is their pedagogical point — so linting them would invert the signal.

Output is structured (clear pass/fail) so an agent knows when a locale
conversion is done — SPEC §6.2. `ok` is false iff any error-severity finding
exists; warning/info findings are reported but non-fatal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from resolver.matching import DEFAULT_TARGET_MODE, find_spans

FATAL = {"error"}


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    term: str | None = None
    example_id: str | None = None
    token: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {"check": self.check, "severity": self.severity, "message": self.message}
        if self.term is not None:
            out["term"] = self.term
        if self.example_id is not None:
            out["example_id"] = self.example_id
        if self.token is not None:
            out["token"] = self.token
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


def lint_model(model: dict[str, Any]) -> LintResult:
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

    return result
