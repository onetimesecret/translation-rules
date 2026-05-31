"""Assemble the resolved model. SPEC.md §2.3 steps 5 + the shape of step 7.

This is the single in-memory model that emit_json, emit_markdown, and lint are
all pure projections of. Building it once (rather than threading raw inputs
through each emitter) keeps the three outputs consistent by construction and
makes golden fixtures stable.

Folds in step 5 (attach retros): applied retrospectives stamp their id onto the
rules they touch; declined retrospectives populate `declined_index`. Both are
filtered per-locale (SPEC §3 "per-locale decline index") — a retro whose
`affected_locales` neither contains this locale nor is empty/universal does not
leak into this locale's output.

Shape note — deviation from SPEC §2.3 (deliberate, 2026-05-29). SPEC draws
`glossary.<term>.<sense>.examples`, but the glossary schema makes `examples`
TERM-level with no sense linkage, and `bad`/`borderline` examples carry *wrong*
forms that match no sense target — they have no sense to nest under. We instead
emit `<term>: {en, senses: {...}, examples: [...]}` where each example is
annotated with the senses its target matches. No downstream consumer is wired
yet (skill is out-of-repo; §6.1 is post-Phase-1), so this contract is defined
here, honestly to the schema.
"""

from __future__ import annotations

from typing import Any

from resolver.matching import DEFAULT_TARGET_MODE, contains

SCHEMA_VERSION = "1"

BINDING_MODALITIES = {"MUST", "MUST_NOT"}
LOCALE_KEY_LEN = (2, 3)  # bare language subtag length, before optional _REGION


class ModelError(Exception):
    """Raised on structural integrity failures during assembly."""


def _retro_applies_to(retro: dict[str, Any], locale: str) -> bool:
    """A retro touches this locale if its affected_locales is empty (universal)
    or explicitly lists the locale."""
    locales = retro.get("affected_locales") or []
    return not locales or locale in locales


def _check_supersede_pairing(retros: list[dict[str, Any]]) -> None:
    """SPEC §3: a superseded retro must be named in some other retro's
    `supersedes` list. The schema enforces shape per-file; the pairing is
    cross-file and therefore the resolver's job."""
    superseding: set[str] = set()
    for r in retros:
        for sid in r.get("supersedes") or []:
            superseding.add(sid)
    for r in retros:
        if r.get("status") == "superseded" and r.get("id") not in superseding:
            raise ModelError(
                f"retro {r.get('id')!r} is status=superseded but no retro's "
                f"supersedes list references it"
            )


def _locale_target(term: dict[str, Any], locale: str) -> Any:
    """Return the term's locale-keyed value (string or sense mapping), or None."""
    val = term.get(locale)
    if val is None:
        # Fall back to the bare language subtag (de for de_AT) if present.
        lang = locale.split("_", 1)[0]
        if lang != locale:
            val = term.get(lang)
    return val


def _senses_for(term: dict[str, Any], locale: str) -> dict[str, dict[str, Any]]:
    """Normalise a term's locale target into a {sense: {target, ...}} map.

    A string target is wrapped in a synthesized single sense `default` so the
    rest of the pipeline (example routing, lint) stays uniform."""
    val = _locale_target(term, locale)
    if val is None:
        return {}
    if isinstance(val, str):
        return {"default": {"target": val}}
    # Sense-split mapping: copy through target/rule_ref/rationale.
    out: dict[str, dict[str, Any]] = {}
    for sense, body in val.items():
        if not isinstance(body, dict):
            continue
        entry: dict[str, Any] = {"target": body["target"]}
        if "rule_ref" in body:
            entry["rule_ref"] = body["rule_ref"]
        if "rationale" in body:
            entry["rationale"] = body["rationale"]
        out[sense] = entry
    return out


def _matched_senses(target: str, senses: dict[str, dict[str, Any]]) -> list[str]:
    """Senses whose target term is present in `target` (word_prefix)."""
    hits = [
        sense
        for sense, body in senses.items()
        if contains(target, body["target"], DEFAULT_TARGET_MODE)
    ]
    return sorted(hits)


def _build_glossary(glossary: dict[str, Any] | None, locale: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not glossary:
        return out
    for term in glossary.get("terms") or []:
        key = term.get("key")
        if not key:
            continue
        senses = _senses_for(term, locale)
        examples: list[dict[str, Any]] = []
        for ex in term.get("examples") or []:
            target = ex.get("target", "")
            entry = {
                "id": ex.get("id"),
                "source": ex.get("source"),
                "target": target,
                "verdict": ex.get("verdict"),
                "senses": _matched_senses(target, senses),
            }
            if ex.get("note"):
                entry["note"] = ex["note"]
            if ex.get("rule_refs"):
                entry["rule_refs"] = ex["rule_refs"]
            examples.append(entry)
        term_out: dict[str, Any] = {"senses": senses}
        if term.get("en"):
            term_out["en"] = term["en"]
        if term.get("rationale"):
            term_out["rationale"] = term["rationale"]
        if examples:
            term_out["examples"] = examples
        out[key] = term_out
    return out


def _build_register(register: dict[str, Any] | None) -> dict[str, Any] | None:
    if not register:
        return None
    out: dict[str, Any] = {
        "form": register.get("form"),
        "pronoun": register.get("pronoun"),
        "forbidden_tokens": register.get("forbidden_tokens") or [],
        "exceptions": register.get("exceptions") or [],
    }
    if register.get("possessive"):
        out["possessive"] = register["possessive"]
    if register.get("rule_ref"):
        out["rule_ref"] = register["rule_ref"]
    return out


def build_model(
    *,
    locale: str,
    merged_rules: dict[str, Any],
    register: dict[str, Any] | None,
    glossary: dict[str, Any] | None,
    retros: list[dict[str, Any]],
    source_commit: str,
    generated_at: str,
    schema_version: str = SCHEMA_VERSION,
) -> dict[str, Any]:
    """Assemble the indexed resolved model for one locale (SPEC §2.3)."""
    _check_supersede_pairing(retros)

    # Per-locale, non-superseded retros split by status.
    applied = [
        r
        for r in retros
        if r.get("status") == "applied" and _retro_applies_to(r, locale)
    ]
    declined = [
        r
        for r in retros
        if r.get("status") == "declined" and _retro_applies_to(r, locale)
    ]

    # rule_id -> list of applied retro ids that touch it (step 5 fold).
    fold: dict[str, list[str]] = {}
    for r in applied:
        for rid in r.get("affected_rules") or []:
            fold.setdefault(rid, []).append(r["id"])

    rules: list[dict[str, Any]] = []
    context: list[str] = list(merged_rules.get("context") or [])
    rationale_index: dict[str, list[str]] = {}

    for item in merged_rules.get("rules") or []:
        rid = item.get("id")
        modality = item.get("modality")
        if item.get("docs"):
            rationale_index[rid] = list(item["docs"])
        if modality in BINDING_MODALITIES:
            entry: dict[str, Any] = {
                "id": rid,
                "modality": modality,
                "statement": item.get("statement"),
                "severity": item.get("severity"),
            }
            if item.get("rule_ref"):
                entry["rule_ref"] = item["rule_ref"]
            if rid in fold:
                entry["retro_refs"] = sorted(fold[rid])
            rules.append(entry)
        else:
            # Advisory (SHOULD/SHOULD_NOT/MAY) is non-binding -> context, as a
            # rendered string. Keeps the `rules` partition pure MUST/MUST_NOT,
            # which is the anti-drift cue (SPEC §2.3). ID linkage already lives
            # in resolver/index.json, so nothing is lost.
            context.append(f"[{modality}] {item.get('statement')}")

    anti_patterns_ref: list[dict[str, Any]] = []
    for ap in merged_rules.get("anti_patterns") or []:
        entry = {"id": ap.get("id"), "statement": ap.get("statement")}
        if ap.get("severity"):
            entry["severity"] = ap["severity"]
        if ap.get("rule_ref"):
            entry["rule_ref"] = ap["rule_ref"]
        anti_patterns_ref.append(entry)

    declined_index: list[dict[str, Any]] = []
    for r in sorted(declined, key=lambda x: x.get("id", "")):
        declined_index.append(
            {
                "id": r["id"],
                "affected_rules": r.get("affected_rules") or [],
                "affected_locales": r.get("affected_locales") or [],
                "declined_reason": r.get("declined_reason"),
                "would_change_decision_if": r.get("would_change_decision_if"),
            }
        )

    return {
        "_meta": {
            "locale": locale,
            "source_commit": source_commit,
            "schema_version": schema_version,
            "generated_at": generated_at,
        },
        "register": _build_register(register),
        "glossary": _build_glossary(glossary, locale),
        "rules": rules,
        "context": context,
        "rationale_index": rationale_index,
        "declined_index": declined_index,
        "anti_patterns_ref": anti_patterns_ref,
    }
