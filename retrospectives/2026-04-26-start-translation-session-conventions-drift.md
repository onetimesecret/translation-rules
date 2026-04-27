---
id: 2026-04-26-start-translation-session-conventions-drift
date: 2026-04-26
status: pending
triggered_by:
  commits: []
  incident: "Hand-maintained 'Locale Conventions Reference' table in /d:start-translation-session.md drifts from authoritative register guidance — same failure pattern as 2026-04-12, different location"
affected_locales: [de, de_AT, es, pt_BR, fr_CA, fr_FR, it, nl, ja, zh, ko, ru]
affected_rules: [register.de_AT.formality]
examples_added: []
baseline_pins: []
resolved_in_commit: null
supersedes: []
declined_reason: null
would_change_decision_if: null
---

# 2026-04-26 — start-translation-session conventions table drift

## What happened

`~/.claude/commands/d/start-translation-session.md` contains an inlined
"Locale Conventions Reference" table at lines 124-139. The table is
hand-maintained and has drifted from the register guidance the rule system
is now establishing. Most directly, line 129 declares:

> **de** | informal "du"; secret→Nachricht, passphrase→Passphrase, burn→loschen

This is the same class of statement that propagated the 2026-04-12 de_AT
register flip. The November 2025 QA review (`reviews/2025-11-16/`)
concluded de docs should use formal `Sie`, and the de_AT register lock
authored in this Phase 0 PR makes `du`-form forbidden for de_AT — yet the
shared command still tells translation agents `de` is informal `du` with no
regional caveat for de_AT. An agent invoked under this command will be
seeded with the same contradiction that produced the original incident.

Several other rows in the table carry similar unverified register claims
(`es | informal tu`, `nl | informal je`, `ja | polite form`, `ko | polite
form`, `ru | informal ты`). They are flagged for review but not actioned
here.

## Root cause

Same as 2026-04-12: prose guidance hand-edited in one location, no
mechanical pipeline to the locales it claims to describe. The table is
the same kind of artifact as the change-log paragraphs in
`language-notes.md` that produced the original incident — descriptive
authoring with no schema, no source-of-truth, no enforcement.

## Why this is a guardrail, not just a fix

Per SPEC §6.4, this drift is captured because deleting or correcting the
table without replacing the upstream coupling will not prevent recurrence.
The rule change required to close this retrospective is the Phase 1
contract: agents in `start-translation-session` consume
`onetimesecret/locales/.resolved/<locale>.json` instead of an inlined
table, and the table is removed from the command. That depends on the
resolver landing.

## Affected rules and resolution path

- `register.de_AT.formality` — already locked by this Phase 0 PR; the
  table's `de | informal du` claim must not be inferred to apply to de_AT.
- Phase 1 P1-2 (resolver) and P1-4 (cross-repo wiring) close this retro
  by making the inlined table redundant. Until then, the table should
  carry an explicit `de_AT: formal "Sie"` row and a note pointing to this
  retrospective.

## Out of scope

The user's private command file is not in any repo this rule system
governs. This retrospective tracks the finding so it cannot be lost; the
edit to the command is the user's call.
