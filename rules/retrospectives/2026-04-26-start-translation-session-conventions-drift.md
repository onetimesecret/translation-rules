---
id: 2026-04-26-start-translation-session-conventions-drift
date: 2026-04-26
status: applied
triggered_by:
  commits: []
  incident: "Hand-maintained 'Locale Conventions Reference' table in /d:start-translation-session.md drifts from authoritative register guidance — same failure pattern as 2026-04-12, different location"
affected_locales: [de, de_AT, es, pt_BR, fr_CA, fr_FR, it, nl, ja, zh, ko, ru]
affected_rules: []
examples_added: []
baseline_pins: []
resolved_in_commit: e0cb652
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

- `register.de_AT.formality` — already locked by the 2026-04-12 retro
  (its target; `resolved_in_commit: 8cf0e22`). This guardrail only
  *references* it: the table's `de | informal du` claim must not be
  inferred to apply to de_AT. It is therefore **not** in `affected_rules`,
  which per SPEC §3 records only ids this retro's closing PR will *touch*.
  `affected_rules` is empty because this retro's closure is structural —
  the resolver landing and table removal below — not a rule edit. (Do not
  re-add a dotted rule here: the resolver requires every `affected_rule` to
  resolve in every `affected_locale`, and this drift spans locales where a
  de_AT-only rule does not exist.)
- Phase 1 P1-2 (resolver) and P1-4 (cross-repo wiring) close this retro
  by making the inlined table redundant. Until then, the table should
  carry an explicit `de_AT: formal "Sie"` row and a note pointing to this
  retrospective.

## Out of scope

The user's private command file is not in any repo this rule system
governs. This retrospective tracks the finding so it cannot be lost; the
edit to the command is the user's call.

## Closure review (2026-07-12)

All closure conditions verified met; status flipped to `applied`.

- **The inlined table is gone.** `~/.claude/commands/d/start-translation-session.md`
  no longer exists (the whole `d/` command directory was removed). No
  "Locale Conventions Reference" table or `de | informal "du"` claim
  survives in any current translator entry point or in the app repo.
- **The Phase 1 contract is live, in its ADR-005 (no-vendor) form.** The
  replacement entry points (`~/.claude/commands/i18n/*`) carry no
  per-locale conventions; each agent follows the app repo's
  `locales/AGENT_TRANSLATION_PROTOCOL.md` and reads governance from
  `generated/i18n/.resolved/{LOCALE}.json`, derived on demand by
  `locales/scripts/derive-governance.sh` from a pinned read-only checkout
  of this repo (the pin contract is guarded by a test, app repo
  `24d37d6e32`). The retro anticipated a vendored `.resolved/` (P1-4b
  submodule); ADR-005/ADR-007 replaced vendoring with derive-on-demand —
  the closure condition is the *contract* (agents consume resolver
  output, not hand-maintained prose), which this satisfies.
- **The CI gate is live in the app repo.** `validate-register.yml` derives
  each locale's resolved register at the pin via the shared derive action
  (ADR-006, `e0cb652`) and scans content with this repo's own lint engine
  (ADR-008).

`resolved_in_commit: e0cb652` is the cross-repo wiring (P1-4: shared
derive composite action + ADR-006/007) that made the inlined table
structurally redundant — the resolution path §"Affected rules" named.
`affected_rules` stays `[]` as filed: closure was structural, no rule
edit.
