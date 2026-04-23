## Title
P1-4a — Resolver CI in `translation-rules` repo

## Labels
`phase-1`, `translation-rules`, `ci`

---

## Context

This repo's own CI must validate rule files and resolver correctness on every PR. This ticket is the `translation-rules` half of the full integration (`SPEC.md` §2.4). The app repo half is P1-4b (human-only, tracked separately).

## Acceptance criteria

- [ ] `.github/workflows/validate.yml` runs on every PR:
  - Schema validation against all `*.yaml` files using the P1-1 schemas
  - Resolver unit tests from P1-2/P1-3
  - `bin/lint-register` against embedded examples and docs
  - Retrospective lifecycle checks: `status: pending` older than 7 days fails; `status: applied` without `resolved_in_commit` fails; all `affected_rules` ids resolve
  - `_archive/` firewall: any PR that moves a file out of `_archive/` requires an approving `prescriptive-promotion` label (enforced via CODEOWNERS or a label-check action)
- [ ] `.github/workflows/publish.yml` tags `main` on merge (allows the app repo to pin against a named release if needed)
- [ ] `README.md` documents the submodule-consumer contract for the app repo side

## Dependencies

- Blocked by P1-3 (needs working resolver + emit)
- Blocks P1-4b (app repo PR consumes tags/contracts this ticket establishes)

## Agent-claimable

Yes. All work is within this repo.

## Out of scope

- Any commit to `onetimesecret/onetimesecret` (P1-4b)
- Retrospective pruning (deferred; see `SPEC.md` §8)

## Estimated effort

4–6 hours.
