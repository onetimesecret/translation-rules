---
id: 003
status: accepted
title: ADR-003: translation-rules is the single authority for translation knowledge and derivation
---

## Status
Accepted

## Date
2026-06-22

## Context
The translation infrastructure serves multiple consumers: the application
(`onetimesecret`), the docs site, and potentially marketing. Each consumer needs
two things — the domain *knowledge* (locale YAML: registers, glossaries, rules)
and the *derivation logic* (the resolver that turns that knowledge into usable
per-locale output). This ADR settles where those two things live and who owns
them.

It formalizes a stance the repo already took inline (SPEC §2.3 / §2.4) once that
stance became load-bearing for the decisions in ADR-004 and ADR-005.

## Decision
Both the knowledge (YAML source) and the derivation logic (resolver) live in
translation-rules. Consumers own neither. A consumer references translation-rules
and derives its outputs from it.

Why: derivation is tightly coupled to the knowledge schema, and the relationship
is one-to-many. Centralizing both means a schema or rule change happens once, in
one place, and propagates outward — rather than requiring coordinated edits
across every consumer.

## Alternatives considered
**Knowledge here, derivation in each consumer.** Each repo implements its own
resolver against shared YAML. Rejected: derivation is tightly coupled to the
schema, so multiple resolvers drift, and a schema change forces coordinated
updates across every consumer.

**No single authority.** Each consumer maintains its own knowledge and derivation
independently. Rejected: this is the state that produced 18k-line vendored diffs
and quality signal buried in noise — duplication with no coordination.

**Split knowledge by domain.** App-specific translations in the app repo,
docs-specific in the docs repo, shared terms in translation-rules. Rejected: the
boundary between "shared" and "domain-specific" shifts over time, and the
resolver needs a coherent corpus to produce consistent output.

## Consequences
- Consumers need a mechanism to reference translation-rules at a specific point
  in time — see **ADR-004** (pin to a commit).
- Consumers must not vendor derived output, since they don't own the derivation —
  see **ADR-005** (derive on demand).
- Changes to knowledge or derivation logic happen in one place and propagate
  outward through the pin.
