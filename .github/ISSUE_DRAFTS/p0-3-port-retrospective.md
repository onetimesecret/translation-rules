## Title
P0-3 — Port 2026-04-12 retrospective into new `retrospectives/` format

## Labels
`phase-0`, `translation-rules`, `retrospective`

---

## Context

The existing `reviews/2026-04-12/` directory contains extensive incident content (README, criteria, qa-validation, guide-repair-report, cross-locale-audit, locale-quality-analysis-de_AT, proposed-new-structure, addendum, advice-for-saas-translator-skill). It is the raw material. The new format specified in `SPEC.md` §3 requires structured YAML frontmatter so retrospectives are machine-readable and participate in the lifecycle gate.

The existing `reviews/` directory remains as-is (raw input, preserved for reference per `SPEC.md` §3). The port produces a new file in `retrospectives/` that cross-references the raw review.

## Acceptance criteria

- [ ] `retrospectives/README.md` exists with the frontmatter template and status lifecycle documentation (`pending | applied | declined | superseded`)
- [ ] `retrospectives/2026-04-12-de_AT-register-flip.md` exists with valid YAML frontmatter:
  - `id: 2026-04-12-de_AT-register-flip`
  - `date: 2026-04-12`
  - `status: applied`
  - `triggered_by: { commits: [b08e59838, 4982d4f84, 44b3c3352], incident: "de_AT formal→informal register flip" }`
  - `affected_locales: [de_AT]` (primary); note secondary spread in prose
  - `affected_rules: [register.de_AT.formality]`
  - `examples_added: []` (Phase 0 doesn't add glossary examples; add in P1-5)
  - `baseline_pins: [baselines.de_AT]` (Phase 0 forward-reference; populated in P1-5)
  - `resolved_in_commit: <PR merge SHA>` (populated on merge)
- [ ] Prose body summarizes the incident, the root cause (change-log promoted to guidance), and the four-locale contamination; full detail remains in `reviews/2026-04-12/` and is linked, not duplicated. Sibling retros for pt_PT/uk/hu are **not** in Phase 0 scope — they require per-locale content work (deferred to knowledge-base phase; see `BACKLOG.md`). The de_AT retro's prose body may mention the other three as "also contaminated, per `reviews/2026-04-12/cross-locale-audit.md`" but does not create file-level records for them.

## ID format

Mixed-mode per `SPEC.md` §2.2 and §4: rule refs use dotted path (`register.de_AT.formality`); retro id is the date-slug filename (`2026-04-12-de_AT-register-flip`); glossary terms and examples use the UUID suffix scheme (`<kind>.<key>#<8char>`) starting in P1-5. Phase 0 doesn't introduce terms/examples.

## Dependencies

- None. This is Phase 0 and unblocks P0-4.

## Out of scope

- Full schema validation of the frontmatter (P1-1 provides the schema).
- CI enforcement of retrospective lifecycle (P1 scope).
- Back-porting `reviews/2025-11-14/` and `reviews/2025-11-16/` into retrospective format — `SPEC.md` §3 is explicit: existing reviews stay as-is, no backfill.

## Estimated effort

≤ 2 hours including sibling stubs.
