---
id: 2026-05-02-fr-only-decline
date: 2026-05-02
status: declined
triggered_by:
  incident: fr-only proposal, must not leak into de_AT output
affected_locales:
  - fr
affected_rules: []
examples_added: []
baseline_pins: []
resolved_in_commit: null
supersedes: []
declined_reason: An fr-scoped decline used to prove per-locale filtering of declined_index.
would_change_decision_if: Never relevant to de_AT; this entry must be absent from de_AT output.
---

Per-locale guard: this decline targets fr only and must not appear in de_AT's resolved JSON.
