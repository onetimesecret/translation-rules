---
id: 007
status: proposed
title: ADR-007: Translator guides are derived on demand, not browsed from a hosted channel
---

## Status
Proposed

<!-- Decision approved by the maintainer (#37, 2026-06-25: "local / on-demand
     only"). Left Proposed pending an explicit accept sign-off. -->

## Date
2026-06-25

## Context
ADR-005 stops consumers vendoring derived output. That output is two things: the
machine artifact (`.resolved/<locale>.json`) and the human translator guide
(`guides/for-translators/<locale>.md`). The machine artifact has obvious
on-demand readers; the guide raised an open question (#37): with no committed
copy, where does a human browse the current guide? The app also still carries
~35 hand-authored guides, including legacy-named duplicates of canonical ones
(`da.md`, `it.md`, `mi.md`, `sv.md`, `zh-cn.md`, `pt-br.md`, `fr.md`).

## Decision
Guides are **derived on demand only** — no hosted browse channel, no committed
copy. A human reads a guide by deriving it the way CI does (the ADR-006 action,
or `lib/resolver/resolve.py <locale> --emit=md --emit-dir .derived` locally) and
opening it from the ignored cache.

A published guides site would be a third place the derived corpus lives, aging
independently of the pin — the "browsable copy drifts from source" failure
ADR-005 removes. The reviewable source of truth is the YAML in
`rules/locales/<locale>/`; the guide is only a rendered view of it. The cost is
that browsing needs one command; the saving is one fewer corpus to keep fresh.
If a web view ever becomes a real need, a CI-published artifact can be added
later without reversing this — it would just be a cache of the same derive.

Consequently the legacy hand-authored guides in the app (including the duplicate
pairs above) are **retired**, not migrated, as part of onetimesecret#3510.
