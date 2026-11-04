# Translation report 2026-11-04 (fr; de and es skipped)

The run's own report step failed to write (see "Write failure"), so this report was assembled afterwards from the run summary (`artifacts/run-1-fr-strict-summary.json`) and the follow-up work in onetimesecret/onetimesecret.com#275.

## 1. Headline

| Locale | Result |
|---|---|
| fr | 17 UI keys approved, all unchanged values (brand names, cognates). `security.md` approved as a full retranslation, written by hand afterwards (eb07836b). |
| de | Skipped: register conflict under `registerPolicy: "strict"`. Rerun with `"file"`, see `website-translation-de-es.md`. |
| es | Skipped: register conflict under `registerPolicy: "strict"`. Rerun with `"file"`, see `website-translation-de-es.md`. |

- Gates: key parity OK (396 keys in each locale), `i18n:scan` 56 rows = baseline, unit tests pass. The gate ran before `security.md` was written, so it did not cover the page. A later `pnpm check` and `pnpm build` did.
- Two fr UI edits made by hand before the run were committed separately (c5d6876f): `web.useCases.itdevops.title` "Informatique et DevOps", `web.footer.links.changelog` "Journal des modifications".

## 2. Register conflict (de, es)

Governance declares informal for both (rule.register-lock, MUST). The scout counted the website UI as formal: de 168 formal / 0 informal, es 50 formal / 12 informal. Prose varies by page: `about.md` informal, `accessibility.md` formal, `security.md` no hits. The counts are heuristic: de `Sie` includes some third-person uses, es `su/sus` includes third-person possessives.

Governance is deliberate: c930872 (2026-06-22) flipped de to du per maintainer decision, and the de and es `register.yaml` headers base the informal lock on the app content. The maintainer decided on 2026-11-04 to keep the website formal and leave governance unchanged.

## 3. Write failure

The approved `fr/security.md` and this report were not written by the run. A session-level text-marking mode altered every `Write` input by inserting an invisible variation selector (U+E0101) after nearly every character. The agents refused to write the altered text to a public page and did not bypass the hook. The mode was turned off and the approved text was recovered from the run journal and written by hand.

## 4. fr security.md

The fr, de and es pages were still the old `<article>` HTML layout with old supported versions (0.21.x+/0.20.x/< 0.19.x). The en page is markdown with 0.22.x+/0.21.x/< 0.20.x. The fr page was translated in full from the current en markdown.

Verifier warnings that survived two repair rounds, and how each was resolved (eb07836b):

- "jours ouvrables" includes Saturday in France and shortens the stated deadlines. Changed to "jours ouvrés".
- Table header "Pris en charge" should be the feminine noun form. Changed to "Prise en charge".
- Infinitive instructions ("Envoyer", "Inclure") conflict with rule.fr-infinitive-buttons, which limits infinitives to button and link labels. Changed to "Envoyez", "Incluez". A second opinion considered infinitives normal procedural French; the binding rule was followed.
- The visible subject line was translated but the mailto link pre-fills the English subject. The visible text now quotes the English subject, so both match.

Not changed, left for a native-speaker read: heading noun forms ("Signaler une vulnérabilité"), one "faille de sécurité" among "vulnérabilité", "Adresse e-mail" as the step label, "mises à jour" for status updates, "votre vie privée".

## 5. keepEnglish candidates (fr)

| Key | Note |
|---|---|
| `LABELS.blog` | Standard French word, same spelling. |
| `LABELS.docs` | Same word in French. |
| `navigation.docs` | Short header nav label; abbreviation is understood in French tech UI, and 'Documentation' would be 13 characters against 4. Full form stays at LABELS.docs. |
| `onetime-secret-literal` | Brand name (rule.brand-names-untranslated). |
| `repository-facts.commits` | Git term used as a loanword in French; matches 'Dernier commit' and 'Aucun commit' in the same block. |
| `web.footer.links.api` | Acronym is the same in French. |
| `web.footer.links.contact` | Same word in French. |
| `web.footer.links.dpa` | Acronym in common use in French B2B contracts; no established French acronym, and expanding it would not fit a footer label. |
| `web.footer.links.github` | Third-party product name. |
| `web.footer.links.guides` | Same word in French. |
| `web.homepage.hero.compliance.openSource` | Standard term in French software usage. |
| `web.homepage.infrastructure.regions.ca` | Place names are spelled the same in French. |
| `web.pricing.tiers.identity.name` | Brand name (rule.brand-names-untranslated). |
| `web.pricing.tiers.team.name` | Plan name, kept in English to parallel Identity Plus. |
| `web.secrets.europe` | Same word in French. |
| `web.secrets.ttl.30minutes` | Same in French. |
| `web.secrets.ttl.5minutes` | Same in French. |

## 6. Glossary candidates (fr)

- commit -> commit. Recurs in repository-facts (Commits, Dernier commit, Aucun commit) and is not fixed by the bound glossary.
- Team Plus -> Team Plus. Plan name kept in English like Identity Plus, but rule.brand-names-untranslated does not list it.
- open source -> open source. Used in a homepage compliance badge and not fixed by the bound glossary; the alternative 'code source ouvert' is not used in fr.json.
- acknowledgment -> accusé de réception. Security-report step label. The existing label "Remerciements" means "thanks", while the sentence under it already says "accusé de réception".
- vulnerability -> vulnérabilité. Used throughout the page, but one sentence in the existing translation uses "faille de sécurité" for "security vulnerability". No bound rendering exists.

## 7. Other findings

- fr `about.md` uses "phrase de passe"; the bound rendering is passphrase -> "phrase secrète".
- The stale check compares en.json at the locale file's last commit with en.json at HEAD. en.json and all locale files shared their last commit (22680c0f), so the check had nothing to detect. Committing a locale file moves its baseline.
- The resolver run (`resolve.py --all`) rewrote `lib/resolver/index.json` in this repo. The committed index predated the `rules/` layout (bd9d655). Regenerated in onetimesecret/translation-rules#58.
- en.json lacks 14 keys used by components (QuoteSection, IconsInfo, EmailObfuscator, HeroTitle). `HERO_HEADING_KEYS.line1` is likely a dynamic-key false positive.
- `src/scripts/generate-markdown-content.mjs` (`pnpm i18n:markdown`) can generate `about.md` and `security.md` from locale JSON. It is not part of the build. A second opinion found it skips fr because fr.json has no `web.security` keys; not verified.
- 16 unrouted content locale directories were dropped: bg, da_DK, de_AT, el_GR, fr_CA, fr_FR, it_IT, ja, ko, mi_NZ, nl, pl, pt_BR, sv_SE, tr, uk.

## Findings manifest

- de and es skipped for a website-vs-governance register conflict.
  wont_fix: maintainer decision 2026-11-04 keeps the website formal and governance unchanged; rerun with `registerPolicy: "file"` (website-translation-de-es.md).
- fr security.md verifier warnings (jours ouvrés, Prise en charge, imperatives, subject line).
  wont_fix: no rule change needed; fixed directly in content (onetimesecret/onetimesecret.com eb07836b).
- Remaining fr security.md style points listed in section 4.
  wont_fix: minor wording; left for a native-speaker read rather than a rule change.
- fr glossary candidates (section 6).
  wont_fix: candidates only, not adopted. Revisit when a term recurs in another surface.
- fr about.md "phrase de passe" conflicts with the bound glossary rendering "phrase secrète".
  wont_fix: website content fix, no rule change; the glossary already decides the term.
- Stale index.json in lib/resolver.
  wont_fix: fixed by regenerating it in onetimesecret/translation-rules#58; no rule change.
- Stale check blind when en.json and the locale file share a commit; 14 en.json source gaps.
  wont_fix: workflow tooling and website code, outside translation-rules.
- Session text-marking mode blocked agent writes.
  wont_fix: local session setting, not a translation rule.
