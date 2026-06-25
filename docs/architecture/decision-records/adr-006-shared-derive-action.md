---
id: 006
status: accepted
title: ADR-006: Deliver the derive step as a reusable composite action
---

## Status
Accepted

## Date
2026-06-25

## Context
ADR-003 puts knowledge and derivation in this authority; ADR-005 has consumers
derive on demand at their pin (ADR-004) instead of vendoring output. Open
question (#35): *how* does the derive step reach each consumer? Today none share
it — the resolver is invoked inline in the app's `resolved-freshness.yml` and
this repo's `schema-validation.yml`. Three consumers are in view (app, docs,
marketing).

## Decision
Publish the derive step as a **reusable composite GitHub Action** at
`.github/actions/derive`. A consumer pins and calls it read-only:

```yaml
- uses: onetimesecret/translation-rules/.github/actions/derive@<pin>
  with:
    ref: <pin>              # same commit as @<pin>
    locales: de_AT fr_CA    # or "all"
    emit-dir: .derived      # gitignored cache, never committed (ADR-005)
```

It checks out this repo read-only at `ref`, runs `lib/resolver/resolve.py`, and
emits `.resolved/<locale>.json` + `guides/for-translators/<locale>.md` into a
caller-side cache, stamping `_meta.source_commit` = the pin and
`_meta.generated_at` = the pin's committer date (UTC) so output is
byte-reproducible per pin.

A composite action — not per-consumer copy/paste (the drift ADR-003 exists to
prevent: every consumer would carry a private, aging derive recipe), and not a
published resolved artifact (that re-creates a vendored-output coupling in a new
hosted place, which ADR-005 rejects). Composite rather than `workflow_call`
because derivation is a step *inside* a consumer's existing job (its gate, its
translation run), which needs the output in that job's workspace.

Caller contract: in steady state pass `ref` equal to the commit you pinned `@`
to, and gitignore `emit-dir`. A freshness gate asserts the run used the committed
pin by comparing it to the action's `source-commit` output (#36).

## Consequences

The action pins its CODE (`uses: .../derive@<pin>`, a SHA digest) and its DATA
(`with: { ref: <pin> }`, the rules+resolver it checks out) *separately*. The
sample above is the steady state — both at the same release. They MAY also
differ deliberately: the override path lets a maintainer point `ref:` at a
candidate translation-rules release and dry-run it against the corpus *before*
bumping the action SHA (the decoupling onetimesecret#3541 adopts). This is
ref-type agnostic — a SHA or a tag in `ref:` both work, no code change needed —
because `ref` is checked out *first*, then collapsed to a concrete SHA by
`git rev-parse HEAD` of the checkout. In the action path that rev-parse is the
wrapper's `resolve-ref` step, which feeds the SHA to the resolver as
`--source-commit`; run bare, the resolver's own `_resolve_source_commit` does the
same rev-parse. Either way the SHA is derived post-checkout, so whatever `ref`
names resolves correctly. Two conventions make that override safe:

**Release tags are immutable.** `v0.0.N` tags (`.github/workflows/publish.yml`,
cut on every merge to `main`) are never moved — no `git tag -f`, no re-point.
New governance content means a new tag. Re-pointing a tag would silently change
the derived governance for every consumer pinning that tag and break the
per-pin byte-reproducibility this ADR relies on (`_meta.source_commit` /
`_meta.generated_at`, ADR-005). So a `ref:` pinned by tag name is as stable as
one pinned by SHA.

**The consumer contract is back-compatible across releases.** Because a run may
execute the action wrapper (`uses:`) and the resolver/data (`ref:`) at *different*
releases, the surface where the wrapper meets the resolver must not change
incompatibly without a deliberate major release. That frozen surface is:

- action inputs: `ref`, `locales`, `emit`, `lint`, `emit-dir`, `checkout-path`
- action outputs: `emit-dir`, `source-commit`, `generated-at`
- resolver CLI flags: `--emit`, `--emit-dir`, `--source-commit`, `--generated-at`,
  `--lint`
- the `rules/` directory layout the resolver runs against (ADR-002)
- the pinned resolver dep set (`jsonschema`, `referencing`, `pyyaml`), declared
  in lockstep across `pyproject.toml`, this `action.yml`, and the CI/resolver
  pins it mirrors — a divergence here is the same hazard

A mismatch — e.g. an older action wrapper invoking a renamed resolver flag — must
fail LOUDLY (non-zero exit), never produce wrong-but-green output. Documenting
the contract is what lets us keep that promise deliberately rather than by luck.

Caveat on "major release": the release automation only ever emits `v0.0.N`,
where `N` is the monotonic commit count on `main` (see README "Release tags");
the major and minor are permanently `0`. There is no automated path to a major
bump, so honouring this contract is a deliberate human gate — a major release
would itself be a manual change to the release process, not something the tagger
produces. Semver is aspirational here, not yet adopted; the guarantee is the
intent to not break the listed surface silently, not a scheme the automation
enforces.

Consumers pin to a commit (ADR-004) and never vendor the derived output
(ADR-005); both conventions above exist to keep those two guarantees intact when
the CODE and DATA pins are allowed to diverge.
