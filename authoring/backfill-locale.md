# Backfill a locale into structured rules

What it takes to make `<locale>` resolved-only-ready: a non-empty
`.resolved/<locale>.json` (register + glossary, not just `base.yaml`) that
passes lint. Until this is done, a locale must NOT be flipped to resolved-only —
`base.yaml` alone gives an agent no register and no terminology, which
re-opens the register-regression class (see `retrospectives/`,
`reviews/2026-04-12/`).

**Source of truth for the content.** Lift the terminology, formality, and
critical rules from the app repo's existing prose guide —
`onetimesecret/locales/guides/for-translators/<locale>.md` — plus the live
`locales/content/<locale>/*.json`. You are *transcribing* agreed knowledge
into schema, not inventing it. Targets/examples you author are AGENT-AUTHORED
and need native-speaker sign-off before merge (PR label; see `locales/de_AT/`).

## Files to create under `locales/<locale>/`

Validate against `schema/*.json`. Copy `locales/de_AT/` as the worked example.

1. **`register.yaml`** — the binding register lock. Required: `id`
   (`register.<locale>`), `source`, `form`
   (`formal|informal|mixed|other`), `pronoun`, `forbidden_tokens` (may be `[]`,
   never null), `exceptions` (may be `[]`, never null). Each forbidden token =
   `{token, context, severity}`; `context` ∈
   `standalone_word|word_prefix|substring|any`. Add `possessive`, `rule_ref`,
   `baseline_ref`, `retro_refs` where they apply. Languages without a T/V split
   (ja keigo, ko politeness): `form: other` + the `register_spec` extension.

2. **`glossary.yaml`** — sense-split terms. Required: `id`
   (`glossary.<locale>`), `source`, `terms`. Each term needs `id` + `key`; add
   `en`, a locale-keyed target (`<locale>: <string>` or
   `<locale>: {<sense>: {target, rule_ref}}`), `disambiguation`
   (`heuristic`, `key_patterns`), `rule_refs`, and `examples`. Give every term at
   least one `good` and one `bad` example: `{id, source, target, verdict}`,
   `verdict` ∈ `good|bad|borderline`.

3. **`rules.yaml`** — locale layer. Required: `id` (`rules.<locale>`),
   `source`. Set `inherits` to an **existing** parent id (`base`, or a family
   parent you also create — see below), `merge_strategy` (`append` is usual),
   any locale-specific `rules`, and `register_ref`/`glossary_ref`/`baseline_ref`.

4. **`baselines.yaml`** (append an entry, not a new file) — pin the commit where
   content was last known-good: `{commit, pinned_on, invariants,
   retro_id | justification_doc}`. One of `retro_id`/`justification_doc` is
   required.

5. **`docs/`** (optional) — rationale prose, referenced via `docs:`, never
   inlined. Bare-prose forbidden tokens fail lint; wrap any mention in backticks.

## IDs

Mint stable ids — never hand-roll the `#<8hex>` suffix:

```
bin/mint-id term <key>     # glossary term  -> term.<key>#<8hex>
bin/mint-id ex   <key>     # worked example -> ex.<key>#<8hex>
bin/mint-id rule <key>     # rule           -> rule.<key>#<8hex>
```

## Inheritance

`inherits` must resolve or the resolver fails. A regional variant needs its
base-language parent to exist first: for `fr_CA`, create `locales/fr/`
(inheriting `base`) **then** `locales/fr_CA/` inheriting `rules.fr` — mirroring
`de_AT -> de -> base`. A standalone language inherits `base` directly.

## Verify (must pass before merge)

The resolver is `uv`-managed; `uv run` auto-syncs deps from the lockfile.

```
uv run resolver/resolve.py <locale> --lint --validate-only   # resolves + lints, no writes
```

Lint (SPEC §2.3 step 6) checks only `good` examples:
- no register `forbidden_tokens` in a good example's target (unless `exceptions`-covered);
- every good example's target contains one of its term's sense targets (word_prefix);
- no bare-prose forbidden tokens in embedded docs.
`bad`/`borderline` examples are exempt — they exist to demonstrate the wrong form.

Then emit the committed artifacts into the app repo:

```
uv run resolver/resolve.py <locale> --lint --emit=md,json --emit-dir <path-to>/onetimesecret/locales
# writes onetimesecret/locales/.resolved/<locale>.json + .../guides/for-translators/<locale>.md
```

## Done

- `uv run resolver/resolve.py <locale> --lint` exits 0;
- `.resolved/<locale>.json` has populated `register` and `glossary` (not just
  base `rules`);
- `bin/lint-register <locale> "<app>/locales/content/<locale>/*.json"` is clean;
- native-speaker sign-off recorded on the PR.

Only then is the locale eligible to flip to resolved-only.
