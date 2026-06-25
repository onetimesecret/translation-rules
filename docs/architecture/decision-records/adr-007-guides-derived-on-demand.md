---
id: 007
status: proposed
title: ADR-007: Translator guides are derived on demand, not browsed from a hosted channel
---

## Status
Proposed

<!-- Decision content approved by the maintainer (issue #37, 2026-06-25:
     "local / on-demand only"). Left Proposed pending an explicit accept
     sign-off per the ADR lifecycle (this repo's ADR STOP-gate). -->

## Date
2026-06-25

## Context
ADR-005 stops consumers vendoring derived output. That output is two things: the
machine artifact (`.resolved/<locale>.json`, read by translation-time agents and
CI) and the human-readable translator guide (`guides/for-translators/<locale>.md`).
The machine artifact has obvious on-demand readers. The guide raised an open
question (issue #37): with no committed copy, **where does a human browse the
current guide?**

Options considered: publish guides from this repo's CI (a docs site / artifact);
derive them locally on demand only; or keep committing them. The app also still
carries ~35 hand-authored guides, including legacy-named duplicates of canonical
ones (`da.md`, `it.md`, `mi.md`, `sv.md`, `zh-cn.md`, `pt-br.md`, `fr.md`).

## Decision
Guides are **derived on demand only** — no hosted browse channel, no committed
copy. A human who needs to read a guide runs the same derive step CI uses
(ADR-006's action, or `lib/resolver/resolve.py <locale> --emit=md --emit-dir .derived`
locally) and reads it from the ignored cache.

Why no hosted channel: a published guides site is a third place the derived
corpus lives — it ages independently of the pin, needs its own freshness story,
and re-creates the "browsable copy drifts from source" failure ADR-005 removes.
The guide is a *view* of the governed YAML; the reviewable source of truth is the
register/glossary/rules in `rules/locales/<locale>/`, not a rendered guide. The
small cost is that browsing requires running one command; the saving is one fewer
corpus to keep fresh.

Consequently the legacy hand-authored guides committed in the app
(`locales/guides/for-translators/*.md`, including the duplicate pairs above) are
**retired** as part of the app's no-vendor migration (onetimesecret#3510), not
migrated.

## Trade-offs
- **We lose:** zero-setup "open a URL to read the guide." Browsing now needs a
  checkout + one derive command.
- **We gain:** no hosted/committed guide corpus to rot; the guide is always
  exactly the pinned source, never a stale snapshot.

## Consequences
### Positive
- The app migration deletes ~35 committed guides outright rather than rehoming
  them; the guide question stops blocking #3510.

### Negative
- No at-a-glance web view of a locale's guidance for non-technical reviewers;
  if that need becomes real, a CI-published artifact can be added later without
  reversing this decision (it would just be a cache of the same derive).

### Neutral
- Independent of ADR-006's delivery mechanism: guides would be on-demand-only
  regardless of how the derive step is delivered.
