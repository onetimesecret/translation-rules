---
id: 2026-04-12-de_AT-register-flip
date: 2026-04-12
status: applied
triggered_by:
  commits: [b08e59838, 4982d4f84, 44b3c3352]
  incident: "de_AT formal→informal register flip; Sie/Ihre replaced by du/dein across email, session-auth, and UI strings"
affected_locales: [de_AT]
affected_rules: [register.de_AT.formality]
examples_added: []
baseline_pins: [baselines.de_AT]
resolved_in_commit: 8cf0e22
supersedes: []
declined_reason: null
would_change_decision_if: null
---

# 2026-04-12 — de_AT register flip

## What happened

Between January and April 2026 the de_AT app locale drifted from formal `Sie`
to informal `du`. The harmonization commit `b08e59838` cemented the flip:
`Geheimnis` was zeroed out (108 → 0), `Nachricht` more than tripled (65 →
201), and every `Sie/Ihre` in email and session-auth content was rewritten as
`du/dein`. Three other locales — `pt_PT`, `uk`, `hu` — were contaminated by
the same harmonization wave. `da_DK` and `zh` saw lighter brand-term and
formal-pronoun damage.

Full evidence — concrete pre/post examples, baseline SHAs, the per-locale
spread table, and the pipeline finding — lives in
[`reviews/2026-04-12/`](../reviews/2026-04-12/), particularly
[`cross-locale-audit.md`](../reviews/2026-04-12/cross-locale-audit.md) and
[`locale-quality-analysis-de_AT.md`](../reviews/2026-04-12/locale-quality-analysis-de_AT.md).
This retrospective does not duplicate that content; it carries the structured
metadata and the rule change.

## Root cause

A descriptive change-log was promoted to prescriptive guidance. `de-translation-notes.txt`
was a conversational transcript explaining what an assistant did to the `de`
(Germany) locale — including a passage about consolidating partial DE strings
on the informal `du`. That transcript was copy-pasted into
`docs.onetimesecret.com`'s `language-notes.md` without regional tagging.
Five months later, harmonization agents reading the corrupted guide for de_AT
followed the only literal signals available — the `du`-form examples — and
flipped Austria's formal register downward.

The November 2025 QA review of the `de` docs locale (`reviews/2025-11-16/`)
already named this pattern and recommended formal `Sie`. Its findings never
landed back in `language-notes.md`. The April 2026 regression is the
recurrence the November review effectively predicted.

The deeper failure is structural: the rule system had no machine-readable
landing zone for QA findings. Insights died in prose, prose drifted, and
agents treated the change-log as guidance because nothing else was
authoritative.

## Rule change

`locales/de_AT/register.yaml` (this PR) locks de_AT as `form: formal`,
`pronoun: Sie`, with forbidden tokens `[du, dein, deine, deinen, deinem,
deiner, dich, dir, euch, euer]`. `bin/lint-register` provides the grep-level
enforcement that would have caught `b08e59838` at PR time.

This retrospective opens with `status: applied` because it is the first
record in the system and the rule change ships in the same PR. Future
retrospectives enter as `pending` and follow the lifecycle in
[`README.md`](README.md).

## Sibling locales

`pt_PT`, `uk`, and `hu` were also contaminated. They are explicitly **not**
in Phase 0 scope — register lock for those locales requires per-locale
forbidden-token research and native-speaker review, deferred to the
knowledge-base population phase per [`BACKLOG.md`](../BACKLOG.md). The
de_AT lock is the structural proof-of-concept; the others follow once the
foundational system is observed working.

## Pipeline finding

The app repo's `locales/guides/for-translators/<locale>.md` files are a
one-shot 2026-01-20 bootstrap from the docs project, not a live sync.
Fixing the docs guide does not auto-propagate. Phase 1's resolver-emitted
artifacts and the cross-repo CI gate (SPEC §2.4) are the mechanical fix.
Phase 0 does not address this directly; the retrospective records it so the
finding cannot be lost.
