## Title
P1-3 — Resolver dual emit (Markdown + JSON) + lint

## Labels
`phase-1`, `translation-rules`, `resolver`

---

## Context

`SPEC.md` §2.3 specifies dual outputs: Markdown for humans (the replacement for `local-guides/for-translators/<locale>.md`) and JSON for CI lint + agent context. `SPEC.md` §6.1 places concrete constraints on the JSON shape (under 20 KB, key-grep-friendly, partitioned by agent decision surface).

## Acceptance criteria

- [ ] `resolver/emit_markdown.py` produces human-readable per-locale guide with `# GENERATED from translation-rules@<submodule-sha> — do not edit, do not cite as source` header
- [ ] `resolver/emit_json.py` produces the structure documented in `SPEC.md` §2.3:
  - `_meta: { source_commit, schema_version, generated_at }`
  - `register: { form, pronoun, forbidden_tokens, rule_ref }`
  - `glossary: { <term>: { <sense>: { target, rule_ref, examples: [...] } } }`
  - `rules: [...]`
  - `context: [...]`
  - `rationale_index: { rule_id: [doc_paths] }`
  - `declined_index: [...]`
  - `anti_patterns_ref: [...]`
- [ ] Stable key ordering (sorted, deterministic output — diffs must be reviewable)
- [ ] `resolver/lint.py` implements the SPEC.md §2.3 step 6 assertions:
  - Every example passes its own register lint (forbidden tokens absent)
  - Every example's target matches its sense's target (substring/morphological)
  - Forbidden tokens absent from embedded docs
  - Every interpolation in `en` preserved in target values
- [ ] `resolve.py` `--emit=md,json` and `--lint` flags are wired in; `--all` runs across every locale
- [ ] JSON output for de_AT is under 20 KB (per `SPEC.md` §6.1 constraint)
- [ ] Pluribus-style `--emit=bundle` combines all resolved JSONs with UUID-delimited sections; `--split <bundle>` restores per-locale JSONs tolerant of filename mangling (per `SPEC.md` §4)

## Dependencies

- Blocked by P1-2 (merge + ID resolution must work)
- Blocks P1-4 (CI gate needs emit output to check)

## Out of scope

- Wiring the output paths in the app repo — that's P1-4
- Migrating the existing 35 `local-guides/for-translators/*.md` files — Phase 2 per locale

## Estimated effort

10–14 hours. Markdown templating is straightforward; JSON shape stabilization and lint predicates are the time sinks.

## Verification

- `resolve.py de_AT --emit=json` produces a file agents can load with `json.load` and find the register-lock forbidden token list at a documented path.
- `resolve.py de_AT --emit=md` produces a file a human translator can read without running the resolver.
- `resolve.py --all --emit=bundle` produces a single file that `--split` restores correctly after a round-trip through a filename-mangling translation service.
