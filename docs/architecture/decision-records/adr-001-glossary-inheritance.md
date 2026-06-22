---
id: 001
status: accepted
title: ADR-001: Glossary inheritance along the rules chain
---

## Status
Accepted

## Date
2026-06-22

## Context
The resolver merges `rules.yaml` along the inheritance chain (e.g. `fr_CA → fr → base`) but, until this ADR, treated `glossary.yaml` as a per-locale leaf file: load + validate, never merge. Register followed the same per-locale-leaf pattern.

That was incidental, not designed. Greptile #29-1 surfaced it: `locales/fr_CA/glossary.yaml` was authored delta-only (just the `courriel` override of `email`), expecting the rest of fr's terminology — `mot de passe`, `phrase secrète`, `brûler`, `lien`, `chiffré` — to flow through. The emitted `.resolved/fr_CA.json` instead contained only the two terms fr_CA had restated locally, while inherited `rule_ref`s still pointed at the missing terms. Translators or downstream consumers reading the resolved artifact would see incomplete terminology guidance with refs that look fine but resolve to nothing in the local view.

The pre-fix workaround was to restate every parent term in each child glossary. That scales badly: ~30 regional variants are on the back-port roadmap (fr_FR, fr_BE, fr_CH; de_DE, de_CH; es_ES, es_MX, es_AR, ...). Each restate is a place the terms can silently drift from the parent.

## Decision
**Glossaries merge along the same inheritance chain as rules, with term-`key` override.** A child term replaces the parent term of the same `key` wholesale; terms the child omits are inherited unchanged. The merged glossary keeps the child's `id` and `source` (downstream consumers attribute the artifact to the locale being resolved), with the union of all chain terms under `terms:`.

**Register stays self-contained (per-locale).** Registers are short, locale-defining, and carry forbidden-token lists tuned to that locale's morphology (e.g. fr blocks `t'` / `t’` elisions specifically — meaningless for de). Merging would create false sharing and would not avoid meaningful duplication.

Why term-`key` and not term-`id`: the `key` is the human-readable grep target ("email", "passphrase"); the `id` is uuid-suffixed and survives renames. Inheritance is over what the term *means*, not over which file declared it. fr_CA's `term.email_ca#287480a5` overriding fr's `term.email#8c4fb076` is correct — both have `key: email`.

Why wholesale term replacement and not sense-level merge: the term is the smallest unit of cross-locale meaning. A child that overrides one sense almost certainly wants its own examples and `rule_ref`s for the others too; partial-sense merges would be an attractive nuisance.

## Trade-offs
- **We lose**: A locale can no longer silently keep a term-name in sync with its parent by restating it. If a parent renames a term's `key`, the child either inherits the new key or has to update.
- **We gain**: Delta-only child glossaries scale linearly with the number of locale-specific differences, not with the total terminology surface. The fr_CA glossary drops from 2 terms to 1.

## Consequences
### Positive
- The ~30 regional variants on the back-port roadmap can be authored as deltas without restating their parent's terminology.
- Inherited `rule_ref`s in the merged glossary are validated against the same combined index as the locale's own refs, so a missing parent rule fails fast at resolve time.

### Negative
- Renaming a term's `key` in a parent locale is a chain-wide change: any child that intended to override the old key inherits the new one instead. Mitigated by lint at resolve time (the override never silently disappears — it just stops being an override) and by the rules-vs-glossary split: a rename is unusual.

### Neutral
- Register and rules continue to use different mechanisms (per-locale leaf vs. chain-merge); the asymmetry is now documented rather than incidental.
- Term `id` collisions across parent and child are harmless: the term-merge dedups by `key`, and `IdIndex.add` only errors on same-id/different-`(kind, key)` records, which a deterministic id minted from a stable `(kind, key)` cannot produce.

## Implementation Notes

### Resolver wiring (2026-06-22)
`resolver/merge.py` adds `merge_glossary_terms(glossaries_child_first)`, called from `resolver/resolve.py:resolve_locale` after the rules chain is built. The function walks the chain child-first (locale leaf, then each ancestor's `glossary.yaml` if present, skipping `base`), dedups by `key`, and emits a glossary headed by the child's `id` / `source`. `_check_refs` validates the merged glossary instead of the leaf so inherited terms' refs are checked. The returned `result["glossary"]` is the merged view; `build_model` continues to consume it unchanged.

No glossary indexing change was needed: `_check_refs` validates `*_ref` fields, not `id` definitions. Inherited terms' `rule_ref`s already point at rules in the chain (which are indexed via `_index_dotted_ids_in_rules` over `chain_nodes`).

### Known limitation: inherited term/example ids are not in the uuid index (2026-06-22)
`_index_glossary` runs only on the locale's own (leaf) glossary, so a parent term's `id` and its examples' `id`s do not enter the combined uuid index. This is invisible today because the only uuid-shaped reference field is `examples_added` (used by retrospectives) and no current YAML references an inherited example. A future retro that did `examples_added: [<an inherited example id>]` would dangle even though the example is present in the merged glossary view. The fix, if that case arises, is to also call `_index_glossary` on each ancestor glossary during the chain walk; deferred until there is a consumer, to keep this change contained. (Duplicate term `id`s across parent/child are harmless either way — they share `(kind, key)`, which `IdIndex.add` permits.)

Fixture coverage: `tests/resolver/fixtures/de-de_AT/locales/de/glossary.yaml` introduces a parent-only `link` term (inherited) plus a duplicate-key `secret_object` (overridden by de_AT), so the de-de_AT golden exercises both cases.
