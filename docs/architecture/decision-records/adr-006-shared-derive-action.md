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

Caller contract: pass `ref` equal to the commit you pinned `@` to, and gitignore
`emit-dir`. A freshness gate asserts the run used the committed pin by comparing
it to the action's `source-commit` output (#36).
