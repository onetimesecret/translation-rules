# translation-rules

Authority repo for translation guidance — the rules, registers, and glossaries
that the companion app repo (`onetimesecret/onetimesecret`) consumes as
generated artifacts. Its job is to prevent the change-log-as-guidance failure
mode: only schema-validated, human-authored YAML can bind translator behavior.

**Design, rationale, and the current state of every gate live in
[`SPEC.md`](SPEC.md).** This README documents only the contract the app repo
depends on, deliberately kept small so it does not drift from the code. For how
a gate works or whether it is live, read `SPEC.md` (§2.4) and the resolver — not
this file.

Design notes (non-binding agent analysis, not part of the app-repo contract):
[`docs/agent-authored-rules.md`](docs/agent-authored-rules.md).

## Consuming this repo (the app-repo contract)

The app repo vendors this repo as a git submodule and commits the resolver's
output next to it (`SPEC.md` §2.3):

- `locales/guides/for-translators/<locale>.md` — human-readable guide.
  Generated, headed `# GENERATED from translation-rules@<sha> — do not edit, do
  not cite as source`.
- `locales/.resolved/<locale>.json` — machine-readable model for translation
  agents.

`_meta.source_commit` in that JSON is **the translation-rules commit the
artifacts were generated from** — the rules-repo `HEAD` at resolve time, or an
explicit `--source-commit` override. It is *not* a copy of the app repo's
submodule pointer (this repo cannot know its own future submodule SHA). The
relationship runs the other way: the app-repo gate verifies
`source_commit == submodule SHA`, which is what proves the committed artifacts
were generated from the exact rules commit the submodule pins (`SPEC.md` §2.4).

### What enforces the contract

- **Live** — the register forbidden-token gate. App-repo CI
  (`validate-register.yml`, onetimesecret/onetimesecret#3432) runs
  `bin/lint-register` from a read-only pinned checkout of this repo against
  `locales/content/<locale>/*.json` on every content PR. Zero tolerance.
- **Planned** (`SPEC.md` §2.4) — submodule-pointer freshness, the
  `source_commit == submodule SHA` check above, and a byte-for-byte hash lock on
  the generated markdown so hand edits are rejected.

Treat the planned items as not-yet-enforced: do not assume drift between rules
and committed artifacts is caught until the `SPEC.md` §2.4 Status line says it
is. That Status line, not this README, is the source of truth for what is wired.

## Release tags

`.github/workflows/publish.yml` tags every merge to `main` as `v0.0.N`, where
`N` is the total commit count on `main` — a monotonic build number, not semver.
The tag is a convenience pin only; the binding is always the commit SHA. Pin the
submodule to a tag when you want a named, browsable release, or to a SHA
otherwise.

## Working in this repo

```bash
uv sync                                              # resolver + dev deps
python lib/resolver/resolve.py <locale> --lint --emit md,json   # resolve one locale
python lib/resolver/resolve.py --all --lint                     # resolve every locale
```

CI runs the schema, type-check, register-lint, and `rules/_archive/` firewall gates on
every PR. `SPEC.md` §2.4 is the authoritative, current list of those gates and
what each enforces.

## Reviews vs retrospectives

Reviews are raw observations; retrospectives are the lifecycle-tracked decisions
findings drive. The canonical definition — including how cross-locale roll-ups
fit — lives in [`_references/reviews/README.md`](_references/reviews/README.md#review-vs-retrospective).
