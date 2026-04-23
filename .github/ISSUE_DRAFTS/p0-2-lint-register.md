## Title
P0-2 — `bin/lint-register` shell grep tool

## Labels
`phase-0`, `translation-rules`, `tooling`

---

## Context

The `register.yaml` files authored in P0-1 are inert until CI can reject PRs that introduce forbidden tokens. A shell script using `yq` for YAML parsing and `grep` for content matching is sufficient for Phase 0 — no Python, no schema enforcement. The full resolver (P1-2) will replace this later.

## Acceptance criteria

- [ ] `bin/lint-register` is an executable shell script
- [ ] Invocation: `bin/lint-register <locale> <path-glob>` (e.g., `bin/lint-register de_AT "onetimesecret/locales/content/de_AT/*.json"`)
- [ ] **YAML parsing is mandatory via `yq`.** No grep/awk hacks against YAML structure. Script uses `yq` queries (e.g., `yq '.forbidden_tokens[].token'` and `yq '.forbidden_tokens[].context'`) to extract the token list and per-token context. If `yq` is not installed, script exits non-zero with a clear install hint.
- [ ] YAML syntactic correctness is the baseline expected of input files (full schema enforcement lands in P1-1). If the register file fails to parse with `yq`, script exits non-zero.
- [ ] Iterates the path glob and greps each content file for each forbidden token using the token's `context:` rule:
  - `standalone_word` → `\b<token>\b` (case-sensitive)
  - `word_prefix` → `\b<token>` (case-sensitive)
- [ ] Exits non-zero if any forbidden token is found; prints file, line, and matched token in a format consumable by CI logs
- [ ] Exits zero with a summary line on success
- [ ] `--dry-run` flag prints the tokens that would be checked without scanning files
- [ ] Minimal CI workflow file wired up: `.github/workflows/lint-register.yml` that runs `bin/lint-register <locale>` for every locale present in `locales/` on every PR. Workflow ensures `yq` is installed. No app repo wiring yet — that's P1-4. This repo's CI only.

## Files to create

- `bin/lint-register` (executable shell script; ≤ 100 lines)
- `.github/workflows/lint-register.yml` (minimal GitHub Actions workflow)

## Dependencies

- Blocked by P0-1 (needs at least one `register.yaml` to lint against)

## Out of scope

- Schema validation of register files (P1-1 — `yq` parses, does not validate structure).
- Linting against embedded docs or examples (P1 resolver lint).
- Handling locale-specific Unicode normalization edge cases — if a token appears as a composed vs decomposed form, log a known limitation.
- App repo CI wiring (P1-4b).

## Estimated effort

≤ 2 hours including test against current de_AT content.

## Verification

Run against the pre-repair `onetimesecret` app repo at a commit containing the known de_AT violations. Script should produce a non-empty error list. Then run against the post-repair commit — should produce zero errors for de_AT.
