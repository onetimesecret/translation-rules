"""Emit `for-translators/<locale>.md`. SPEC.md §2.3 step 7a.

A pure projection of the assembled model into human-readable reference. Under
the no-vendor model (ADR-005/ADR-007) the guide is derived on demand and never
committed; the byte-hash lock is retired, and its guarantee (no hand-edited
governance) is preserved by regenerating from scratch at the pin in CI. The
only variable is the `@<sha>` source-commit pin in the header (injected by the
caller); there is no `generated_at`, so a pinned sha yields a fully
reproducible file.

The header is the SPEC §2.3 literal — do not paraphrase it; it is what marks
the file as generated and uncitable as a rule source.
"""

from __future__ import annotations

from typing import Any

HEADER = "# GENERATED from translation-rules@{sha} — do not edit, do not cite as source"


def _section(lines: list[str], title: str) -> None:
    lines.append("")
    lines.append(f"## {title}")
    lines.append("")


def emit_markdown(model: dict[str, Any], source_commit: str) -> str:
    meta = model.get("_meta", {})
    locale = meta.get("locale", "?")
    lines: list[str] = [HEADER.format(sha=source_commit), ""]
    lines.append(f"Locale: `{locale}` · schema v{meta.get('schema_version', '?')}")

    register = model.get("register")
    if register:
        _section(lines, "Register")
        lines.append(f"- Form: **{register.get('form')}**")
        lines.append(f"- Pronoun: `{register.get('pronoun')}`")
        if register.get("possessive"):
            lines.append(
                f"- Possessive: {', '.join(f'`{p}`' for p in register['possessive'])}"
            )
        forbidden = register.get("forbidden_tokens") or []
        if forbidden:
            lines.append("- Forbidden tokens:")
            for ft in forbidden:
                note = f" — {ft['note']}" if ft.get("note") else ""
                lines.append(
                    f"  - `{ft.get('token')}` ({ft.get('context')}, {ft.get('severity')}){note}"
                )
        exceptions = register.get("exceptions") or []
        if exceptions:
            lines.append("- Exceptions:")
            for exc in exceptions:
                lines.append(f"  - `{exc.get('token')}` — {exc.get('reason')}")

    glossary = model.get("glossary") or {}
    if glossary:
        _section(lines, "Glossary")
        for key in sorted(glossary):
            term = glossary[key]
            en = f" (en: {term['en']})" if term.get("en") else ""
            lines.append(f"### {key}{en}")
            senses = term.get("senses") or {}
            for sense in sorted(senses):
                body = senses[sense]
                lines.append(f"- _{sense}_: **{body.get('target')}**")
            for ex in term.get("examples") or []:
                verdict = ex.get("verdict")
                mark = {"good": "✓", "bad": "✗", "borderline": "~"}.get(verdict, "?")
                lines.append(f"  - {mark} {ex.get('source')} → {ex.get('target')}")

    rules = model.get("rules") or []
    if rules:
        _section(lines, "Rules (binding)")
        for r in rules:
            lines.append(
                f"- **{r.get('modality')}** ({r.get('severity')}): {r.get('statement')} `[{r.get('id')}]`"
            )

    context = model.get("context") or []
    if context:
        _section(lines, "Context (non-binding)")
        for c in context:
            lines.append(f"- {c}")

    anti = model.get("anti_patterns_ref") or []
    if anti:
        _section(lines, "Anti-patterns")
        for ap in anti:
            lines.append(f"- {ap.get('statement')} `[{ap.get('id')}]`")

    declined = model.get("declined_index") or []
    if declined:
        _section(lines, "Declined decisions (active guardrails)")
        for d in declined:
            lines.append(f"- `{d.get('id')}`: {d.get('declined_reason')}")
            if d.get("would_change_decision_if"):
                lines.append(f"  - would change if: {d['would_change_decision_if']}")

    return "\n".join(lines) + "\n"
