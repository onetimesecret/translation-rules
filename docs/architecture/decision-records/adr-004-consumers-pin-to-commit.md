---
id: 004
status: accepted
title: ADR-004: Consumers pin translation-rules to a specific commit
---

## Status
Accepted

## Date
2026-06-22

## Context
ADR-003 makes consumers derive their output from translation-rules. A consumer
must therefore select *which version* of the authority it derives against.
translation-rules is one-to-many (app, docs, marketing) and evolves on its own
timeline. Two options: float against a moving ref (e.g. `main`), or pin to a
specific commit.

## Decision
Each consumer references translation-rules at a pinned commit SHA, not a floating
branch.

Why pinning over floating: it decouples each consumer's CI and translation runs
from the authority's timeline. A change upstream cannot make an *unrelated*
consumer's gate fail, nor silently alter a translation run; adopting new
governance becomes a deliberate, reviewable pin bump. A derivation at a pin is a
pure function of that commit, so "what governance produced this output?" is always
answerable by SHA. This matches the stance already recorded inline for the
register gate (SPEC §2.4: a read-only pinned checkout, "not a submodule").

The pin is the *only* translation-rules state a consumer commits — ADR-005 keeps
the derived output itself out. It must live in a single canonical location per
consumer: the app already drifted to two gates pinned at two different SHAs, and
consolidating to one pin is what prevents that.

## Trade-offs
- **We lose**: automatic propagation of upstream changes — a consumer must bump to
  adopt new governance.
- **We gain**: decoupling (unrelated PRs aren't hostage to upstream timing) and
  reproducibility (a SHA names exactly the governance used).

## Consequences
### Negative
- A pin goes stale if nothing bumps it. Hand-editing a SHA is not a sustainable
  workflow and already drifted in practice — so the bump is automated (see
  Implementation Notes).

## Implementation Notes

### Automated pin bump (2026-06-22)
The pin is kept fresh by automation, not by hand: a scheduled job / Renovate-style
bot opens a "bump translation-rules → `<sha>`" PR when the authority advances, and
a human merges it on green. The *decision* in this ADR is pinning; the automation
is how the pin stays current without manual toil. Floating would remove the bump
step entirely but is rejected for the decoupling reason above. The automation is
not independently reversible from the pin decision, so it is recorded here rather
than as its own ADR.
