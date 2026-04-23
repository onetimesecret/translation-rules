## Title
P0-1 — Author `register.yaml` for de_AT

## Labels
`phase-0`, `translation-rules`, `register-lock`

---

## Context

de_AT is the incident locale and its forbidden token list is grounded in `SPEC.md` §1 verbatim. Authoring it as the first — and for Phase 0, *only* — register file proves the structural shape without pulling knowledge-base population work forward. Other locales' token lists are deferred to the knowledge-base population phase; see `BACKLOG.md`.

This is the single highest-leverage artifact in the whole design: the register lock on de_AT alone would have blocked the original regression.

**Scope note.** Phase 0 is foundational work. Authoring forbidden-token lists for pt_PT, uk, hu, and the other 30+ locales is knowledge-base content and is explicitly deferred (tracked in `BACKLOG.md`). Do not expand P0-1 scope to other locales under any circumstance.

## Acceptance criteria

- [ ] `locales/de_AT/register.yaml` exists with `form: formal`, `pronoun: Sie`, and forbidden tokens `[du, dein, deine, deinen, deinem, deiner, dich, dir, euch, euer]` (source: `SPEC.md` §1)
- [ ] File carries `baseline_ref:`, `retro_refs: [2026-04-12-de_AT-register-flip]`, and an `exceptions: []` field (explicit empty list)
- [ ] File has `rule_ref: register.de_AT.formality`
- [ ] File carries a `source:` field (nullable) at the register-file level *and* per `forbidden_tokens` entry if sources differ. For de_AT in P0-1, top-level `source: SPEC.md#1` is acceptable. See P1-1 for schema formalization.
- [ ] YAML is syntactically valid (parses with `yq`). No schema enforcement yet; schema lands in P1-1.
- [ ] **Native-speaker review (human-only merge gate).** Agents may author the YAML; final merge requires a human native-speaker spot-check captured in the PR description ("spot-checked by N, no objections"). Agents opening a PR should apply the `Needs-native-review` label and stop.

## Schema (provisional, pending P1-1)

```yaml
id: register.de_AT
source: SPEC.md#1
form: formal
pronoun: Sie
possessive: [Ihr, Ihre, Ihren, Ihrem, Ihrer]
forbidden_tokens:
  - { token: du,   context: standalone_word, severity: error }
  - { token: dein, context: word_prefix,     severity: error }
  - { token: dich, context: standalone_word, severity: error }
  - { token: dir,  context: standalone_word, severity: error }
exceptions: []
rule_ref: register.de_AT.formality
baseline_ref: baselines.de_AT
retro_refs: [2026-04-12-de_AT-register-flip]
```

Flow-style `{ token: ..., context: ..., severity: ... }` entries are expected for readability; the P0-2 linter uses `yq` and tolerates both flow and block styles, but flow style keeps Phase 0 files compact.

## Dependencies

- None. This is Phase 0 and unblocks P0-2.

## Out of scope

- JSON Schema file for `register.yaml` (P1-1). Field names here are provisional; the schema will enforce them later — including formalizing the `source:` field.
- **Register files for any locale other than de_AT.** pt_PT, uk, hu, and all remaining locales are knowledge-base content, deferred to a later phase. Tracked in `BACKLOG.md`.
- `baselines.yaml` population (P1-5 for de_AT; deferred for others).

## Estimated effort

≤ 30 minutes. Values are known from `SPEC.md` §1 verbatim.
