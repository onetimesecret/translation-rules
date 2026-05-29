# Backlog — deferred quality & content issues

Append-only log. Foundational/structural work (SPEC.md, tickets, resolver, schemas, CI) is separate from knowledge-base population (forbidden token lists, glossary terms, worked examples, baseline pins, register conventions per locale).

This file captures quality/content items surfaced during foundational work that we explicitly defer until the system has enough structure to capture them in an organized manner. Do not modify past entries. Add new entries at the bottom.

Format per entry:

```
## YYYY-MM-DD — <short slug>
- Surfaced in: <ticket/PR/file>
- Type: content | quality | provenance | schema-extension | other
- Defer until: <phase or condition>
- Detail: <1–3 sentences>
```

---

## 2026-04-23 — pt_PT/uk/hu forbidden-token lists unverified
- Surfaced in: P0-1 draft (dropped from Phase 0 scope)
- Type: content
- Defer until: knowledge-base population phase, after foundational work stabilizes
- Detail: Initial P0-1 draft listed forbidden tokens for pt_PT (`tu, teu, tua, teus, tuas`), uk (`ти, твій, твоя, твоє, твої, тебе, тобі`), and hu (`te, ti, téged, neked, tiéd`). These were drafted from language knowledge, not cited from `reviews/2026-04-12/cross-locale-audit.md` or native-speaker review. Dropped from Phase 0 to keep foundational work scoped to de_AT (the incident locale, grounded in SPEC §1). Revisit during knowledge-base population; each locale needs audit-backed or native-speaker-confirmed token sets with a populated `source:` field.

## 2026-04-23 — register `source:` field needed on every token set
- Surfaced in: P0-1 review discussion
- Type: provenance / schema-extension
- Defer until: P1-1 schema design
- Detail: Every `forbidden_tokens` entry (or the register file as a whole) should carry a `source:` field — e.g., `SPEC.md §1`, `reviews/2026-04-12/cross-locale-audit.md`, `native-speaker:<initials>`, or `null`. "Obvious now" rots fast; provenance survives the rot. Applies to de_AT too even though its current source is SPEC-verbatim.

## 2026-04-26 — de_AT informal-plural-possessive paradigm coverage gap
- Surfaced in: P0-1 implementation
- Type: content
- Defer until: knowledge-base population phase, after P1-1 schema lands
- Detail: The Phase 0 forbidden-token list for de_AT (per `SPEC.md` §1) carries `euch` and `euer` but not the inflected possessive paradigm `eure / euren / eurem / eurer / eures`. The asymmetry is inherited verbatim from the SPEC; the `dein` paradigm gets all 5 forms enumerated, the `euer` paradigm only gets the citation form. A single `\beur` word_prefix entry would close the gap, but mixing prefix-matching with the explicit-enumeration scheme requires the P1-1 schema to settle context semantics first. Revisit during knowledge-base population with native-speaker confirmation. Native-speaker priority note (2026-04-26): `eure` is the highest-frequency missing form in UI strings (catches `eure E-Mail`, `eure Anmeldedaten`); `euren` is second.
