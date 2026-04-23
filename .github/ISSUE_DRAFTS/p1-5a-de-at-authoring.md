## Title
P1-5a — de_AT authoring + local resolver green

## Labels
`phase-1`, `translation-rules`, `de_AT`, `milestone`

---

## Context

This is the proof that the Phase 1 authoring side works end-to-end in isolation (no app repo dependency). P1-5b lands the app repo integration.

de_AT is the right first-through-full-pipeline locale: it's the incident locale, it has a baseline commit per `reviews/2026-04-12/cross-locale-audit.md`, and the retrospective is already drafted.

## Acceptance criteria

- [ ] `base.yaml` authored by absorbing mechanical rules from `local-guides/UX-TRANSLATION-GUIDE.md` and `local-guides/SECURITY-TRANSLATION-GUIDE.md`; rationale prose moved to `base/docs/`
- [ ] `locales/de/rules.yaml` exists as inheritance parent (minimal — just what de_AT needs to inherit)
- [ ] `locales/de_AT/rules.yaml` exists with `inherits: de` and de_AT-specific overrides
- [ ] `locales/de_AT/register.yaml` exists (authored in P0-1; updated to schema-conformance from P1-1)
- [ ] `locales/de_AT/glossary.yaml` exists with:
  - `secret_object` → `Geheimnis` with disambiguation heuristic and key patterns
  - `secret_payload` → `Nachricht` with disambiguation heuristic and key patterns
  - At least one worked example per sense, each with `rule_refs` pointing at real rule IDs
  - Term and example ids use the UUID-suffix format (`term.secret_object#<8char>`, `ex.burn#<8char>`) minted via `bin/mint-id`
- [ ] `baselines.yaml` populated for de_AT: `{ commit: f95b03f44, notes: "Last commit (2025-04-15) before de_AT contamination sequence began per 2026-04-12-cross-locale-audit", retro_id: 2026-04-12-de_AT-register-flip }`. **Note:** the commit does not itself edit de_AT files; it's a "de_AT state frozen here was acceptable" pin, not a curation commit.
- [ ] `retrospectives/2026-04-12-de_AT-register-flip.md` updated: `affected_rules` populated with real ids (register.de_AT.formality plus glossary term ids), `resolved_in_commit` set on merge
- [ ] `_archive/` created; any prose files from repair work moved in
- [ ] Resolver passes: `resolve.py de_AT --lint --emit=md,json` exits zero and produces valid outputs locally
- [ ] `resolver/index.json` regenerated and committed
- [ ] **Native-speaker gate at merge.** Agent may author; final merge requires human native-speaker sign-off on the glossary sense split and worked examples (spot-check captured in PR description). Agents open PR with `Needs-native-review` label.

## Dependencies

- Blocked by P1-3 (resolver emit must work)
- Blocked by P0-1 (register.yaml must exist)
- Blocks P1-5b (app repo integration)

## Agent-claimable

Yes, with native-speaker gate at merge.

## Out of scope

- App repo integration (P1-5b)
- de, pt_PT, uk, hu full conversions — Phase 2 follow-up

## Estimated effort

10–16 hours agent time plus ≤2 hours native-speaker review.
