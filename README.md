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
maintainer, never free-written. A resolver reads those files, validates them,
and emits two artifacts per locale: a human-readable guide
(`for-translators/<locale>.md`) and a machine-readable model
(`.resolved/<locale>.json`). The app repo consumes those artifacts and runs a
CI gate that rejects translation PRs containing forbidden tokens.

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
    rules.yaml ────────────────────── pin + derive + CI gate
  rules/base.yaml                           │
                                            ▼
                                   PR touching de_AT strings?
                                   forbidden token found → FAIL
```

**Inheritance — how de_AT gets its rules:**

```
  rules/base.yaml    universal rules (brand names, interpolation, pluralization...)
      │
  rules/locales/de/  German-specific rules (formal Sie form)
  rules.yaml
      │
  rules/locales/de_AT/  Austrian overrides + register lock + glossary
  rules.yaml
  register.yaml      form: formal, pronoun: Sie, forbidden: [du, dein, deine...]
  glossary.yaml      secret object → Geheimnis / secret message → Nachricht
```

**The end-to-end picture** — the authoring→enforcement loop, the agent/human
split, the authoring discipline, and decide-once enforcement — is diagrammed in
[`SPEC.md`](SPEC.md) §2 (Target Architecture).

**Design, rationale, and the current state of every gate live in
[`SPEC.md`](SPEC.md).** This README documents only the contract the app repo
depends on, deliberately kept small so it does not drift from the code. For how
a gate works or whether it is live, read `SPEC.md` (§2.4) and the resolver — not
this file.

Design notes (non-binding agent analysis, not part of the app-repo contract):
[`docs/agent-authored-rules.md`](docs/agent-authored-rules.md).

## Consuming this repo (the app-repo contract)

A consumer **pins** this repo to a commit (ADR-004) and **derives on demand**.
It does *not* vendor this repo as a submodule and does *not* commit the
resolver's output (ADR-005). The derive is the single shared GitHub Action
(ADR-006); output lands in a gitignored cache, regenerated each run and never
committed:

- `<emit-dir>/.resolved/<locale>.json` — machine-readable model for translation
  agents.
- `<emit-dir>/guides/for-translators/<locale>.md` — human-readable guide,
  headed `# GENERATED from translation-rules@<sha> — do not edit, do not cite as
  source`. Derived on demand only — no committed copy, no hosted browse channel
  (ADR-007); read one by deriving it and opening it from the cache.

In the app, `<emit-dir>` is `generated/i18n/` (gitignored); see the app's
`locales/scripts/derive-governance.sh` and its `resolved-derive-gate.yml` /
`validate-register.yml` workflows.

`_meta.source_commit` in the JSON is **the translation-rules commit the output
was derived from** — the ref the consumer pinned, resolved to a concrete commit
at derive time (the action's `git rev-parse HEAD`, or an explicit
`--source-commit`). With the deterministic `_meta.generated_at` (the pinned
commit's committer date, UTC) it makes the output byte-reproducible for a given
pin — which is what the regenerate-in-CI freshness gate relies on.

### What enforces the contract

Both gates derive from a read-only pinned checkout of this repo (the ADR-006
action) and commit nothing:

- **Register forbidden-token gate** — the consumer's `validate-register.yml`
  (onetimesecret/onetimesecret#3432) derives the resolved registers and lints
  changed `locales/content/<locale>/*.json` on every content PR. Zero tolerance.
- **Regenerate-in-CI freshness/integrity gate** — the consumer's
  `resolved-derive-gate.yml` re-derives the full corpus at the pin and lints it,
  so a consumer cannot pin to a commit whose governance does not lint clean.
  This replaces the retired byte-hash gate (old `resolved-freshness.yml`): with
  no committed corpus there is nothing to hash, so the "no hand-edited
  governance" guarantee is preserved by deriving from scratch instead
  (ADR-005; onetimesecret/onetimesecret#3510, #36).

`SPEC.md` §2.4 carries the historical gate snapshot; the ADRs above are the
current source of truth for the consumer model.

## Release tags

`.github/workflows/publish.yml` tags every merge to `main` as `v0.0.N`, where
`N` is the total commit count on `main` — a monotonic build number, not semver.
The tag is a convenience pin only; the binding is always the commit SHA. Pin to
a tag when you want a named, browsable release, or to a SHA otherwise. Tags are
cut on merge to `main` and never re-pointed — neither moved
with `git tag -f` nor deleted and recreated at a different commit. New governance
content gets a new tag, because re-pointing an existing tag either way would
silently change the derived governance for every consumer pinning it and break
their reproducibility and freshness gates.

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
