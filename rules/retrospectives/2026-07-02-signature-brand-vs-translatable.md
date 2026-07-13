---
id: 2026-07-02-signature-brand-vs-translatable
date: 2026-07-02
status: pending
triggered_by:
  commits: []
  incident: "email.*.signature support-team labels ('Secret Support' and the generic 'Support Team' family) were handled contradictorily across the 2026-07-01 parallel review wave — 11 locales kept English, 18 translated — because no glossary term or rule decided whether these labels are untranslatable brand names or translatable copy; 'Workspace' exhibits the same undecided class"
affected_locales:
  [
    ar,
    bg,
    ca_ES,
    cs,
    da_DK,
    de,
    de_AT,
    el_GR,
    eo,
    es,
    fr_CA,
    fr_FR,
    he,
    hu,
    it_IT,
    ja,
    ko,
    mi_NZ,
    nl,
    pl,
    pt_BR,
    pt_PT,
    ru,
    sl_SI,
    sv_SE,
    tr,
    uk,
    vi,
    zh,
  ]
affected_rules: []
examples_added: []
baseline_pins: []
resolved_in_commit: null
supersedes: []
declined_reason: null
would_change_decision_if: null
---

# 2026-07-02 — signature labels: brand name or translatable copy?

## What happened

During the 2026-07-01 parallel review/translation wave, ~29 independent agents
each made an isolated call on the email support-signature strings and
disagreed. The clearest key is `email.feedback_email.signature`, whose English
source is **"Secret Support"** (a string the en source deliberately marks
distinct from the 20 generic `Support Team` signatures via a separate
`content_hash`: `f6a6c90f` vs `dc75bf9f`). On merged main the 29 locales
carrying that key split **11 keep English / 18 translate** — an inconsistency no
authority resolved. `Workspace` is the same class of failure: the nav label
`web.layout.workspace` is translated nearly everywhere, but the footer label
`web.footer.workspace` and prose keep the English loanword in several locales,
with `pt_BR`/`it_IT` internally split, and **no glossary term anywhere decides
it** (`grep workspace rules/locales/*/glossary.yaml` → 0 hits).

The raw evidence is the batch log at
[`../../_references/reviews/2026-07-01/batch-operations-log.md`](../../_references/reviews/2026-07-01/batch-operations-log.md)
(and its `-analysis.md` sibling); this retrospective does not duplicate it. The
log even contradicts itself: one agent's C6 conclusion (log line 73 — "leaving
as-is, roughly half keep literal Secret Support") was silently overridden by
other agents who translated `he`, `sl_SI`, `sv_SE`, `tr` (log lines 173, 306,
315, 330). That agent-by-agent divergence, with no shared ruling enforced, is
the mechanical cause of the 11-vs-18 split.

## Current state — `email.feedback_email.signature` (the harmonization payload)

en source (`en/email.json:362`) = **"Secret Support"** (`content_hash f6a6c90f`),
a brand-distinct string from the generic "Support Team" signatures. All non-en
values below are at `<loc>/email.json:317`. `fr/` carries no `email.json`, so 29
locales carry the key.

**English-verbatim "Secret Support" (11):**

| locale                                                 | value                        |
| ------------------------------------------------------ | ---------------------------- |
| ca_ES, cs, da_DK, de, de_AT, hu, it_IT, ko, nl, ru, zh | `Secret Support` (unchanged) |

**Translated / localized (18):**

| locale | value                   | note                                                                       |
| ------ | ----------------------- | -------------------------------------------------------------------------- |
| ar     | دعم الأسرار               | full translation                                                           |
| bg     | Поддръжка на тайни      | full translation                                                           |
| el_GR  | Υποστήριξη μυστικών     | full translation                                                           |
| eo     | Sekreta Subteno         | full translation — **contradicts** its own translator guide (see below)    |
| es     | Soporte Secreto         | full translation                                                           |
| fr_CA  | Soutien aux secrets     | full translation                                                           |
| fr_FR  | Support des secrets     | full translation                                                           |
| he     | צוות התמיכה            | **brand-erasing** — byte-identical to its generic "Support Team" rendering |
| ja     | シークレットサポート    | katakana transliteration                                                   |
| mi_NZ  | Tautoko Huna            | full translation                                                           |
| pl     | Wsparcie Secret         | partial — keeps English "Secret"                                           |
| pt_BR  | Suporte Secret          | partial — keeps English "Secret"                                           |
| pt_PT  | Suporte Secret          | partial — keeps English "Secret"                                           |
| sl_SI  | Ekipa za podporo        | **brand-erasing** — collapses to its generic "Support Team" rendering      |
| sv_SE  | Hemlig Support          | partial — keeps English "Support"                                          |
| tr     | Destek Ekibi            | **brand-erasing** — collapses to its generic "Support Team" rendering      |
| uk     | Служба підтримки Secret | partial — keeps English "Secret"                                           |
| vi     | Hỗ trợ bí mật           | full translation                                                           |

Two corrections to the secondhand claim that seeded this review:

- **The "left English in ar, da_DK, es, pt_PT" list is stale.** Only `da_DK` of
  those four is still English on merged main; `ar`, `es`, `pt_PT` were
  translated by later agents after the log entry was written.
- **`email.expiration_warning.signature` is mis-scoped and out of scope here.**
  Its en source is "Support Team" (`dc75bf9f`), not "Secret Support"; the
  `mi_NZ` fix there was a within-"Support Team" consistency fix, unrelated to
  the brand question. Across all 20 "Support Team" signature keys, no locale
  leaves verbatim English.

## Root cause

Same structural root as the [de_AT sense-split](2026-05-30-de_AT-secret-sense-split.md):
a fact that belongs in the authority lived only in prose (and in each agent's
head), so parallel agents re-derived it and disagreed. Specifically:

- **No glossary term and no binding rule decides these labels.** `rule.terminology-consistency`
  (base.yaml, MUST/error) says "use the glossary's chosen term consistently" —
  but there is **no glossary term** for "Secret Support" or "Workspace" for it
  to enforce against, so it has nothing to bite on.
- **The prose authority disagrees with the merged tree.**
  [`../../_references/local-guides/UX-TRANSLATION-GUIDE.md`](../../_references/local-guides/UX-TRANSLATION-GUIDE.md)
  §"Brand Names (Do Not Translate)" (lines 283–291) lists "**Secret Support** —
  Support team name (used in email signatures)" as MUST-stay-English (line 288),
  and the per-locale guide
  [`../../_references/local-guides/for-translators/eo.md`](../../_references/local-guides/for-translators/eo.md)
  line 137 repeats "Keep in English (email signature, brand name)". Yet `eo`'s
  own merged content translated it to "Sekreta Subteno" — the guide and the
  content directly contradict each other. Under the guide's rule the 11 English
  locales are correct and the 18 translated ones violate it; that is the inverse
  of how the wave actually behaved.
- **Parallel-agent coordination gap.** C6 needed a single brand-name ruling
  applied batch-wide, not 29 independent per-agent judgments. The "follow the
  majority" heuristic produced a moving target as the majority itself shifted
  mid-wave.

## Decision (2026-07-02, maintainer)

**Ruled: Direction A — translate both "Secret Support" and "Workspace" by
meaning, not literally.** "Secret Support" is not a brand name; it fails the
cross-surface anchor test now recorded in
[`../../docs/terminology.md`](../../docs/terminology.md). The brand-list entries
were removed from
[`../../_references/local-guides/UX-TRANSLATION-GUIDE.md`](../../_references/local-guides/UX-TRANSLATION-GUIDE.md)
and `for-translators/eo.md` in this same change. Both terms are to be encoded as
translatable glossary terms with idiomatic-meaning targets and `good`/`bad`
examples — the `bad` examples being the partial "keep-Secret" renders
(`Suporte Secret`, `Wsparcie Secret`) and the collapse onto the generic
"Support Team" rendering (he, sl_SI, tr). Poor existing translations are in
scope to fix, not grandfathered — see
[`../../docs/scope-and-ownership.md`](../../docs/scope-and-ownership.md).

Status stays `pending` until the glossary terms, guide edits, and per-locale
content corrections land in a merged commit; the closing PR flips it to
`applied` and populates `resolved_in_commit`.

## What must change

The engineering fix encodes the decision once, in machine-readable form, so no
agent re-derives it. Two things to reconcile:

1. **Decide the class of the support-signature labels ("Secret Support"), then
   encode it as a glossary term** (uuid-form `term.*#<8hex>`), disambiguated by
   `key_patterns` matching `email.*.signature` / `email.feedback_email.signature`,
   so `rule.terminology-consistency` finally has something to enforce:
   - **Direction A (recommended, not decided): translatable support-team label.**
     Demote "Secret Support" from brand-name status, add a translatable glossary
     term with a per-locale target, and translate consistently across all 29.
     This matches how 18/29 locales already behaved and how translators plainly
     _read_ the string (the partial and brand-erasing renders show they do not
     perceive a locked brand). It requires editing `UX-TRANSLATION-GUIDE.md:288`
     and `for-translators/eo.md:137` to drop it from the brand list.
   - **Direction B: keep-English brand name.** Add a glossary brand-name term
     with an explicit keep-English decision and revert the 18 translated locales
     to "Secret Support". This is what the _current_ documented authority says
     (`UX-TRANSLATION-GUIDE.md:288`), so it is the smaller doc change but the
     larger content revert.

   The recommendation leans **Direction A** — it is a support-_team_ label, not
   a product/company brand like "Onetime Secret", and the merged tree already
   trends that way — but the authority currently asserts the opposite, so the
   maintainer must pick and the two can not both stand.

2. **Decide "Workspace" (maintainer call, genuinely open).** No authority
   decides it today. Add a `Workspace` glossary term (per-locale or base) that
   picks translate-vs-loanword per locale, then reconcile `web.footer.workspace`
   and prose to match `web.layout.workspace`. There is no documented rule
   pointing either way here, so this is a fresh decision, not a contradiction to
   resolve.

An **optional base-rule clarification** the maintainer may also want: state, in
or alongside `rule.brand-names-untranslated`, that the enumerated brand list is
the authority and that "support-team signature labels are/are not brands" — so
the next wave has a rule to cite instead of prose. This retro does **not**
assume that edit (see below).

## Learnings

**Carry forward (good):**

- _One decision, encoded once._ Where a single source label's translate-vs-keep
  status is contested, the ruling belongs in a glossary term with `key_patterns`,
  not in prose guides that agents read inconsistently — the same lesson as the
  de_AT sense-split.
- _The source's `content_hash` already flags the distinction._ en marks
  "Secret Support" (`f6a6c90f`) as a different string from the generic
  "Support Team" (`dc75bf9f`); tooling can key off that to detect signature
  keys that need a brand ruling.

**Prevent (avoid):**

- _Never resolve a brand/terminology question by per-agent majority vote._ The
  "follow the majority" heuristic (log line 73) produced a moving target and the
  11-vs-18 split. Brand-name calls must be decided in the authority and applied
  batch-wide before the wave, not re-litigated per locale.
- _Never let guide and content diverge silently._ `eo.md:137` says keep English;
  `eo` content translated it. A rule that lives only in prose, with no
  glossary term or lint behind it, will be ignored under parallel load.

## Why `affected_rules` is empty

Per the exemplar and the resolver invariant (every `affected_rule` must resolve
in every `affected_locale`, and SPEC §3 records only ids the _closing PR
touches_), this stays `[]`.

- **`rule.terminology-consistency`** is already correct as written — the fix
  _supplies it a term to enforce_, it does not edit the rule. Not touched.
- **`rule.brand-names-untranslated`** is the near-miss. Under **Direction A**
  the label is explicitly _not_ a brand, so the rule is untouched. Under
  **Direction B** the cleanest encoding is still a glossary brand-name term
  (the rule's inline list is illustrative, and brand names are enumerated in
  glossaries, not in the rule statement), so the base rule remains untouched
  there too. In **both** plausible directions the enforcement surface is a
  glossary term plus guide/content reconciliation — not a YAML edit to either
  base rule.

**Apply-time caveat.** If the maintainer chooses to encode the brand decision
by amending the enumerated statement of `rule.brand-names-untranslated` itself
(rather than via a glossary term), the closing PR _does_ touch that rule and
must add `rule.brand-names-untranslated` to `affected_rules` at that point. As
filed, no such edit is assumed, so the list is empty.

## Out of scope (spun off, do not lose)

Surfaced by the same signature enumeration but not part of this incident; file
as separate source-issues:

- **`vi` = "Delano" on all 20 generic "Support Team" signature keys** — the
  founder's name shipped as the support signature across `vi`'s non-feedback
  signatures (its `feedback_email.signature` is separately fine). Replace with a
  proper Vietnamese "Support Team" rendering.
