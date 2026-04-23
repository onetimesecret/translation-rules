## Title
P1-4b — App repo submodule + cross-repo CI gate (human-only)

## Labels
`phase-1`, `translation-rules`, `ci`, `cross-repo`, `human-only`

---

## Context

Companion ticket to P1-4a. The cross-repo PR in `onetimesecret/onetimesecret` that lands the submodule, wires the resolver into app repo CI, and enables the pipeline gate blocking locale content PRs against stale submodule pointers.

**This ticket is `human-only`.** `/d:work-tasks-db` agents cannot claim it — the work spans a repository they don't have authorship context for, and requires coordination with the app repo maintainer. The agent-claimable portion is P1-4a.

## Acceptance criteria (all in `onetimesecret/onetimesecret`)

- [ ] `locales/translation-rules/` submodule added pointing at this repo's `main`
- [ ] `locales/scripts/resolve-guides.sh` (or equivalent) invokes the resolver; runs in CI on every PR
- [ ] Generated artifacts committed at `locales/guides/for-translators/<locale>.md` and `locales/.resolved/<locale>.json` (per `SPEC.md` §2.3 commit policy)
- [ ] CI check: submodule pointer freshness on locale-content PRs (PRs touching `locales/content/<locale>/*.json` must have submodule current)
- [ ] CI check: `.resolved/<locale>.json`'s `_meta.source_commit` equals submodule SHA
- [ ] CI check: `forbidden_tokens` grep against `locales/content/<locale>/*.json` — this is the mechanical prevention of the original incident class
- [ ] CI check: `for-translators/*.md` hash matches resolver output — hand edits rejected

## Dependencies

- Blocked by P1-4a (needs this repo's CI contracts established)
- Blocks P1-5b (de_AT integration test against app repo)

## Out of scope

- Migrating the existing 35 `local-guides/for-translators/*.md` files in this repo to the new generated location — Phase 2 per locale
- Retrospective lifecycle CI enforcement (7-day pending timeout) in app repo context — belongs in this repo only (P1-4a)

## Estimated effort

4–8 hours, plus app repo maintainer review cycle.
