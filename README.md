# translation-rules

This repo defines the translation rules for Onetime Secret — which register
(formal or informal address), which terms to use for which concepts, and which
words are forbidden — and enforces them mechanically in the app repo's CI.

**The problem it solves.** In April 2026, the de_AT (Austrian German) locale
was silently flipped from formal (`Sie`) to informal (`du`) across email and UI
strings. The cause: an agent read a conversational change-log as prescriptive
guidance. This repo makes that class of error impossible by requiring all
binding guidance to live in structured YAML that cites an accepted source,
passes schema and reference validation, and is CI-enforced — so a rule can
never originate from unreviewed prose, whoever or whatever drafts it.

**How it works.** Rules live as structured YAML in `rules/locales/<locale>/`,
drafted from accepted sources — in practice by an agent — and audited by a
maintainer, never free-written. A resolver
reads those files, validates them, and emits two artifacts per locale: a
human-readable guide (`for-translators/<locale>.md`) and a machine-readable
model (`.resolved/<locale>.json`). The app repo consumes those artifacts and
runs a CI gate that rejects translation PRs containing forbidden tokens.

**Glossary of terms used in this repo:**
- *Register* — formality level (e.g. formal `Sie` vs informal `du` in German).
- *Merge* — the inheritance chain (de_AT → de → base) collapsed into one flat rule set.
- *Resolved* — merged, with every cross-reference verified to exist.
- *Baseline* — a git commit SHA pinned as the last known-good state for a locale.

**Authoring flow — how a rule gets from YAML into enforcement:**

```
  this repo                          app repo (onetimesecret)
  ─────────────────────────────      ──────────────────────────────────────
  rules/locales/de_AT/
    register.yaml  ─┐
    rules.yaml     ─┤─► resolver ──► for-translators/de_AT.md   (human guide)
    glossary.yaml  ─┘                .resolved/de_AT.json        (agent context)
  rules/locales/de/                         │
    rules.yaml ────────────────────── submodule + CI gate
  rules/base.yaml                           │
                                            ▼
                                   PR touching de_AT strings?
                                   forbidden token found → FAIL
```

**Inheritance — how de_AT gets its rules:**

```
  rules/base.yaml       universal rules (brand names, interpolation, pluralization...)
      │
  rules/locales/de/     German-specific rules (formal Sie form)
  rules.yaml
      │
  rules/locales/de_AT/  Austrian overrides + register lock + glossary
  rules.yaml
  register.yaml         form: formal, pronoun: Sie, forbidden: [du, dein, deine...]
  glossary.yaml         secret object → Geheimnis / secret message → Nachricht
```

**The end-to-end picture** — the authoring→enforcement loop, the agent/human
split, the authoring discipline, and decide-once enforcement — is diagrammed in
[`SPEC.md`](SPEC.md) §2 (Target Architecture).

**Design, rationale, and the current state of every gate live in
[`SPEC.md`](SPEC.md).** This README documents only the contract the app repo
depends on, deliberately kept small so it does not drift from the code. For how
a gate works or whether it is live, read `SPEC.md` (§2.4) and the resolver — not
this file.

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
