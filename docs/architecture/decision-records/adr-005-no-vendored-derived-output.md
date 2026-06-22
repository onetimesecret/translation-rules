---
id: 005
status: accepted
title: ADR-005: Consumers do not vendor derived output
---

## Status
Accepted

## Date
2026-06-22

## Context
ADR-003 puts derivation in the authority; ADR-004 pins the version a consumer
derives against. One question remains: does a consumer commit the resolver's
*output* — `.resolved/<locale>.json` and the generated translator guides — into
its own repo, or derive it on demand?

The current app state vendors it. A single locale set produced a +14k-line diff,
and that corpus would be replicated into every consumer.

This ADR revises the earlier inline stance (SPEC §2.3 "Output commit policy:
... committed to the app repo, not CI-generated-only"), which the ADR README
explicitly anticipates revisiting as a numbered record.

## Decision
Consumers do not commit derived output. A consumer commits only the pin (ADR-004)
and derives `.resolved` / guides on demand — in the translation orchestration and
in CI — from a read-only checkout at the pin, into an ignored or temporary
location.

Why: the derived corpus is a cache, not a source. Nothing in a consumer's build or
runtime reads it; the only readers are translation-time agents and CI, both of
which can derive at the pin. The app already proves the pattern —
`validate-register.yml` runs the register gate from a read-only pinned checkout
and commits nothing. Vendoring instead copies the authority's output into every
consumer: N caches to keep fresh, N× the diff noise, and the actual quality signal
(the register/glossary/rule decisions, reviewed in translation-rules YAML) diluted
into thousands of unreviewable generated lines in repos whose reviewers don't own
locale knowledge.

The "committed copy is an anti-tamper baseline" argument (SPEC §2.4) does not
survive: output that is never written to disk cannot be hand-edited, and
regenerate-from-scratch is the recovery. The guarantee is preserved more cheaply
by "agents read only freshly-derived output; CI regenerates; the authority's own
validation is the firewall."

## Trade-offs
- **We lose**: in-repo browsability of guides, and the byte-for-byte freshness
  gate.
- **We gain**: a near-zero consumer footprint, no cache to rot, and review
  concentrated in the authority.

## Consequences
### Positive
- Onboarding a consumer is "add a pin + call the shared derive step," not "vendor
  a corpus." The current +14k app branch collapses to a pin + gitignore + a derive
  step.

### Negative
- The orchestration and CI gain a dependency on a translation-rules checkout + the
  resolver toolchain at derive time (already true for `validate-register.yml`).
- The §2.4 byte-hash freshness gate is retired and must be replaced
  (regenerate-in-CI + assert-pin-is-current); tracked as a separate open item.

### Neutral
- Separable from ADR-004: one could pin-and-vendor, or float-and-derive. This ADR
  fixes only the vendor axis.
