## Title
P1-5b — de_AT app repo integration green

## Labels
`phase-1`, `translation-rules`, `de_AT`, `milestone`, `cross-repo`

---

## Context

Companion to P1-5a. Proves that de_AT works end-to-end through the app repo CI gate with the new system. This is the reversibility checkpoint — after this lands, only de_AT is in the new system; 34 other locales still use the frozen `local-guides/for-translators/*.md`.

## Acceptance criteria

- [ ] App repo submodule bumped to the main commit that includes P1-5a
- [ ] Resolver regenerates `onetimesecret/locales/guides/for-translators/de_AT.md` and `.resolved/de_AT.json`; both committed in the bump PR
- [ ] App repo CI lint against current `onetimesecret/locales/content/de_AT/*.json` goes green (violations either fixed in content or logged as exceptions via retrospective)
- [ ] A `saas-translator` agent running against a de_AT task loads `.resolved/de_AT.json` (not the command's inlined conventions table) and produces translations that pass the register lint
- [ ] The generated `locales/guides/for-translators/de_AT.md` is human-readable without running the resolver
- [ ] A reviewer can trace any rule cited in the guide back to source YAML via `resolver/index.json` in this repo

## Dependencies

- Blocked by P1-5a (authoring complete in this repo)
- Blocked by P1-4b (app repo integration landed)

## Agent-claimable

Partially. The mechanical work (submodule bump, running resolver, committing generated files) is agent-claimable. Handling any lint failures against current de_AT content requires either native-speaker content fixes or a human-approved retrospective exception.

## Out of scope

- Other locales (Phase 2 fan-out)
- Retiring `/d:start-translation-session` inlined conventions table (follow-up; one line changes per agent prompt)

## Reversibility checkpoint

After this lands:
- de_AT is in the new system
- 34 other locales are untouched
- If the pattern has flaws, blast radius is one locale
- Rollback: revert the submodule bump PR; de_AT falls back to its prior state

## Estimated effort

4–8 hours plus app repo review cycle.
