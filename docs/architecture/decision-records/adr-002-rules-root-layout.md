---
id: 002
status: accepted
title: ADR-002: Rules-root repository layout
---

## Status
Accepted

## Date
2026-06-22

## Context
The repository grew organically. Governing content (`base.yaml`, `baselines.yaml`, per-locale `locales/`, `retrospectives/`), tooling (`resolver/`), and non-governing reference material (`reviews/`, `local-guides/`, `en-translation-docs/`, `authoring/`, stray plan docs) all accumulated at the root, interleaved with no structural cue to which was which.

The structured-vs-prose firewall — the load-bearing invariant of this system (`SPEC.md` §2.1) — was a per-file property, not a directory boundary. Whether a file binds depended on what it *was* (schema-validated YAML) and where it happened to sit (`_archive/` excluded), not on a clean root-level partition the tooling could key off. `_references`-style material lived next to governing YAML with nothing but convention keeping the resolver and the CI gates from walking into it.

The pressure to act came from a stale reference implementation. Issue #25 (`fix/clarity`) carried a full reorganization plus resolver wiring, but it was cut against an old tree and went stale while content work — new locales, retrospectives, gate wiring — continued on the original layout. Rebasing #25 forward would have replayed a large, conflict-prone diff over a tree that had moved underneath it.

## Decision
**Sort everything in the repository under three roots by role, and leave a small, deliberate set of things at root.**

- `rules/` — governing content (the binding set): `base.yaml`, `baselines.yaml`, `locales/`, `retrospectives/`, and the `_archive/` firewall.
- `lib/` — tooling: the `resolver/` package.
- `_references/` — non-governing material: `reviews/`, `local-guides/`, `en-translation-docs/`, `authoring/`, the recovery/plan docs, and the next-languages list.

Stays at root: `schema/`, `bin/`, `tests/`, `.github/`, the meta docs (`SPEC.md`, `README.md`, `SPEC-cross-property.md`, `BACKLOG.md`), and `docs/` — the resolver-embedded rationale prose plus design/ADR docs. Resolver output moves from `.resolved/` to `generated/` (gitignored; the committed artifacts the app repo consumes are unaffected and keep their own paths).

`schema/` stays at root **non-negotiably**. Its `$id` URLs — `https://onetimesecret.github.io/translation-rules/schema/<name>.schema.json` — are the published contract. Moving the directory would either break every published `$id` or force a rewrite of the contract URLs that downstream consumers pin. Neither is acceptable for a reorganization whose entire point is internal tidiness.

This was **re-derived as a clean, scripted move against current `main`** rather than by merging the stale #25. A deterministic migration script applied to the live tree avoids replaying #25's conflicts and guarantees the move matches the repository as it actually is, not as it was when #25 was authored. #25's reference implementation informed the target shape; it did not supply the diff.

## Consequences
### Positive
- The firewall is now a directory boundary, not a per-file property. `_references/` is excluded from tooling **by path** — the resolver and gates can refuse to look there structurally, rather than relying on each file being individually well-behaved.
- Role is legible from the root: governing vs. tooling vs. reference is the first thing the tree communicates.

### Negative
- Open branches face one big-bang rebase. Any in-flight work was authored against the old paths and must move in a single step; there is no incremental path that keeps both layouts valid.
- App-repo-facing artifact paths are deliberately left unchanged, so two `for-translators` notions now coexist: this repo's source/reference material under `_references/`, and the committed artifact the app repo consumes at its own `locales/guides/for-translators/<locale>.md`. The asymmetry is documented (`SPEC.md` §2.3, §5) rather than resolved.

### Neutral
- `schema/` sits at root while its sibling governing content (`base.yaml`, `locales/`, `retrospectives/`) lives under `rules/`. This is an intentional, documented asymmetry: the `$id` contract pins `schema/` at root, and the governing-content grouping is worth keeping despite `schema/` not joining it.
