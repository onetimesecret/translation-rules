# Draft glossary targets — `Secret Support` & `Workspace` (2026-07-02)

Agent-authored first-pass targets from the 29-locale fan-out (`encode-signature-workspace-terms`), per the 2026-07-02 ruling: **translate both by meaning** (see `docs/terminology.md`, `rules/retrospectives/2026-07-02-signature-brand-vs-translatable.md`).

**Status: DRAFT — every locale requires native-speaker sign-off before it lands in a glossary.** Nothing here is written to `rules/locales/*/glossary.yaml` yet.

## Design pattern (consistent across all 29)

`Secret Support` → **`Onetime Secret` (real brand, kept) + locale word for "support team" (translated by meaning)**. Anchoring on the brand is what keeps this sign-off DISTINCT from the generic `Support Team` signature, which the English source separates via its own `content_hash` — so the anchor is not decorative, it preserves the source distinction.

## Secret Support

| loc | current (merged main) | defect | proposed target | conf |
|-----|-----------------------|--------|-----------------|------|
| ar | دعم الأسرار | other | **فريق دعم Onetime Secret** | medium |
| bg | Поддръжка на тайни | other | **Поддръжка на Onetime Secret** | medium |
| ca_ES | Secret Support | english | **Equip de suport d'Onetime Secret** | high |
| cs | Secret Support | english | **Tým podpory Onetime Secret** | high |
| da_DK | Secret Support | english | **Onetime Secret-support** | medium |
| de | Secret Support | english | **Onetime Secret Support-Team** | medium |
| de_AT | Secret Support | english | **Onetime Secret Support-Team** | medium |
| el_GR | Υποστήριξη μυστικών | other | **Ομάδα υποστήριξης του Onetime Secret** | high |
| eo | Sekreta Subteno | other | **Subtena teamo de Onetime Secret** | medium |
| es | Soporte Secreto | other | **Equipo de soporte de Onetime Secret** | high |
| fr_CA | Soutien aux secrets | other | **L'équipe de soutien d'Onetime Secret** | medium |
| fr_FR | Support des secrets | acceptable | **L'équipe d'assistance Onetime Secret** | medium |
| he | צוות התמיכה | collapsed | **צוות התמיכה של Onetime Secret** | high |
| hu | Secret Support | english | **Onetime Secret ügyfélszolgálat** | medium |
| it_IT | Secret Support | english | **Team di supporto di Onetime Secret** | high |
| ja | シークレットサポート | transliteration | **Onetime Secret サポートチーム** | medium |
| ko | Secret Support | english | **Onetime Secret 지원팀** | medium |
| mi_NZ | Tautoko Huna | other | **Te Kapa Tautoko o Onetime Secret** | medium |
| nl | Secret Support | english | **Onetime Secret-supportteam** | medium |
| pl | Wsparcie Secret | partial | **Zespół pomocy Onetime Secret** | high |
| pt_BR | Suporte Secret | partial | **Equipe de Suporte do Onetime Secret** | medium |
| pt_PT | Suporte Secret | partial | **Equipa de Suporte do Onetime Secret** | high |
| ru | Secret Support | english | **Служба поддержки Onetime Secret** | medium |
| sl_SI | Ekipa za podporo | collapsed | **Ekipa za podporo Onetime Secret** | medium |
| sv_SE | Hemlig Support | partial | **Onetime Secret-supporten** | medium |
| tr | Destek Ekibi | collapsed | **Onetime Secret Destek Ekibi** | high |
| uk | Служба підтримки Secret | partial | **Служба підтримки Onetime Secret** | high |
| vi | Hỗ trợ bí mật | other | **Đội ngũ hỗ trợ Onetime Secret** | medium |
| zh | Secret Support | english | **Onetime Secret 支持团队** | high |

## Workspace

| loc | proposed target | loanword | note |
|-----|-----------------|----------|------|
| ar | **مساحة العمل** | no |  |
| bg | **Работно пространство** | no |  |
| ca_ES | **Espai de treball** | no |  |
| cs | **Pracovní prostor** | no |  |
| da_DK | **Arbejdsområde** | no | footer.workspace still English |
| de | **Arbeitsbereich** | no | footer.workspace still English |
| de_AT | **Arbeitsbereich** | no | footer.workspace still English |
| el_GR | **Χώρος εργασίας** | no | footer.workspace still English |
| eo | **Laborspaco** | no |  |
| es | **espacio de trabajo** | no |  |
| fr_CA | **Espace de travail** | no |  |
| fr_FR | **Espace de travail** | no |  |
| he | **סביבת עבודה** | no |  |
| hu | **Munkaterület** | no |  |
| it_IT | **Area di lavoro** | no | footer.workspace still English |
| ja | **ワークスペース** | yes |  |
| ko | **작업 공간** | no |  |
| mi_NZ | **Wāhi Mahi** | no |  |
| nl | **Werkruimte** | no | footer.workspace still English |
| pl | **przestrzeń robocza** | no |  |
| pt_BR | **Área de Trabalho** | no | footer.workspace still English |
| pt_PT | **Espaço de trabalho** | no |  |
| ru | **Рабочее пространство** | no |  |
| sl_SI | **delovni prostor** | no |  |
| sv_SE | **Arbetsyta** | no |  |
| tr | **Çalışma Alanı** | no | footer.workspace still English |
| uk | **Робоча область** | no |  |
| vi | **Không gian làm việc** | no |  |
| zh | **工作区** | no |  |

## Bad-examples to encode (the wrong renders, per locale)

| loc | avoid | why |
|-----|-------|-----|
| ar | دعم الأسرار | Iḍāfa "دعم الأسرار" = "support of the secrets" — it ties the sign-off to the domain noun أسرار (a secrets-support/feature reading) instead of naming the product's support team; a m |
| bg | Поддръжка на тайни | Translates the brand-shorthand "Secret" as the тайна domain noun (plural тайни), so a bg reader parses it as "support for the secret objects" rather than "the Onetime Secret suppor |
| ca_ES | Secret Support | Untranslated English leak (current merged value). Also avoid the partial 'Suport Secret' (keeps English 'Secret') and avoid collapsing onto the bare generic 'Equip de suport' (that |
| cs | Secret Support | Left untranslated in English. It also must not become the partial 'Podpora Secret' (keeps the English word 'Secret'), nor collapse to the bare generic 'Tým podpory' used by the ~20 |
| da_DK | Secret Support | Left fully in English/untranslated — keeps the word 'Secret'. Also avoid the partial 'Secret-support' (still keeps 'Secret') and avoid collapsing onto the generic 'Supportteamet',  |
| de | Secret Support | Leaves the sign-off fully English (current defect). Also WRONG: partials that keep the standalone word 'Secret' ('Secret-Support', 'Support Secret'); a literal transliteration; and |
| de_AT | Secret Support | Untranslated English that keeps the word 'Secret'; also avoid the partial 'Secret-Support' and avoid collapsing onto the generic 'Support-Team' (that erases the source's deliberate |
| el_GR | Υποστήριξη μυστικών | Word-for-word 'support of secrets' — μυστικών (genitive plural of μυστικό) reframes the product-brand 'Secret' as the ordinary noun 'secrets', so it reads as a helpdesk FOR secrets |
| eo | Sekreta Subteno | Wrong sense: 'Sekreta' is the adjective secret/confidential, so the phrase reads 'confidential support' rather than naming the product's support team. Also must NOT collapse to the |
| es | Soporte Secreto | Literal word-for-word render: "Secreto" functions as an adjective meaning clandestine/hidden support, so it reads as "secret (covert) support" rather than referencing the Onetime S |
| fr_CA | Soutien aux secrets | Wrong-sense literal: reads as 'support for/about secrets', reframing the product word 'Secret' as a common-noun object and dropping the 'team' sense. Also avoid the partial 'Soutie |
| fr_FR | L'équipe d'assistance | Collapsing onto the generic Support Team sign-off (fr_FR renders 'Support Team' as 'L'équipe d'assistance' in email.welcome/email.expiration_warning) erases the source's deliberate |
| he | צוות התמיכה | Byte-identical to the ~20 generic 'Support Team' signatures in email.json (all render צוות התמיכה), so it collapses the source's deliberate distinction. Also wrong: partials keepin |
| hu | Secret Support | Current value is an untranslated English leak. Also avoid: (a) partials that keep 'Secret' — 'Secret ügyfélszolgálat' / 'Secret támogatás'; (b) collapsing onto the generic 'Support |
| it_IT | Secret Support | Current value is untranslated English and keeps the word 'Secret'. Also wrong: the partial 'Supporto Secret' (still keeps 'Secret'); collapsing onto the plain generic 'Team di supp |
| ja | シークレットサポート | Katakana transliteration of 'Secret Support' — it phonetically keeps 'Secret' as シークレット instead of rendering the meaning, and reads as 'concealed/secret support' rather than 'the O |
| ko | Secret Support | Untranslated English (the current value) — leaves 'Secret Support' verbatim. Also wrong: 시크릿 서포트 (katakana-style transliteration, banned) and bare 지원팀 (collapses onto the generic S |
| mi_NZ | Tautoko Huna | Literal word-for-word calque: translates "Secret"->huna (hidden adjective) and "Support"->tautoko, yielding "Hidden/Concealed Support" — misreads the source (the product's support  |
| nl | Secret Support | Current merged value is left in English (untranslated). Also wrong: bare 'Supportteam' (collapses onto the 20 generic email.*.signature sigs, erasing the deliberate distinction), ' |
| pl | Wsparcie Secret | Keeps the English word 'Secret' as a bare, meaningless brand fragment (a partial); reads as a truncated product name, not as a support team, and mixes Polish 'Wsparcie' with untran |
| pt_BR | Suporte Secret | Wrong: keeps the English word "Secret" (a partial), and "Suporte Secret" does not read as a support-team sign-off in pt-BR — it looks like a stray brand fragment. Also avoid bare " |
| pt_PT | Suporte Secret | The current value keeps the bare English word 'Secret' grafted onto Portuguese 'Suporte'. It reads as a broken half-translation, not a real team name, and 'Suporte Secret' is not t |
| ru | Secret Support | Left in English (untranslated) — the current defective value. Also wrong: the partial «Поддержка Secret» (keeps the English word Secret), a transliteration «Секрет Саппорт» / «Сикр |
| sl_SI | Ekipa za podporo | Byte-identical to all ~20 generic 'Support Team' signatures in the same email.json (each also 'Ekipa za podporo'), so it erases the source's deliberate distinction — this is the co |
| sv_SE | Hemlig Support | Wrong: 'Hemlig' renders the brand anchor 'Secret' as the Swedish adjective 'hemlig' (secret/confidential), so the sign-off reads as 'confidential support' rather than 'the Onetime  |
| tr | Destek Ekibi | "Destek Ekibi" alone is exactly how all 20+ generic "Support Team" signatures render in tr email.json (source_hash f58154f7), so it collapses the source's deliberate distinction. A |
| uk | Служба підтримки Secret | Leaves the orphaned English word "Secret" dangling after a Ukrainian head noun — reads as a half-translated fragment, not a name. "Secret" alone is not the brand; the brand is "One |
| vi | Hỗ trợ bí mật | Current value; a literal 'secret + support' calque that reads 'confidential support', misreads the brand word 'Secret' as the common noun 'bí mật', and drops 'team' — so it does no |
| zh | Secret Support | Leaving "Secret Support" in English is an untranslated leak (defect). Also wrong: literal/transliterated 秘密支持 (uses the app-banned 秘密 term, rule.zh-secret-no-mimi) and the collapse |
