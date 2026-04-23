## Title
P0-1 — Author `register.yaml` for de_AT, pt_PT, uk, hu

## Labels
`phase-0`, `translation-rules`, `register-lock`

---

## Context

The four locales identified in `reviews/2026-04-12/cross-locale-audit.md` as High-severity register flips need a machine-readable forbidden-token list for CI grep. This is the single highest-leverage artifact in the whole design: the register lock on de_AT alone would have blocked the original regression.

## Acceptance criteria

- [ ] `locales/de_AT/register.yaml` exists with `form: formal`, `pronoun: Sie`, and forbidden tokens `[du, dein, deine, deinen, deinem, deiner, dich, dir, euch, euer]`
- [ ] `locales/pt_PT/register.yaml` exists with `form: formal`, `pronoun: você`, and forbidden tokens covering the pt_PT informal set `[tu, teu, tua, teus, tuas]`
- [ ] `locales/uk/register.yaml` exists with `form: formal`, `pronoun: Ви`, and forbidden tokens covering the ти-form set (`[ти, твій, твоя, твоє, твої, тебе, тобі]`)
- [ ] `locales/hu/register.yaml` exists with `form: formal`, `pronoun: Ön/Önök`, and forbidden tokens covering the te-form set (`[te, ti, téged, neked, tiéd]`)
- [ ] Each file carries `baseline_ref:`, `retro_refs: [2026-04-12-de_AT-register-flip]` (or locale-specific retro id), and an `exceptions: []` field (explicit empty list)
- [ ] Each file has a `rule_ref:` in the form `register.<locale>.formality`
- [ ] **Native-speaker review (human-only merge gate).** Agents may author the YAML; final merge requires a human native-speaker spot-check captured in the PR description per locale (even if brief — "spot-checked by N, no objections"). Agents opening a PR should apply the `Needs-native-review` label and stop.

## Schema (provisional, pending P1-1)

```yaml
id: register.de_AT
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

## Dependencies

- None. This is Phase 0 and unblocks P0-2.

## Out of scope

- JSON Schema file for `register.yaml` (P1-1). Field names here are provisional; the schema will enforce them later.
- Register files for the other 31 locales (Phase 2 fan-out).
- `baselines.yaml` population (P1-5 for de_AT; Phase 2 for others).

## Estimated effort

≤ 1 hour. Values are known from `reviews/2026-04-12/` and `SPEC.md` §2.2.
