# Translation report 2026-11-04 (de, es)

## 1. Headline

| Locale | UI keys approved / lines changed | Pages | Rejected |
|---|---|---|---|
| de | 18 / ~3 keys (`6 +-`) | `src/content/pages/de/security.md` (full retranslation) | 0 |
| es | 11 / ~2 keys (`4 +-`) | `src/content/pages/es/security.md` (full retranslation) | 0 |

- Register: formal (Sie / usted), per the user request. This overrides governance `register.form=informal`.
- Gates: JSON parse and key parity OK (396 keys each, 0 missing/extra). `i18n:scan` exit 0, 56 missing rows = baseline. vitest 1519/1519 passed.
- **Nothing blocks a commit.** The governance register conflict needs a decision, but it does not block this diff.
- Most approved UI values already matched the existing values (brand names, loanwords). Real UI changes:
  - de: nav docs `Docs`->`Dokumentation`, changelog->`Änderungsprotokoll`, dpa `DPA`->`AVV`.
  - es: docs->`Documentación`, changelog->`Registro de cambios`.
- Both old security.md files were mostly English inside the old HTML layout, so they were retranslated in full from the current en Markdown. fr (eb07836b) was the structural reference.

## 2. Decisions needed

**Skipped locales:** none. fr is routed but was not a target in this run.

**Rejected items:** none.

**Register / governance (decide once):**
- Governance (70c4f453) sets de=du and es=tú, and lists `usted`/`ustedes` as forbidden tokens. The website uses formal register. Record a website-surface exception in translation-rules, or lint/verify will flag correct formal output in later runs.
- `de/about.md` is fully informal (24 du/dir/dein hits). Under the formal policy it needs a register rewrite. Not done in this run.
- es UI mixes tú imperatives (`Contacta`, `Escribe`, `te envió`) with usted/su. es `about.md` / `accessibility.md` also mix registers (7x su, 2x sus, 7x tu). A formal normalization pass is needed. Not done in this run.

**Reviewer warnings (fidelity), not applied:**
- de security.md closing line: "sicher und hervorragend zu halten" is unidiomatic. Suggested: "… Onetime Secret sicher und zuverlässig zu halten!"
- es security.md bullet: "Cualquier posible impacto." is a calque. Suggested: "El posible impacto."

**Open questions:**
- Confirm that the full retranslation of de/es security.md is acceptable. Applying only the diff would have left English pages.
- Email subject `Vulnerability Report: [Brief Description]` stays English (de, es, fr) to match the mailto subject parameter. Localize both?
- DPA: de now shows `AVV`, es keeps `DPA`. Is the asymmetry intended? Does the DPA page that de links to use AVV?
- de heading `Schwachstelle melden` vs `Eine Schwachstelle melden`.
- `Dokumentation` / `Documentación` are much longer than `Docs`. Check that nav/header doesn't wrap at narrow widths.
- de footer `Self-Hosting` stays English (keepEnglish below). Confirm.
- Minor: de/es security.md end with `\n\n`; en/fr end with `\n`.

## 3. keepEnglish candidates (next run `args.keepEnglish`)

| Key | de | es | Note |
|---|---|---|---|
| `LABELS.blog` | x | x | Loanword |
| `onetime-secret-literal` | x | x | Brand |
| `repository-facts.commits` | x | x | Dev loanword; matches `latest-commit` |
| `web.footer.links.api` | x | x | Acronym |
| `web.footer.links.github` | x | x | Brand |
| `web.pricing.comparison.status.beta` | x | x | Same word |
| `web.pricing.tiers.identity.name` | x | x | Plan name (brand) |
| `web.pricing.tiers.team.name` | x | x | Plan name |
| `status` | x | | Same word in de |
| `web.footer.links.selfHosting` | x | | IT loanword |
| `web.lookalike.headerLabel` | x | | Brand + `?` |
| `web.pricing.region` | x | | Same word in de |
| `web.secrets.passphraseInputLabel` | x | | Glossary binds Passphrase |
| `web.useCases.hr.title` | x | | HR / People Ops loan terms |
| `web.useCases.itdevops.title` | x | | Technical terms |
| `web.footer.links.dpa` | | x | Acronym common in es GDPR use (de uses AVV) |

## 4. Glossary candidates (propose upstream in translation-rules; not written there)

**de**
- DPA -> AVV (Auftragsverarbeitungsvertrag). This is the GDPR term.
- changelog -> Änderungsprotokoll
- docs (nav) -> Dokumentation
- vulnerability -> Schwachstelle (Sicherheitslücke as a variant in prose)
- business days -> Arbeitstage, not Werktage (Werktage includes Saturday). fr uses "jours ouvrés".
- security updates -> Sicherheitsupdates
- fix (security patch) -> Korrektur

**es**
- changelog -> Registro de cambios
- docs (nav) -> Documentación
- commit -> commit (loanword; not «confirmación»)
- supported (version) -> con soporte / sin soporte (replaces the calque «Soportado»)
- vulnerability report -> informe; informar de una vulnerabilidad
- fix (security patch) -> corrección (kept separate from actualización)

**Both:** governance needs a website-surface register exception (formal).

## 5. Source gaps

**Keys used in components but missing from en.json** (14 keys; they produce the 56 scan rows):
- QuoteSection.vue: `ai-generated-testimonials`, `what-leading-ai-says-about-us`, `note`, `this-quote-was-generated-by`, `it-was-based-on-the-content-of-the-page-and-does`
- IconsInfo.vue: `font-awesome-6`, `carbon`, `heroicons`, `material-design-icons`, `google-material`, `other`, `icon-library`
- EmailObfuscator.vue: `email-address-copied-to-clipboard`
- HeroTitle.vue: `HERO_HEADING_KEYS.line1` (likely a false positive from a dynamic key)

**Unrouted content locale dirs, not translated:** bg, da_DK, de_AT, el_GR, fr_CA, fr_FR, it_IT, ja, ko, mi_NZ, nl, pl, pt_BR, sv_SE, tr, uk.

**Governance:** source (b) `../onetimesecret/generated/i18n/.resolved` is missing, so governance was derived via (c) at 70c4f453. The resolver also rewrote `translation-rules/lib/resolver/index.json` in the sibling repo. It shows no tracked diff there.

## 6. Next steps

1. Review `git --no-pager diff src/i18n/ui/{de,es}.json src/content/pages/{de,es}/security.md`.
2. Optionally apply the two fidelity fixes from section 2.
3. Commit on a branch (current: `i18n/website-translation-2026-11`), push, and open a PR against `develop`.
4. Follow-up: formal register pass on de `about.md`, es `about.md` / `accessibility.md`, and the es UI tú keys.
5. Recommended: add a per-key source-hash manifest (en value hash per key/page at translation time), so stale detection no longer depends on git commit ordering.
6. Propose the glossary entries and the register exception upstream in translation-rules.

## 7. Applied after the run

Changes made by hand in onetimesecret/onetimesecret.com#275 after this report was written:

- Both fidelity warnings from section 2 were applied: de "sicher und zuverlässig zu halten", es "El posible impacto." (commits 4f6aaa97, a89be8e2).
- `navigation.docs` was set back to `Docs` in de and es, matching fr. The header nav label has little room; the full form stays at `LABELS.docs`. The `apply-de.json` / `apply-es.json` artifacts show the workflow's proposed `Dokumentation` / `Documentación`.
- The trailing blank line was removed from de/es `security.md`.
- The full retranslation of both security pages was accepted.
- The email subject stays English in fr, de and es, so it matches the mailto `subject` parameter.

## Findings manifest

- Website register (formal Sie/usted) diverges from governance (informal du/tú, set in c930872 from the app content).
  wont_fix: maintainer decision 2026-11-04 keeps the website formal and leaves governance unchanged. Website runs use `registerPolicy: "file"`. No website-surface exception has been adopted yet; file a retro if one is wanted.
- de `about.md` is informal; es UI, `about.md` and `accessibility.md` mix tú and usted.
  wont_fix: website content work, not a rule change. Tracked as a follow-up in onetimesecret/onetimesecret.com#275.
- Glossary candidates for de and es (section 4).
  wont_fix: candidates only, not adopted. Revisit when a term recurs in another surface.
- Two fidelity warnings on the security pages (section 2).
  wont_fix: no rule change needed; fixed directly in content (section 7).
- Proposed nav label `Dokumentation` / `Documentación` is too long for the header.
  wont_fix: reverted to `Docs` in content; no rule change.
- 14 keys used by components are missing from the website's en.json.
  wont_fix: website source code gap, outside translation-rules.
- Stale detection depends on git commit ordering (section 6, step 5).
  wont_fix: workflow tooling change, not a rule; belongs with the translate-website-i18n workflow.
