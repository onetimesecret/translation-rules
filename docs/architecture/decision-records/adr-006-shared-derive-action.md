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
ADR-003 puts both the knowledge and the derivation in this authority; ADR-005
says consumers don't vendor the output, they derive on demand at their pin
(ADR-004). That leaves one open question (issue #35): *how* does the derive step
reach each consumer? Three consumers are in view (the app, the docs site,
marketing), and today none of them share derivation — the resolver is only ever
invoked inline (the app's `resolved-freshness.yml`, this repo's
`schema-validation.yml`).

The options:
- **(a) a reusable step published here** that each consumer calls;
- **(b) each consumer wires its own checkout + resolve** (copy/paste);
- **(c) this repo publishes resolved artifacts** as a release/package that
  consumers pull at the pin.

## Decision
Publish the derive step as a **reusable composite GitHub Action** in this repo at
`.github/actions/derive`. A consumer pins and calls it read-only:

```yaml
- uses: onetimesecret/translation-rules/.github/actions/derive@<pin>
  with:
    ref: <pin>              # same commit as @<pin>
    locales: de_AT fr_CA    # or "all"
    emit-dir: .derived      # gitignored cache, never committed (ADR-005)
```

The action checks out this repo read-only at `ref`, installs the pinned resolver
deps, and runs `lib/resolver/resolve.py` — emitting `.resolved/<locale>.json` and
`guides/for-translators/<locale>.md` into a caller-side cache, with
`_meta.source_commit` = the pin and `_meta.generated_at` = the pin's committer
date (UTC) so output is byte-reproducible for a given pin.

Why a composite action over the alternatives:
- **vs (b) copy/paste:** one implementation, N callers. The resolver invocation,
  dep pins, and the deterministic-stamp logic live once, here, next to the schema
  they derive from. Copy/paste is exactly the drift ADR-003 exists to prevent —
  every consumer would carry a private, silently-aging derive recipe.
- **vs (c) published artifact:** publishing a resolved corpus re-creates a
  vendored-output coupling in a new place — a second freshness surface to keep in
  sync, and the same "derived corpus masquerading as a source" problem ADR-005
  rejects, just hosted instead of committed. The action keeps the cache ephemeral
  and the pin the only shared state.

A composite action (not a `workflow_call` reusable workflow) because derivation
is a *step inside* a consumer's existing job (its CI gate, its translation
orchestration), not a standalone job — the consumer needs the output in its own
workspace to act on.

## Trade-offs
- **We lose:** consumers take a runtime dependency on a translation-rules
  checkout + a Python resolver toolchain at derive time. The app already runs the
  resolver in CI today (`resolved-freshness.yml`), and checks out the authority
  read-only (`validate-register.yml`) — this action just makes that one shared
  step instead of bespoke per-consumer wiring.
- **We gain:** the derive recipe is single-sourced and versioned with the data it
  derives; onboarding a consumer is "pin + call the action."

## Consequences
### Positive
- The #36 replacement freshness gate and the #3510 app no-vendor migration both
  become thin callers of this action rather than bespoke resolver wiring.
- The action's `ref` input and `@<pin>` ref are the same commit, so "which rules
  version did this run use" is unambiguous and assertable.

### Negative
- The action pins `actions/checkout`/`setup-python` by moving major tag (matching
  this repo's existing style); hardening to SHA pins is a later, separate call.

### Neutral
- Separable from ADR-005: one could derive-on-demand with copy/paste. This ADR
  fixes only the *delivery* axis.

## Implementation Notes

### Caller contract (2026-06-25)
The consumer must pass `ref` equal to the commit it pinned `@` to, and should
gitignore `emit-dir`. A freshness gate can assert the run used the consumer's
committed pin by comparing its pin to the action's `source-commit` output.
