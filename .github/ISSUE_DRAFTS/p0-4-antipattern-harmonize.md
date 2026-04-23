## Title
P0-4 — Anti-pattern in UX guide: "harmonize = keys only"

## Labels
`phase-0`, `translation-rules`, `anti-pattern`

---

## Context

`reviews/2026-04-12/cross-locale-audit.md` and `advice-for-saas-translator-skill.md` both identify "harmonize" vs "rewrite" task-framing as a root failure mode: agents labeled with a harmonization task ended up rewriting text, which is where the register flips happened.

Phase 0 cannot implement the full anti-patterns subsystem. But a single prose rule added to the existing UX guide costs nothing and addresses the task-framing error directly.

## Acceptance criteria

- [ ] `local-guides/UX-TRANSLATION-GUIDE.md` gains a new section (approximately half a page) titled "Anti-pattern: harmonize vs rewrite"
- [ ] Section states:
  - Harmonization touches key structures, variable placeholders, and formatting only
  - Harmonization never changes register, tone, terminology, or rewrites text field values
  - A task labeled "harmonize" that appears to require text rewrites is mislabeled — stop and escalate
- [ ] Section cites the 2026-04-12 incident as motivation with a link to `retrospectives/2026-04-12-de_AT-register-flip.md`
- [ ] No other sections of the UX guide are modified (keeps diff reviewable)

## Dependencies

- Blocked by P0-3 (retrospective must exist for citation)

## Out of scope

- Full `anti_patterns.yaml` schema and mechanical enforcement (`SPEC.md` §3 Phase 1+).
- CI check that detects harmonize-labeled PRs touching register tokens (Phase 1).

## Estimated effort

≤ 30 minutes.

## Note

This is interim. Phase 1's resolver-emitted output will absorb this into a structured `anti_patterns` section consumed by translator agents at spawn time. The prose in the UX guide is the stopgap for human readers and for the `saas-translator` skill until the resolver is live.
