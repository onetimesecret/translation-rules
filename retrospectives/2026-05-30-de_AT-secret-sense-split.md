---
id: 2026-05-30-de_AT-secret-sense-split
date: 2026-05-30
status: applied
triggered_by:
  commits: [b08e59838]
  incident: "de_AT 'secret' sense-collapse: the secret object (Geheimnis) was zeroed (108 → 0) and merged into the payload term (Nachricht, 65 → 201) by the 2026-04-12 harmonization, erasing the object/payload distinction in the locale"
affected_locales: [de_AT]
affected_rules: []
examples_added: ["ex.secret-created#e4355c4f", "ex.secret-genitive#cb21d6c1", "ex.secret-informal#40c23f2d", "ex.message-enter#9a4a3f91", "ex.message-informal#78142c00"]
baseline_pins: [baselines.de_AT]
resolved_in_commit: 47d4741
supersedes: []
declined_reason: null
would_change_decision_if: null
---

# 2026-05-30 — de_AT "secret" object/payload sense-split

## What happened

The 2026-04-12 incident had two distinct findings. The
[register-flip retrospective](2026-04-12-de_AT-register-flip.md) carries the
formality finding (`Sie` → `du`) and locks `register.de_AT.formality`. This
retrospective carries the **second** finding from the same harmonization
wave: the English word *secret* collapsed onto a single German term.

The harmonization commit `b08e59838` zeroed `Geheimnis` (108 → 0) and more
than tripled `Nachricht` (65 → 201). Both German words had been doing
distinct jobs — `Geheimnis` for the protected *object* (the thing created,
shared, burned, expired) and `Nachricht` for the *payload* (the message
content the user typed). After harmonization, de_AT had one word where the
product model has two concepts. The evidence is in
[`reviews/2026-04-12/locale-quality-analysis-de_AT.md`](../reviews/2026-04-12/locale-quality-analysis-de_AT.md);
this retrospective does not duplicate it.

## Root cause

Same structural root as the formality flip — a prose guide that fed agents a
single literal signal — but a *different* missing artifact. There was no
machine-readable record that "secret" carries two senses in this product.
The glossary prose listed one gloss per term, so a harmonizer minimizing
key-level variance had no reason to preserve two German words for one English
one. The distinction lived only in a human translator's head; once that
translator was an agent reading a flat gloss, the distinction was lost.

## What changed

`locales/de_AT/glossary.yaml` (commit `47d4741`) splits *secret* into two
terms, each with a machine-checkable disambiguation surface:

- **`term.secret_object#c0902808`** → `Geheimnis`. Disambiguated by lifecycle
  verbs and key patterns `["*secret*", "*.burn*", "*.share*", "*.expire*"]`.
- **`term.secret_payload#1687a617`** → `Nachricht`. Disambiguated by
  input/compose context and key patterns `["*.message*", "*.content*", "*.body*"]`.

Five worked examples ship with them (`examples_added`). Three are `good`
anchors — including a genitive inflection (`des Geheimnisses`) proving the
match survives morphology — and **two are deliberately `bad`**
(`ex.secret-informal`, `ex.message-informal`): they reproduce the original
register flip inside the example set so the anti-pattern is testable, not just
described.

The disambiguation `key_patterns` are the enforcement surface a lint can run
against locale content: "secret" under a `*.burn*`/`*.share*` key that
resolves to `Nachricht` is now a flaggable mismatch. That is the mechanical
defense the flat gloss never had.

**Caveat:** the de_AT targets are agent-authored and carry a native-speaker
(AT) sign-off requirement before they are treated as authoritative — see the
header note in `glossary.yaml` and the PR label. This retrospective records
the structural fix; the linguistic sign-off is tracked separately.

## Learnings

**Carry forward (good):**
- *Two concepts, two terms — encoded, not implied.* Where one source word maps
  to multiple target words, the split belongs in the glossary as separate
  terms with disambiguation, so the distinction survives an agent that reads
  only the data.
- *Ship the anti-pattern as a `bad` example.* Including the exact failing
  string as a `verdict: bad` example turns "don't do this" from prose into a
  fixture a reviewer or lint can check against.
- *Disambiguation by key pattern is enforceable.* Heuristics phrased as
  `key_patterns` give the resolver/lint a concrete hook, unlike free-text
  guidance.

**Prevent (avoid):**
- *Never let "harmonize" minimize term variance.* Collapsing two valid target
  words to one to reduce key-level diff is the failure that produced this
  finding. Structural harmonization is keys-only (SPEC Phase 0 §1); meaning is
  off-limits to it.
- *Don't trust a single gloss per term for polysemous source words.* A flat
  one-line gloss is exactly what let the senses merge.

## Why `affected_rules` is empty

This closure is structural, not a rule edit — the same case as the
[2026-04-26 conventions-drift retro](2026-04-26-start-translation-session-conventions-drift.md).
The fix is the glossary terms and examples (uuid-form ids in `examples_added`),
not a change to any dotted rule. The terms *reference* `register.de_AT.formality`
and `rule.terminology-consistency`, but they do not modify them, so neither
belongs in `affected_rules` — which per SPEC §3 records only ids the closing
PR *touches*.

Do **not** add a dotted glossary rule here. As the 2026-04-26 retro notes, the
resolver requires every `affected_rule` to resolve in every `affected_locale`;
a sense-split is a per-locale lexical fact already fully expressed by the term
entries' disambiguation, so a separate rule would add a resolver obligation
without adding enforcement the `key_patterns` don't already provide.

## Relationship to 2026-04-12

This is the glossary sibling of the register-flip retro: same incident, same
harmonization commit, distinct finding, distinct fix dated when the
disambiguation actually landed (`47d4741`, 2026-05-30). Splitting them keeps
each finding independently auditable and each fix traceable to its own commit.
