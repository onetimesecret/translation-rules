# Sign-off review — `Secret Support` & `Workspace` draft glossary targets

Review of the 29-locale draft targets in
[`../2026-07-01/signature-workspace-drafts.md`](../2026-07-01/signature-workspace-drafts.md),
per the 2026-07-02 ruling (translate both by meaning; see
`rules/retrospectives/2026-07-02-signature-brand-vs-translatable.md`).

## Provenance — read this first

**This is a model review (Claude, 2026-07-12), not native-speaker sign-off.**
The native speaker who was to perform sign-off passed away; the maintainer
asked for a model review in substitution. Confidence is high for the major
languages below and is stated per locale; locales where model confidence is
genuinely lower are **flagged for external native validation** rather than
approved. Whether this review satisfies the retro's sign-off gate is the
maintainer's call, recorded by merging the PR that carries it.

## Method

1. **Mechanical distinctness check** (script over the app repo's
   `locales/content/<loc>/email.json`, 2026-07-12): extracted every
   `email.*.signature` rendering per locale and verified each proposed
   "Secret Support" target differs from that locale's generic "Support Team"
   rendering. **All 29 pass.** The extraction also re-confirmed the `vi`
   defect: all 18 generic signatures render as `Delano`.
2. **Design-pattern check:** every target must anchor on the real brand
   ("Onetime Secret", kept English) plus a meaning-rendered support-team
   phrase. **All 29 comply.**
3. **Rule conformance:** `zh` target avoids 秘密 (`rule.zh-secret-no-mimi`);
   `de_AT` target is a noun phrase, no register-lock tokens implicated.
4. **Linguistic review** of grammar, sense, and naturalness per locale,
   against the locale's own generic rendering for register consistency.

## Verdicts — Secret Support

Generic column is the locale's actual merged "Support Team" rendering
(distinctness baseline).

| loc | generic (merged) | proposed target | verdict |
|-----|------------------|-----------------|---------|
| ar | فريق الدعم | فريق دعم Onetime Secret | **approve** — correct iḍāfa; Latin brand tail is standard practice in Arabic product copy |
| bg | Екип за поддръжка | Поддръжка на Onetime Secret | **amend** → **Екип за поддръжка на Onetime Secret** — the draft drops the "team" sense and breaks parallelism with the generic; the amended form keeps both and stays distinct via the anchor |
| ca_ES | Equip de suport | Equip de suport d'Onetime Secret | **approve** |
| cs | Tým podpory | Tým podpory Onetime Secret | **approve** — brand in apposition is natural Czech |
| da_DK | Supportteamet | Onetime Secret-support | **approve** — correct Danish compounding off a multiword name; reads naturally as a sign-off |
| de | Support-Team | Onetime Secret Support-Team | **approve** — strict Duden would fully hyphenate, but open spacing before a brand is standard product-copy German |
| de_AT | Support-Team | Onetime Secret Support-Team | **approve** — same as de; no register-lock interaction |
| el_GR | Ομάδα υποστήριξης | Ομάδα υποστήριξης του Onetime Secret | **approve** — correct genitive article |
| eo | Subtena teamo | Subtena teamo de Onetime Secret | **approve** |
| es | Equipo de soporte | Equipo de soporte de Onetime Secret | **approve** |
| fr_CA | L'équipe de soutien | L'équipe de soutien d'Onetime Secret | **approve** — keeps fr_CA's "soutien" (vs fr_FR "assistance") |
| fr_FR | L'équipe d'assistance | L'équipe d'assistance Onetime Secret | **approve** — brand apposition is fine; "d'Onetime Secret" also acceptable |
| he | צוות התמיכה | צוות התמיכה של Onetime Secret | **approve** — של + Latin brand is standard; fixes the collapse (generic and feedback were byte-identical) |
| hu | Támogatási csapat | Onetime Secret ügyfélszolgálat | **approve** — "ügyfélszolgálat" (customer service) is the idiomatic Hungarian for a product's support desk and is doubly distinct from the generic |
| it_IT | Team di supporto | Team di supporto di Onetime Secret | **approve** |
| ja | サポートチーム | Onetime Secret サポートチーム | **approve** — replaces the シークレット transliteration; spacing correct |
| ko | 지원팀 | Onetime Secret 지원팀 | **approve** |
| mi_NZ | Te Kapa Tautoko | Te Kapa Tautoko o Onetime Secret | **flag — external native validation** (see below) |
| nl | Supportteam | Onetime Secret-supportteam | **approve** — correct Dutch compound hyphenation |
| pl | Zespół pomocy technicznej | Zespół pomocy Onetime Secret | **approve** — grammatical; distinct both by anchor and by dropping "technicznej" |
| pt_BR | Equipe de Suporte | Equipe de Suporte do Onetime Secret | **approve** — masculine article for the brand is right |
| pt_PT | Equipa de Suporte | Equipa de Suporte do Onetime Secret | **approve** |
| ru | Команда поддержки | Служба поддержки Onetime Secret | **approve** — "Служба поддержки" is the idiomatic support-desk term; doubly distinct from the generic "Команда поддержки" |
| sl_SI | Ekipa za podporo | Ekipa za podporo Onetime Secret | **approve** — anchor restores the distinction the collapse erased |
| sv_SE | Supportteamet | Onetime Secret-supporten | **approve** — correct compounding and definite form |
| tr | Destek Ekibi | Onetime Secret Destek Ekibi | **approve** — anchor restores the erased distinction |
| uk | Служба підтримки | Служба підтримки Onetime Secret | **approve** — replaces the dangling English "Secret" fragment |
| vi | Delano *(defect)* | Đội ngũ hỗ trợ Onetime Secret | **approve** — but the same pass MUST fix the 18 generic `Delano` signatures (→ Đội ngũ hỗ trợ); approving the feedback key alone leaves the worse defect standing |
| zh | 支持团队 | Onetime Secret 支持团队 | **approve** — avoids 秘密 per `rule.zh-secret-no-mimi` |

**Tally: 27 approve, 1 amend (bg), 1 flag (mi_NZ).**

## Verdicts — Workspace

All 29 proposed targets are standard, idiomatic renderings; **approve all**,
with three notes:

- **mi_NZ "Wāhi Mahi"** is included in the external-validation flag below
  ("wāhi mahi" is literally *workplace*; plausible for a virtual workspace,
  but this is exactly the calque risk a native speaker should confirm).
- **ja ワークスペース** is the one deliberate loanword; correct call — it is
  the established Japanese term for a software workspace.
- **Capitalization is inconsistent across the table** (es/pl/sl_SI lowercase,
  others title-case). That is not wrong — those are sentence-case locales —
  but the glossary entries should state the target in nav-label form
  (first-letter capitalized: "Espacio de trabajo", "Przestrzeń robocza",
  "Delovni prostor") with prose-context lowercase left to the locale's
  ordinary casing rules, so the footer/nav reconciliation has one canonical
  form to converge on.

## Flagged for external native validation

- **mi_NZ (both terms).** Model confidence in te reo Māori is low.
  Specific questions for a validator: (a) is "kapa" right for a support
  *team* here, or is "rōpū tautoko" more natural? — note the generic
  signatures already use "Te Kapa Tautoko", so changing the noun would need
  a consistency pass; (b) is "o Onetime Secret" the right possessive
  particle (o vs. ā/a category) for a team belonging to a product?;
  (c) "Wāhi Mahi" for a virtual workspace. Until validated, encode the
  mi_NZ glossary entries with the drafts as-is but mark them
  `confidence: low` / pending-validation in the rationale, or hold mi_NZ
  out of the first encoding PR.

## What this unblocks

With this review standing in for sign-off (maintainer's acceptance = merging
the PR that carries it):

1. Encode `term.secret-support` and `term.workspace` glossary entries across
   the 29 locale glossaries (bg amended; mi_NZ per the flag above), with
   `key_patterns`, idiomatic-meaning `rationale`, and the per-locale `bad`
   examples from the drafts file.
2. Content-correction PR(s) in onetimesecret: 29 × `email.feedback_email.signature`,
   the `vi` Delano repair (18 keys), and the `web.footer.workspace`
   reconciliation (da_DK, de, de_AT, el_GR, it_IT, nl, pt_BR, tr).
3. Flip retro `2026-07-02-signature-brand-vs-translatable` to `applied` in
   the closing PR and drop its grace waiver.

## Findings manifest

- Sign-off review of the 29-locale Secret Support / Workspace draft targets:
  27 approve, bg amended, mi_NZ flagged for external native validation.
  Model review in substitution for native-speaker sign-off (provenance above).
  retro: 2026-07-02-signature-brand-vs-translatable
- `vi` generic signatures re-confirmed as `Delano` on 18 keys (2026-07-12
  extraction); repair is in scope for the content-correction pass.
  retro: 2026-07-02-signature-brand-vs-translatable
