# Audit trail: run 2 (de, es; registerPolicy file)

Every agent step of the run in execution order, rendered from the run journal. Values and page text are as each agent returned them, before any later hand edit. Local paths are removed. The scout's full result is in the matching `artifacts/*-scout.json` file.

## 1. scout (Scout)

Routed locales: fr, de, es. Targets: 2. Scan missing rows: 56. Notes: 9 (see the scout JSON).

## 2. read:de/security.md (Translate)

Read the existing page (2001 characters). The text is in git history.

## 3. translate:de/ui-1 (Translate)

| Key | Value | keepEnglish | Note |
|---|---|---|---|
| `LABELS.blog` | Blog | yes | Established loanword in German; same word. |
| `navigation.docs` | Dokumentation |  | Header nav item (LayoutHeader.astro); matches existing LABELS.docs = Dokumentation. |
| `onetime-secret-literal` | Onetime Secret | yes | Brand name. |
| `repository-facts.commits` | Commits | yes | Standard German developer term; matches existing repository-facts.latest-commit = Letzter Commit. |
| `status` | Status | yes | Same word in German. |
| `web.footer.links.api` | API | yes | Technical acronym used unchanged in German. |
| `web.footer.links.changelog` | Änderungsprotokoll |  | Matches existing changelog.label = Änderungsprotokoll. |
| `web.footer.links.dpa` | AVV |  | German GDPR term: Auftragsverarbeitungsvertrag (AVV) is the standard equivalent of DPA. |
| `web.footer.links.github` | GitHub | yes | Brand name. |
| `web.footer.links.selfHosting` | Self-Hosting | yes | Established loanword in German IT usage; short footer label. |
| `web.lookalike.headerLabel` | Onetime Secret? | yes | Brand name with question mark; no surrounding text to adapt. |
| `web.pricing.comparison.status.beta` | Beta | yes | Same word in German. |
| `web.pricing.region` | Region | yes | Same word in German. |
| `web.pricing.tiers.identity.name` | Identity Plus | yes | Product tier name (brand). |
| `web.pricing.tiers.team.name` | Team Plus | yes | Product tier name. |
| `web.secrets.passphraseInputLabel` | Passphrase | yes | Bound glossary rendering: passphrase -> Passphrase. |
| `web.useCases.hr.title` | HR & People Ops | yes | HR and People Ops are standard loan terms in German business usage; matches existing de descriptions using HR. |
| `web.useCases.itdevops.title` | IT & DevOps | yes | Technical terms used unchanged in German. |

glossaryCandidates:

- term: DPA (Data Processing Agreement); rendering: AVV (Auftragsverarbeitungsvertrag); reason: Legal term likely to recur in footer, legal pages and pricing; the German GDPR equivalent is AVV, not the English acronym.
- term: changelog; rendering: Änderungsprotokoll; reason: Used in changelog.label and now web.footer.links.changelog; should stay consistent.
- term: docs (navigation label); rendering: Dokumentation; reason: LABELS.docs and navigation.docs should share one rendering.

## 4. translate:es/ui-1 (Translate)

| Key | Value | keepEnglish | Note |
|---|---|---|---|
| `LABELS.blog` | Blog | yes | Blog is the standard Spanish loanword (RAE accepts it). |
| `navigation.docs` | Documentación |  | Header nav item (LayoutHeader.astro). Matches the existing LABELS.docs value; neighbouring items such as Características are similar in length. |
| `onetime-secret-literal` | Onetime Secret | yes | Brand name; never translated. |
| `repository-facts.commits` | Commits | yes | Standard developer loanword in Spanish; matches the existing repository-facts.latest-commit value «Último commit». |
| `web.footer.links.api` | API | yes | Acronym used as-is in Spanish. |
| `web.footer.links.changelog` | Registro de cambios |  | Matches the existing changelog.label value «Registro de cambios». |
| `web.footer.links.dpa` | DPA | yes | Short footer label for the Data Processing Agreement. The acronym DPA is widely used in Spanish GDPR contexts, and the full Spanish term is too long for a footer link. |
| `web.footer.links.github` | GitHub | yes | Product name. |
| `web.pricing.comparison.status.beta` | Beta | yes | Same word in Spanish for a software release stage. |
| `web.pricing.tiers.identity.name` | Identity Plus | yes | Brand/plan name; never translated (rule.brand-names-untranslated). |
| `web.pricing.tiers.team.name` | Team Plus | yes | Plan name, kept in English to match Identity Plus. |

glossaryCandidates:

- term: changelog (noun); rendering: Registro de cambios; reason: Used in both changelog.label and web.footer.links.changelog; the glossary does not set a rendering.
- term: docs (navigation label); rendering: Documentación; reason: LABELS.docs and navigation.docs now share this value; the glossary does not set a rendering.
- term: commit (noun); rendering: commit (loanword); reason: Kept in English in repository-facts.*; this should be recorded so no one translates it to «confirmación».

questions:

- The task's REGISTER OVERRIDE (formal usted, which the user's request asks for) conflicts with the governance file. That file sets rule.es-register-informal (tú) and lists usted/ustedes as forbidden tokens. None of these 11 rows uses a pronoun, so the conflict has no effect on this batch. The orchestrator should decide whether the governance file or the formal site-wide register (already in use, e.g. «Vuelva pronto», «Lea nuestra Política de Privacidad») is authoritative, so the forbidden-token gate does not fail on formal strings.

## 5. read:es/security.md (Translate)

Read the existing page (2001 characters). The text is in git history.

## 6. translate:de/security.md (Translate)

Page text returned:

````markdown
---
title: Sicherheitsrichtlinie
---


Wir nehmen die Sicherheit dieses Projekts ernst und wissen Ihre Bemühungen zu schätzen, Schwachstellen verantwortungsvoll offenzulegen. Dieses Dokument beschreibt unsere Sicherheitsrichtlinie und erläutert, wie Sie Schwachstellen melden können.

## Unterstützte Versionen

Für die folgenden Versionen unseres Projekts stellen wir Sicherheitsupdates bereit:

| Version  | Unterstützt |
|----------|-------------|
| 0.22.x+  | ✅          |
| 0.21.x   | ✅          |
| < 0.20.x | ❌          |

Wenn Sie eine nicht unterstützte Version verwenden, empfehlen wir Ihnen dringend ein Upgrade auf eine der unterstützten Versionen, damit Sie die neuesten Sicherheitsupdates erhalten.

## Schwachstelle melden

Wenn Sie in diesem Projekt eine Sicherheitslücke entdecken, bitten wir Sie, diese so schnell wie möglich zu melden.

### So melden Sie eine Schwachstelle

1. **E-Mail:** Senden Sie eine E-Mail an [security@onetimesecret.com](mailto:security@onetimesecret.com?subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D) mit dem Betreff „Vulnerability Report: [Brief Description]“.
2. **Details:** Geben Sie so viele Informationen wie möglich zur Schwachstelle an:
   - Eine ausführliche Beschreibung der Schwachstelle.
   - Schritte zum Reproduzieren des Problems.
   - Mögliche Auswirkungen.
   - Ihre Kontaktdaten für Rückfragen.

### Was Sie erwarten können

1. **Eingangsbestätigung:** Sie erhalten innerhalb von 5 Arbeitstagen eine Eingangsbestätigung.
2. **Erste Bewertung:** Wir nehmen innerhalb von 14 Arbeitstagen eine erste Bewertung vor.
3. **Statusmeldungen:** Sie erhalten mindestens alle 7 Tage eine Statusmeldung, bis das Problem behoben ist oder eine Entscheidung getroffen wurde.

### Ablauf der Behebung

1. **Akzeptierte Schwachstellen:** Wir beheben die Schwachstelle und benachrichtigen Sie, sobald die Korrektur bereitgestellt ist.
2. **Abgelehnte Schwachstellen:** Wird eine Schwachstelle nicht akzeptiert, erhalten Sie von uns eine ausführliche Begründung.

### Vertraulichkeit

Wir nehmen Ihre Privatsphäre ernst. Meldungen werden vertraulich behandelt, und wir koordinieren die Offenlegung, sobald eine Korrektur vorliegt.

Vielen Dank, dass Sie uns helfen, Onetime Secret sicher und hervorragend zu halten!
````

glossaryCandidates:

- term: vulnerability; rendering: Schwachstelle (Sicherheitslücke as a variant in running prose); reason: This is the central term on the security page and has no bound rendering. It should stay consistent if the other de website pages or the docs mention vulnerability reporting.
- term: business days; rendering: Arbeitstage; reason: I chose this over 'Werktage', which in strict German usage includes Saturday and would change the response-time commitment. The French page made a matching choice: 'jours ouvrés'.
- term: security updates; rendering: Sicherheitsupdates; reason: Loanword compound. It matches the existing de house style, where 'Upgrade' is also kept as a loanword.
- term: fix (noun, security patch); rendering: Korrektur; reason: Used in 'once the fix is deployed' and 'after a fix is in place'. No rendering exists in the governance artifact.

questions:

- Most of the old de/security.md had never been translated: apart from the table header 'Unterstützt', it was English text inside the old HTML layout. Applying only the diff would have left the page in English. So I translated the whole page from the current English markdown source, the same way the French security page was redone in commit eb07836b. Please confirm that a full retranslation was acceptable here.
- Register: I used formal Sie/Ihr/Ihnen throughout, following your instruction to keep the website formal and matching de/accessibility.md. This conflicts with rule.de-du in tmp/i18n/governance/.resolved/de.json. If the website's de pages are meant to stay formal, the governance artifact should record a website-surface exception so later rounds don't flag or 'fix' this page.
- I left the email subject line 'Vulnerability Report: [Brief Description]' in English, inside German quotes „…“, so it matches the pre-filled mailto subject in the link URL. The French page does the same. Should both the visible text and the mailto subject be localized instead?
- Heading 'Reporting a Vulnerability' is now 'Schwachstelle melden' (an infinitive, without the article), the usual style for German headings. Change it to 'Eine Schwachstelle melden' if you'd rather mirror the English article.

## 7. translate:es/security.md (Translate)

Page text returned:

````markdown
---
title: Política de seguridad
---


Nos tomamos muy en serio la seguridad de este proyecto y agradecemos sus esfuerzos por divulgar las vulnerabilidades de forma responsable. Este documento describe nuestra política de seguridad y ofrece pautas sobre cómo informar de vulnerabilidades.

## Versiones con soporte

Ofrecemos actualizaciones de seguridad para las siguientes versiones de nuestro proyecto:

| Versión  | Con soporte |
|----------|-------------|
| 0.22.x+  | ✅          |
| 0.21.x   | ✅          |
| < 0.20.x | ❌          |

Si utiliza una versión sin soporte, le recomendamos encarecidamente que actualice a una de las versiones con soporte para asegurarse de recibir las últimas actualizaciones de seguridad.

## Informar de una vulnerabilidad

Si descubre una vulnerabilidad de seguridad en este proyecto, le animamos a que nos la comunique lo antes posible.

### Cómo informar

1. **Correo electrónico:** Envíe un correo electrónico a [security@onetimesecret.com](mailto:security@onetimesecret.com?subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D) con el asunto «Vulnerability Report: [Brief Description]».
2. **Detalles:** Incluya toda la información posible sobre la vulnerabilidad:
   - Una descripción detallada de la vulnerabilidad.
   - Los pasos para reproducir el problema.
   - Cualquier posible impacto.
   - Sus datos de contacto para el seguimiento.

### Qué puede esperar

1. **Acuse de recibo:** Recibirá un acuse de recibo en un plazo de 5 días hábiles.
2. **Evaluación inicial:** Realizaremos una evaluación inicial en un plazo de 14 días hábiles.
3. **Actualizaciones:** Recibirá actualizaciones sobre el estado al menos una vez cada 7 días hasta que el problema se resuelva o se tome una decisión.

### Proceso de resolución

1. **Vulnerabilidades aceptadas:** Las corregiremos y le avisaremos en cuanto la corrección esté desplegada.
2. **Vulnerabilidades rechazadas:** Si la vulnerabilidad no se acepta, le daremos una explicación detallada.

### Confidencialidad

Nos tomamos muy en serio su privacidad. Los informes se mantendrán confidenciales y coordinaremos la divulgación una vez que haya una corrección disponible.

¡Gracias por ayudarnos a mantener Onetime Secret seguro y excelente!
````

glossaryCandidates:

- term: supported (version); rendering: con soporte; reason: The previous es page used the calque 'Soportado'. I used 'con soporte' / 'sin soporte' for the heading, the table column and the prose so the page says it one way throughout.
- term: vulnerability report / report (noun); rendering: informe; informar de una vulnerabilidad; reason: Security-policy wording that may recur on other website or docs pages.
- term: fix (noun, security patch); rendering: corrección; reason: Kept apart from 'actualización' (update) so the two terms don't drift across security pages.

questions:

- This page uses the formal register (Envíe, Incluya, su, le), as the user asked. Governance rule.es-register-informal requires tú for es. I avoided the literal forbidden tokens 'usted'/'ustedes', but a register lint may still flag the su/le forms. The other es website pages mix the two registers (7x su, 2x sus, 7x tu), so about.md and accessibility.md need a formal pass too if the website is to read consistently formal.
- The existing es/security.md was almost all untranslated English inside the old HTML (only 'Versión', 'Soportado' and 'Detalles' were Spanish). Applying only the diff would have left an English page, so I translated the whole page into the new Markdown structure. I changed 'Soportado' to 'Con soporte'.
- The email subject stays in English («Vulnerability Report: [Brief Description]») to match the pre-filled mailto subject, which is part of the URL and can't be changed. The fr page does the same. Should the visible subject be translated anyway?

## 8. verify:governance:es/ui-1 (Verify)

No findings.


## 9. verify:fidelity:es/ui-1 (Verify)

No findings.


## 10. verify:governance:de/ui-1 (Verify)

No findings.


## 11. verify:fidelity:de/ui-1 (Verify)

No findings.


## 12. verify:governance:es/security.md (Verify)

No findings.


## 13. verify:fidelity:es/security.md (Verify)

- **warn** `page`: "Cualquier posible impacto." is a literal calque of "Any potential impact." and reads awkwardly as a list item in Spanish. The bullet asks the reporter to describe the impact, but "cualquier" makes it sound like an open-ended disclaimer.
  Suggestion: Replace it with "El posible impacto." (or "El impacto potencial."). This matches the parallel article-plus-noun structure of the other bullets ("Una descripción...", "Los pasos...", "Sus datos...").

## 14. verify:governance:de/security.md (Verify)

No findings.


## 15. verify:fidelity:de/security.md (Verify)

- **warn** `page`: Closing line "Onetime Secret sicher und hervorragend zu halten" is a literal rendering of "secure and excellent". In German, "hervorragend halten" is not idiomatic and reads awkwardly.
  Suggestion: Vielen Dank, dass Sie uns helfen, Onetime Secret sicher und zuverlässig zu halten! (alternatively: "... Onetime Secret sicher und auf hohem Niveau zu halten!")

## 16. apply:de (Apply)

problems:

- de.json diff shows only 6 changed lines: most of the 18 keys already had the same values (many are brand or loanword identities), so only a few lines actually changed.

```json
{
 "locale": "de",
 "filesWritten": [
  "tmp/i18n/apply-de.json",
  "src/i18n/ui/de.json",
  "src/content/pages/de/security.md"
 ],
 "uiKeysWritten": 18,
 "parityOk": true,
 "diffStat": " src/content/pages/de/security.md | 161 +++++++++++----------------------------\n src/i18n/ui/de.json              |   6 +-\n 2 files changed, 49 insertions(+), 118 deletions(-)"
}
```

## 17. apply:es (Apply)

problems:

- es.json diff is only 2 lines: most of the 11 approved values were already present (identical to existing/English values), so only ~2 keys actually changed.

```json
{
 "locale": "es",
 "filesWritten": [
  "tmp/i18n/apply-es.json",
  "src/i18n/ui/es.json",
  "src/content/pages/es/security.md"
 ],
 "uiKeysWritten": 11,
 "parityOk": true,
 "diffStat": " src/content/pages/es/security.md | 161 +++++++++++----------------------------\n src/i18n/ui/es.json              |   4 +-\n 2 files changed, 48 insertions(+), 117 deletions(-)"
}
```

## 18. gate (Gate)

```json
{
 "scanMissingCount": 56,
 "scanOk": true,
 "testsRan": true,
 "testsPassed": true,
 "jsonParseOk": true,
 "details": "All three gates pass. No tracked files were changed.\n\n1. JSON key parity: en.json, de.json, es.json and fr.json all parse. Each has 396 flattened keys, with 0 missing and 0 extra compared with en.json.\n2. `pnpm run i18n:scan` exits 0. The Missing Keys table has 56 rows (indices 0 to 55), which matches the baseline. These are the same 14 keys across 4 locales, from QuoteSection, IconsInfo, EmailObfuscator and HeroTitle (`HERO_HEADING_KEYS.line1`). None of them were introduced by this change. Output saved at <local scratch> `pnpm run test` (vitest) exits 0: 44 test files and 1519 tests passed.\n\nFor the reviewer:\n- UI string changes:\n  - de: nav.docs \"Docs\" -> \"Dokumentation\", changelog -> \"Änderungsprotokoll\", dpa \"DPA\" -> \"AVV\" (Auftragsverarbeitungsvertrag, the correct German term). Check that \"AVV\" is the abbreviation you want in the footer and that the DPA page it links to uses the same term.\n  - es: docs -> \"Documentación\", changelog -> \"Registro de cambios\". dpa stays \"DPA\" in Spanish. The German and Spanish handling of DPA now differs; that may be intended, but it is worth confirming.\n  - \"Self-Hosting\" is still English in de.\n- \"Dokumentation\" and \"Documentación\" are much longer than \"Docs\". Check that the nav and header don't wrap or overflow at narrow widths.\n- de/es security.md: both use the formal register (Sie / usted forms; a grep for du/dich/dein and tú/puedes/tienes found nothing). Headings, the version table rows (0.22.x+, 0.21.x) and the mailto link (including its English subject parameter) match en exactly.\n- Minor: de and es security.md end with an extra blank line (`\\n\\n`), while en and fr end with a single `\\n`. It does not affect rendering and only matters if lint or prettier checks it."
}
```

## 19. report (Report)

```json
{
 "wrote": true,
 "path": "tmp/i18n/translation-report-2026-11-04-de-es.md",
 "headline": "de: 18 UI keys approved (about 3 actually changed) and security.md fully retranslated; es: 11 UI keys approved (about 2 actually changed) and security.md fully retranslated. Formal register used, overriding governance. All gates pass and nothing blocks a commit. Still to decide: a governance register exception, plus the de about.md and es mixed-register follow-up."
}
```

## Findings manifest

- Verifier findings for run 2 (de, es) are recorded above; their outcomes are summarized in website-translation-de-es.md.
  wont_fix: audit record only; each finding is already resolved or triaged in website-translation-de-es.md, so no separate rule change follows from this file.
