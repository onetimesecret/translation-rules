## Title
Translation Rules v1 — phased rollout (clearinghouse)

## Labels
`epic`, `translation-rules`, `charter`

---

## Charter

Implement the v1 translation rules system per [`SPEC.md`](../../SPEC.md). Purpose: prevent the change-log-as-guidance failure mode and route QA insights into enforceable rules.

## Context

The 2026-04-12 de_AT regression flipped an entire locale from formal `Sie` to informal `du` because a conversational change-log had been pasted into `language-notes.md` under a "Thinking Behind Changes" heading and read by a translator agent as prescriptive. Four locales contaminated (de_AT, pt_PT, uk, hu); two more had lighter damage (da_DK, zh). Full retrospective: `reviews/2026-04-12/`.

The root cause is not a content bug — it is a pipeline that lets descriptive prose flow into prescriptive guidance. `SPEC.md` describes the YAML + JSON Schema + resolver system that makes that flow mechanically impossible.

## Decisions (all resolved in SPEC.md)

- Resolver language: Python 3.11+ (`SPEC.md` §2.3)
- ID format: mixed-mode — dotted paths for rule/register ids, UUID suffix (`<kind>.<key>#<8char>`) for terms, examples, retros (`SPEC.md` §2.2, §4)
- App repo output commit policy: committed, not CI-generated-only (`SPEC.md` §2.3)

App repo maintainer still needs to sign off on P1-4b (the cross-repo PR) but that's coordination, not design.

## Foundational vs knowledge-base content split

**Hard line.** All work tracked by this clearinghouse is *foundational/structural* — SPEC, schemas, resolver, CI gates, retrospective lifecycle, directory layout, `bin/` tooling. Authoring forbidden token lists for locales beyond de_AT, glossary content, worked examples, and baseline pins is *knowledge-base population* and is deliberately deferred until the structural work stabilizes.

de_AT is the single exception: its forbidden token list ships in Phase 0 because it's grounded in `SPEC.md` §1 verbatim and is the structural proof-of-concept.

Quality/content items surfaced during foundational work are logged in `BACKLOG.md` (AOF-style — append-only) and picked up during the knowledge-base population phase. Do not modify `SPEC.md` ad-hoc for these items; that's what `BACKLOG.md` is for.

## Phase 0 — Minimum viable prevention

Shippable immediately. These four tickets alone would have blocked the original regression at `b08e59838` for de_AT.

- [ ] P0-1 — `register.yaml` for **de_AT only** (structural proof; other locales deferred to knowledge-base phase — see `BACKLOG.md`)
- [ ] P0-2 — `bin/lint-register` using `yq` for YAML parsing
- [ ] P0-3 — Port 2026-04-12 retrospective into new `retrospectives/` format
- [ ] P0-4 — Anti-pattern line in UX guide ("harmonize = keys only")

Side task (not blocking Phase 0): file a retrospective for the drift in `~/.claude/commands/d/start-translation-session.md` (conventions table says `de: informal "du"` — same failure pattern, different file).

## Phase 1 — de_AT end-to-end in new system

Blocked until Phase 0 is merged.

- [ ] P1-1 — JSON Schema files for all six YAML types
- [ ] P1-2 — Resolver skeleton + merge algorithm
- [ ] P1-3 — Resolver dual emit (Markdown + JSON)
- [ ] P1-4a — Resolver CI in this repo (agent-claimable)
- [ ] P1-4b — App repo submodule PR + cross-repo CI gate (human-only; coordination with app repo maintainer)
- [ ] P1-5a — de_AT rule authoring + local resolver green (agent-claimable; native-speaker gate at merge)
- [ ] P1-5b — de_AT app repo integration green (follows P1-4b)

## Human-only vs agent-claimable

Tickets marked `human-only` cannot be claimed by `/d:work-tasks-db` agents. They require either coordination across repos (P1-4b) or native-speaker linguistic judgment (parts of P0-1, P1-5a merge gate). Agents may do all the mechanical work and open a PR with a `Needs-native-review` label; a human finalizes.

## Phase 2 — fan-out to remaining locales

**Not filed as individual tickets yet.** Templated after Phase 1 lands and proves the pattern. Approximately 34 per-locale conversions, ideal for parallel execution via `/d:work-tasks-db` with modulo sharding.

## Execution

Phase 0 is small enough to execute directly. Phase 1 can be worked sequentially or with light parallelism. Phase 2 will use `/d:work-tasks-db` — one task per locale, `id % N = agent_index` sharding, no lock contention.

Migration work-tracking DB goes at `.claude/tasks/translation-rules-rollout.db`; distinct from the app repo's per-string translation task DB (`onetimesecret/locales/scripts/tasks/*.py`). See `SPEC.md` §6 for downstream workflow integration.

## Reversibility

- Phase 0 artifacts are additive; removing them restores current state.
- Phase 1 (steps 1–6 of `SPEC.md` §7) makes no app repo changes; reversibility checkpoint at step 7 before submodule landing.
- Phase 1 completion leaves 34 locales still on the frozen 2026-01-20 guides; if the pattern has flaws, only one locale is in the new system.

## Out of scope for v1

See `SPEC.md` §8. Deferred with rationale: language-groups layer, authorities subsystem, per-key baselines, non-binary register (ja keigo, ko politeness), cold-start template, retrospective pruning, agent-filed retrospectives.
