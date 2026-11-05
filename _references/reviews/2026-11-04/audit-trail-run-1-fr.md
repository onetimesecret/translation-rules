# Audit trail: run 1 (fr; registerPolicy strict)

Every agent step of the run in execution order, rendered from the run journal. Values and page text are as each agent returned them, before any later hand edit. Local paths are removed. The scout's full result is in the matching `artifacts/*-scout.json` file.

## 1. scout (Scout)

Routed locales: fr, de, es. Targets: 3. Scan missing rows: 56. Notes: 14 (see the scout JSON).

## 2. read:fr/security.md (Translate)

Read the existing page (2001 characters). The text is in git history.

## 3. translate:fr/ui-1 (Translate)

| Key | Value | keepEnglish | Note |
|---|---|---|---|
| `LABELS.blog` | Blog | yes | Standard French word, same spelling. |
| `LABELS.docs` | Documentation | yes | Same word in French. |
| `navigation.docs` | Docs | yes | Short header nav label; abbreviation is understood in French tech UI, and 'Documentation' would be 13 characters against 4. Full form stays at LABELS.docs. |
| `onetime-secret-literal` | Onetime Secret | yes | Brand name (rule.brand-names-untranslated). |
| `repository-facts.commits` | Commits | yes | Git term used as a loanword in French; matches 'Dernier commit' and 'Aucun commit' in the same block. |
| `web.footer.links.api` | API | yes | Acronym is the same in French. |
| `web.footer.links.contact` | Contact | yes | Same word in French. |
| `web.footer.links.dpa` | DPA | yes | Acronym in common use in French B2B contracts; no established French acronym, and expanding it would not fit a footer label. |
| `web.footer.links.github` | GitHub | yes | Third-party product name. |
| `web.footer.links.guides` | Guides | yes | Same word in French. |
| `web.homepage.hero.compliance.openSource` | Open source | yes | Standard term in French software usage. |
| `web.homepage.infrastructure.regions.ca` | Toronto, Canada | yes | Place names are spelled the same in French. |
| `web.pricing.tiers.identity.name` | Identity Plus | yes | Brand name (rule.brand-names-untranslated). |
| `web.pricing.tiers.team.name` | Team Plus | yes | Plan name, kept in English to parallel Identity Plus. |
| `web.secrets.europe` | Europe | yes | Same word in French. |
| `web.secrets.ttl.30minutes` | 30 minutes | yes | Same in French. |
| `web.secrets.ttl.5minutes` | 5 minutes | yes | Same in French. |

glossaryCandidates:

- term: commit; rendering: commit; reason: Recurs in repository-facts (Commits, Dernier commit, Aucun commit) and is not fixed by the bound glossary.
- term: Team Plus; rendering: Team Plus; reason: Plan name kept in English like Identity Plus, but rule.brand-names-untranslated does not list it.
- term: open source; rendering: open source; reason: Used in a homepage compliance badge and not fixed by the bound glossary; the alternative 'code source ouvert' is not used in fr.json.

## 4. translate:fr/security.md (Translate)

Page text returned:

````markdown
---
title: Politique de sécurité
---


Nous prenons la sécurité de ce projet au sérieux et apprécions vos efforts pour divulguer les vulnérabilités de manière responsable. Ce document décrit notre politique de sécurité et fournit des lignes directrices sur la manière de signaler les vulnérabilités.

## Versions prises en charge

Nous fournissons des mises à jour de sécurité pour les versions suivantes de notre projet&nbsp;:

| Version  | Pris en charge |
|----------|----------------|
| 0.22.x+  | ✅             |
| 0.21.x   | ✅             |
| < 0.20.x | ❌             |

Si vous utilisez une version non prise en charge, nous vous recommandons vivement d'effectuer une mise à niveau vers l'une des versions prises en charge afin de recevoir les dernières mises à jour de sécurité.

## Signaler une vulnérabilité

Si vous découvrez une faille de sécurité dans ce projet, nous vous encourageons à la signaler dès que possible.

### Comment rapporter

1. **Adresse e-mail&nbsp;:** Envoyer un e-mail à [security@onetimesecret.com](mailto:security@onetimesecret.com?subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D) avec pour objet «&nbsp;Rapport de vulnérabilité&nbsp;: [Brève description]&nbsp;».
2. **Détails&nbsp;:** Inclure autant d'informations que possible sur la vulnérabilité&nbsp;:
   - Description détaillée de la vulnérabilité.
   - Marche à suivre pour reproduire le problème.
   - Tout impact potentiel.
   - Vos coordonnées pour le suivi.

### À quoi s'attendre

1. **Remerciements&nbsp;:** Vous recevrez un accusé de réception dans les 5 jours ouvrables.
2. **Évaluation initiale&nbsp;:** Nous procéderons à une première évaluation dans un délai de 14 jours ouvrables.
3. **Mises à jour&nbsp;:** Vous recevrez des mises à jour sur l'état d'avancement au moins une fois tous les 7 jours jusqu'à ce que le problème soit résolu ou qu'une décision soit prise.

### Processus de résolution

1. **Vulnérabilités acceptées&nbsp;:** Nous corrigerons le problème et vous avertirons dès que le correctif sera déployé.
2. **Vulnérabilités déclassées&nbsp;:** Nous fournirons une explication détaillée si la vulnérabilité n'est pas acceptée.

### Confidentialité

Nous prenons votre vie privée au sérieux. Les rapports resteront confidentiels et nous coordonnerons la divulgation une fois un correctif mis en place.

Merci de nous aider à préserver la sécurité et l'excellence de Onetime Secret&nbsp;!
````

glossaryCandidates:

- term: acknowledgment; rendering: accusé de réception; reason: Security-report step label. The existing label "Remerciements" means "thanks", while the sentence under it already says "accusé de réception".
- term: vulnerability; rendering: vulnérabilité; reason: Used throughout the page, but one sentence in the existing translation uses "faille de sécurité" for "security vulnerability". No bound rendering exists.

questions:

- Changes beyond the diff, made to meet binding rules: "courriel" became "e-mail" (bound glossary), and `&nbsp;` was added before `:` and `!` (rule.fr-punctuation-nbsp). The subject line's straight quotes also became « » to match src/content/pages/fr/about.md; no rule requires this.
- Kept unchanged under the apply-only-the-diff instruction, but these look like translation errors. Approve the fixes? "**Remerciements**" for "Acknowledgment" -> "**Accusé de réception**"; "**Vulnérabilités déclassées**" for "Declined Vulnerabilities" -> "**Vulnérabilités refusées**"; "### Comment rapporter" for "How to Report" -> "### Comment signaler"; "**Adresse e-mail**" for "Email" -> "**E-mail**".
- The mailto link's prefilled subject stays in English as required (`subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D`), while the visible text asks for « Rapport de vulnérabilité : [Brève description] ». French reporters who use the link get a subject that differs from the one the page gives. Is that acceptable for triage?
- Outside this task: src/content/pages/fr/about.md uses "phrase de passe" ("Si vous utilisez une phrase de passe (disponible sous « Options de confidentialité »)"), which conflicts with the bound rendering passphrase -> "phrase secrète". Not changed here.

## 5. verify:governance:fr/ui-1 (Verify)

No findings.


## 6. verify:fidelity:fr/ui-1 (Verify)

No findings.


## 7. verify:governance:fr/security.md (Verify)

- **error** `page`: "**Remerciements :**" mistranslates "Acknowledgment". Here the word means confirmation of receipt, not thanks. The label also disagrees with its own sentence, which says "accusé de réception".
  Suggestion: **Accusé de réception&nbsp;:** Vous recevrez un accusé de réception dans les 5 jours ouvrables.
- **error** `page`: "**Vulnérabilités déclassées :**" mistranslates "Declined". "Déclassée" means downgraded or declassified, which has a misleading meaning in a security policy. The sentence that follows says "n'est pas acceptée", so the label and body also disagree.
  Suggestion: **Vulnérabilités refusées&nbsp;:** Nous fournirons une explication détaillée si la vulnérabilité n'est pas acceptée.
- **warn** `page`: Heading "### Comment rapporter" breaks rule.fr-infinitive-buttons, which requires the noun form for headings. It also breaks rule.terminology-consistency, because the same action is "signaler" everywhere else on the page. "Rapporter" with no object is also unidiomatic.
  Suggestion: ### Procédure de signalement
- **warn** `page`: Heading "## Signaler une vulnérabilité" uses an infinitive. rule.fr-infinitive-buttons reserves the infinitive for button and link labels and requires the noun form for titles and headings.
  Suggestion: ## Signalement d'une vulnérabilité
- **warn** `page`: Heading "### À quoi s'attendre" is an infinitive construction. rule.fr-infinitive-buttons requires the noun form for headings.
  Suggestion: ### Suite donnée à votre signalement
- **warn** `page`: "Envoyer un e-mail..." and "Inclure autant d'informations..." use the infinitive in instructions addressed to the reader. rule.fr-infinitive-buttons allows the infinitive only for button and link labels. The glossary examples render sentence-level instructions in the vous imperative ("Saisissez", "Copiez"), and the rest of the page addresses the reader as vous.
  Suggestion: "Envoyez un e-mail à [...]" and "Incluez autant d'informations que possible sur la vulnérabilité&nbsp;:"
- **warn** `page`: "security vulnerability" becomes "faille de sécurité" in one sentence, while "vulnerability" is "vulnérabilité" everywhere else on the page. rule.terminology-consistency forbids varying terms for the same sense.
  Suggestion: Si vous découvrez une vulnérabilité de sécurité dans ce projet, nous vous encourageons à la signaler dès que possible.
- **warn** `page`: The visible text gives the subject as "Rapport de vulnérabilité : [Brève description]", but the unchanged mailto link pre-fills "Vulnerability Report: [Brief Description]". A reader who clicks the link sees a different subject from the one the page tells them to use. The URL matches the source, so markup is preserved, but the two no longer agree.
  Suggestion: If triage does not depend on the English subject, localize the query: mailto:security@onetimesecret.com?subject=Rapport%20de%20vuln%C3%A9rabilit%C3%A9%20%3A%20%5BBr%C3%A8ve%20description%5D. If triage does depend on it, keep the URL and show the English subject in the visible text.
- **warn** `page`: Table header "Pris en charge" is masculine, but it describes the rows of the "Version" column, and the section heading uses "Versions prises en charge". The agreement is wrong.
  Suggestion: | Version  | Prise en charge |, with the separator and cell padding adjusted to match.
- **warn** `page`: "Merci de nous aider à préserver..." is ambiguous. "Merci de + infinitive" is the standard French polite request, so it can read as "please help us" and not as thanks for help given, which is what the source says.
  Suggestion: Merci de votre aide pour préserver la sécurité et l'excellence de Onetime Secret&nbsp;!

## 8. verify:fidelity:fr/security.md (Verify)

- **error** `page`: '**Remerciements :**' mistranslates 'Acknowledgment'. It means thanks, not confirmation of receipt, and it does not match the sentence that follows ('accusé de réception').
  Suggestion: **Accusé de réception&nbsp;:** Vous recevrez un accusé de réception dans les 5 jours ouvrés.
- **error** `page`: 'Vulnérabilités déclassées' has the wrong sense. 'Déclassé' means downgraded or declassified, while the source 'Declined' means not accepted. The sentence itself says 'n'est pas acceptée', and the label should pair with 'acceptées'.
  Suggestion: **Vulnérabilités refusées&nbsp;:** Nous fournirons une explication détaillée si la vulnérabilité n'est pas acceptée.
- **warn** `page`: The heading 'Comment rapporter' is an English calque. 'Rapporter' with no object reads as broken French here, and the parent heading and body use 'signaler' for the same action.
  Suggestion: ### Comment signaler une vulnérabilité (or: ### Comment la signaler)
- **warn** `page`: 'jours ouvrables' does not match 'business days' in France, where 'ouvrables' includes Saturday. This shifts the stated response deadlines. 'Ouvrables' is correct for fr_CA, but this is the generic fr locale and fr_CA has its own file.
  Suggestion: Use 'jours ouvrés' in both lines: 'dans les 5 jours ouvrés' and 'dans un délai de 14 jours ouvrés'.
- **warn** `page`: The table header 'Pris en charge' is masculine, but the column describes 'Version' (feminine). The body text correctly uses 'versions prises en charge'.
  Suggestion: | Version  | Prise en charge |
- **warn** `page`: The label '**Adresse e-mail :**' changes the meaning. The source 'Email:' names the reporting channel, and the item tells the reader to send a message rather than giving an address field.
  Suggestion: **E-mail&nbsp;:** Envoyer un e-mail à [...]
- **warn** `page`: The prose tells the reader to use the subject « Rapport de vulnérabilité : [Brève description] », but the mailto link pre-fills the English 'Vulnerability Report: [Brief Description]'. A French reader who clicks the link gets a subject that differs from the instruction. All locales share this English mailto, so the fix may need to be made across locales or checked against any URL-preservation rule.
  Suggestion: Localize the link: mailto:security@onetimesecret.com?subject=Rapport%20de%20vuln%C3%A9rabilit%C3%A9%C2%A0%3A%20%5BBr%C3%A8ve%20description%5D

## 9. repair:fr/security.md#1 (Verify)

Page text returned:

````markdown
---
title: Politique de sécurité
---


Nous prenons la sécurité de ce projet au sérieux et apprécions vos efforts pour divulguer les vulnérabilités de manière responsable. Ce document décrit notre politique de sécurité et fournit des lignes directrices sur la manière de signaler les vulnérabilités.

## Versions prises en charge

Nous fournissons des mises à jour de sécurité pour les versions suivantes de notre projet&nbsp;:

| Version  | Pris en charge |
|----------|----------------|
| 0.22.x+  | ✅             |
| 0.21.x   | ✅             |
| < 0.20.x | ❌             |

Si vous utilisez une version non prise en charge, nous vous recommandons vivement d'effectuer une mise à niveau vers l'une des versions prises en charge afin de recevoir les dernières mises à jour de sécurité.

## Signaler une vulnérabilité

Si vous découvrez une faille de sécurité dans ce projet, nous vous encourageons à la signaler dès que possible.

### Comment rapporter

1. **Adresse e-mail&nbsp;:** Envoyer un e-mail à [security@onetimesecret.com](mailto:security@onetimesecret.com?subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D) avec pour objet «&nbsp;Rapport de vulnérabilité&nbsp;: [Brève description]&nbsp;».
2. **Détails&nbsp;:** Inclure autant d'informations que possible sur la vulnérabilité&nbsp;:
   - Description détaillée de la vulnérabilité.
   - Marche à suivre pour reproduire le problème.
   - Tout impact potentiel.
   - Vos coordonnées pour le suivi.

### À quoi s'attendre

1. **Accusé de réception&nbsp;:** Vous recevrez un accusé de réception dans les 5 jours ouvrables.
2. **Évaluation initiale&nbsp;:** Nous procéderons à une première évaluation dans un délai de 14 jours ouvrables.
3. **Mises à jour&nbsp;:** Vous recevrez des mises à jour sur l'état d'avancement au moins une fois tous les 7 jours jusqu'à ce que le problème soit résolu ou qu'une décision soit prise.

### Processus de résolution

1. **Vulnérabilités acceptées&nbsp;:** Nous corrigerons le problème et vous avertirons dès que le correctif sera déployé.
2. **Vulnérabilités refusées&nbsp;:** Nous fournirons une explication détaillée si la vulnérabilité n'est pas acceptée.

### Confidentialité

Nous prenons votre vie privée au sérieux. Les rapports resteront confidentiels et nous coordonnerons la divulgation une fois un correctif mis en place.

Merci de nous aider à préserver la sécurité et l'excellence de Onetime Secret&nbsp;!
````

## 10. verify:governance:fr/security.md (Verify)

- **warn** `page`: The heading "## Signaler une vulnérabilité" uses an infinitive. rule.fr-infinitive-buttons reserves the infinitive for button and link labels and requires the noun form for titles and headings.
  Suggestion: ## Signalement d'une vulnérabilité
- **warn** `page`: The heading "### Comment rapporter" breaks the noun-form heading rule (rule.fr-infinitive-buttons). It also uses "rapporter" with no object, while the rest of the page uses "signaler" for "report", which is the term variation that rule.terminology-consistency prohibits.
  Suggestion: ### Procédure de signalement
- **warn** `page`: The heading "### À quoi s'attendre" uses an infinitive construction, not the noun form that rule.fr-infinitive-buttons requires for headings. The sibling headings "Processus de résolution" and "Confidentialité" are nouns.
  Suggestion: ### Suites données à votre signalement
- **warn** `page`: "security vulnerability" is rendered as "faille de sécurité" in "Si vous découvrez une faille de sécurité", while every other occurrence on the page uses "vulnérabilité". rule.terminology-consistency prohibits varying the term for the same sense.
  Suggestion: Si vous découvrez une vulnérabilité de sécurité dans ce projet, nous vous encourageons à la signaler dès que possible.
- **warn** `page`: The table header "Pris en charge" is masculine, but it describes the feminine noun in the adjacent "Version" column. The noun form also fits the rule.fr-infinitive-buttons heading convention.
  Suggestion: | Version  | Prise en charge | (widen the delimiter row and cell padding to match)
- **warn** `page`: The label "**Adresse e-mail&nbsp;:**" adds "Adresse", which is not in the source. The source label "Email:" names the reporting channel, and the bound glossary rendering for the noun is "e-mail". As written, an address label is followed by an instruction to send a message.
  Suggestion: **E-mail&nbsp;:**
- **warn** `page`: The instructions "Envoyer un e-mail à..." and "Inclure autant d'informations..." use bare infinitives. rule.fr-infinitive-buttons covers only button and link labels; these are full sentences addressed to the reader. The glossary's good examples use the vous imperative ("Saisissez", "Copiez"), and the rest of the page addresses the reader as vous.
  Suggestion: Envoyez un e-mail à [...] ; Incluez autant d'informations que possible sur la vulnérabilité&nbsp;:

## 11. verify:fidelity:fr/security.md (Verify)

- **error** `page`: Heading "### Comment rapporter" uses the transitive verb "rapporter" with no object, so it reads as incomplete. It also breaks consistency with the parent heading and body, which use "signaler". "Rapporter" can also suggest telling on someone.
  Suggestion: ### Comment signaler une vulnérabilité
- **warn** `page`: The table header "Pris en charge" is masculine, but it describes the feminine "Version" in the adjacent column.
  Suggestion: | Version  | Prise en charge |
- **warn** `page`: "business days" is rendered as "jours ouvrables" (twice). In France, "jours ouvrables" normally includes Saturdays, so the commitment is shorter than the English: 5 and 14 weekdays. "Jours ouvrés" matches the source.
  Suggestion: "dans les 5 jours ouvrés" and "dans un délai de 14 jours ouvrés"
- **warn** `page`: The visible text gives the subject line in French ("Rapport de vulnérabilité : [Brève description]"), but the mailto link still pre-fills the English "Vulnerability Report: [Brief Description]". A French reader who clicks the link gets a different subject from the one they were told to use.
  Suggestion: Encode the French subject in the link: mailto:security@onetimesecret.com?subject=Rapport%20de%20vuln%C3%A9rabilit%C3%A9%20%3A%20%5BBr%C3%A8ve%20description%5D. If triage depends on the English subject, keep the link and show the English subject in the text instead.
- **warn** `page`: The label "Adresse e-mail :" announces an address, but the item is an instruction to send a message. The source label "Email:" names the channel. This also repeats "e-mail" in the same line.
  Suggestion: **Par e-mail :** Envoyer un message à [security@onetimesecret.com](...) avec pour objet ...
- **warn** `page`: "Vous recevrez des mises à jour sur l'état d'avancement" is a calque of "status updates". In this document "mises à jour" already means software updates ("mises à jour de sécurité"), so the same term now has two senses, and the "Mises à jour :" label has the same problem.
  Suggestion: **Suivi :** Nous vous informerons de l'état d'avancement au moins une fois tous les 7 jours jusqu'à ce que le problème soit résolu ou qu'une décision soit prise.

## 12. repair:fr/security.md#2 (Verify)

Page text returned:

````markdown
---
title: Politique de sécurité
---


Nous prenons la sécurité de ce projet au sérieux et apprécions vos efforts pour divulguer les vulnérabilités de manière responsable. Ce document décrit notre politique de sécurité et fournit des lignes directrices sur la manière de signaler les vulnérabilités.

## Versions prises en charge

Nous fournissons des mises à jour de sécurité pour les versions suivantes de notre projet&nbsp;:

| Version  | Pris en charge |
|----------|----------------|
| 0.22.x+  | ✅             |
| 0.21.x   | ✅             |
| < 0.20.x | ❌             |

Si vous utilisez une version non prise en charge, nous vous recommandons vivement d'effectuer une mise à niveau vers l'une des versions prises en charge afin de recevoir les dernières mises à jour de sécurité.

## Signaler une vulnérabilité

Si vous découvrez une faille de sécurité dans ce projet, nous vous encourageons à la signaler dès que possible.

### Comment signaler une vulnérabilité

1. **Adresse e-mail&nbsp;:** Envoyer un e-mail à [security@onetimesecret.com](mailto:security@onetimesecret.com?subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D) avec pour objet «&nbsp;Rapport de vulnérabilité&nbsp;: [Brève description]&nbsp;».
2. **Détails&nbsp;:** Inclure autant d'informations que possible sur la vulnérabilité&nbsp;:
   - Description détaillée de la vulnérabilité.
   - Marche à suivre pour reproduire le problème.
   - Tout impact potentiel.
   - Vos coordonnées pour le suivi.

### À quoi s'attendre

1. **Accusé de réception&nbsp;:** Vous recevrez un accusé de réception dans les 5 jours ouvrables.
2. **Évaluation initiale&nbsp;:** Nous procéderons à une première évaluation dans un délai de 14 jours ouvrables.
3. **Mises à jour&nbsp;:** Vous recevrez des mises à jour sur l'état d'avancement au moins une fois tous les 7 jours jusqu'à ce que le problème soit résolu ou qu'une décision soit prise.

### Processus de résolution

1. **Vulnérabilités acceptées&nbsp;:** Nous corrigerons le problème et vous avertirons dès que le correctif sera déployé.
2. **Vulnérabilités refusées&nbsp;:** Nous fournirons une explication détaillée si la vulnérabilité n'est pas acceptée.

### Confidentialité

Nous prenons votre vie privée au sérieux. Les rapports resteront confidentiels et nous coordonnerons la divulgation une fois un correctif mis en place.

Merci de nous aider à préserver la sécurité et l'excellence de Onetime Secret&nbsp;!
````

## 13. verify:governance:fr/security.md (Verify)

- **warn** `page`: The visible subject line was translated, but the mailto link still prefills the English subject (subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D). A reader who clicks the link gets a subject that differs from the one the text tells them to use. The de/es pages sampled keep the visible subject in English.
  Suggestion: Leave the URL unchanged and quote the literal subject so both match: avec pour objet «&nbsp;Vulnerability Report: [Brief Description]&nbsp;».
- **warn** `page`: The heading '## Signaler une vulnérabilité' uses an infinitive. rule.fr-infinitive-buttons reserves the infinitive for button and link labels and requires the noun form for titles and headings. '### Comment signaler une vulnérabilité' also avoids the noun form.
  Suggestion: Use '## Signalement d'une vulnérabilité' and '### Procédure de signalement'.
- **warn** `page`: The numbered steps 'Envoyer un e-mail à...' and 'Inclure autant d'informations...' use infinitives for instructions addressed to the reader. rule.fr-infinitive-buttons limits the infinitive to button and link labels, and the rest of the page addresses the reader as vous ('Vous recevrez', 'Vos coordonnées'). The glossary examples also use the vous imperative ('Saisissez', 'Copiez').
  Suggestion: Use 'Envoyez un e-mail à...' and 'Incluez autant d'informations que possible sur la vulnérabilité&nbsp;:'.
- **warn** `page`: 'security vulnerability' is rendered as 'faille de sécurité' in one sentence, while every other instance of the concept on the page uses 'vulnérabilité', including the heading directly above it. This varies the term for one sense, against the intent of rule.terminology-consistency, although the term is not in the glossary.
  Suggestion: Use 'Si vous découvrez une vulnérabilité de sécurité dans ce projet, nous vous encourageons à la signaler dès que possible.'
- **warn** `page`: The label '**Adresse e-mail&nbsp;:**' translates 'Email:' as 'email address'. The label names the reporting channel, and the address itself follows in the sentence.
  Suggestion: Use '**E-mail&nbsp;:**', which also matches the bound glossary term e-mail.

## 14. verify:fidelity:fr/security.md (Verify)

- **warn** `page`: "jours ouvrables" (used for both the 5-day and 14-day commitments) does not match "business days" in France, where it legally includes Saturday. That shortens the stated deadlines. The equivalent there is "jours ouvrés" (Monday to Friday).
  Suggestion: "dans les 5 jours ouvrés" and "dans un délai de 14 jours ouvrés".
- **warn** `page`: The text gives the subject as "Rapport de vulnérabilité : [Brève description]", but the mailto link still pre-fills the English "Vulnerability Report: [Brief Description]". A French reader who clicks the link gets a subject different from the one the page tells them to use.
  Suggestion: Encode the French subject in the link: mailto:security@onetimesecret.com?subject=Rapport%20de%20vuln%C3%A9rabilit%C3%A9%C2%A0%3A%20%5BBr%C3%A8ve%20description%5D. If triage depends on the English subject, keep the link and quote the English subject in the text instead, so the two match.
- **warn** `page`: "**Adresse e-mail :** Envoyer un e-mail à..." mislabels the step. The source label "Email" names the action of sending an email, not an address, and "Adresse" is an addition that reads oddly in front of an instruction.
  Suggestion: "**E-mail :** Envoyer un e-mail à...", or "**Par e-mail :** ...".
- **warn** `page`: "Vous recevrez des mises à jour sur l'état d'avancement" is a calque of "status updates". It also reuses "mises à jour", which this page uses for software in "mises à jour de sécurité", so the label "Mises à jour :" could be misread as software updates.
  Suggestion: "**Suivi :** Nous vous tiendrons informé de l'état d'avancement au moins une fois tous les 7 jours jusqu'à ce que le problème soit résolu ou qu'une décision soit prise."

## 15. apply:fr (Apply)

problems:

- src/content/pages/fr/security.md was NOT written; the file is unchanged and still has the old HTML version. Both Write attempts failed: a hook rewrote the input, adding invisible Unicode characters (variation selectors, bytes starting F3 A0) throughout the French text, and auto mode then gave no verdict.
- The Write error said to reissue the call with the hook's altered input. I did not, because it comes from a tool result and would break the exact-content requirement by putting hidden characters in a public security page. I also did not write the file through Bash, which would have sidestepped the hook and the auto mode review.
- Action needed: find and disable the hook or plugin that alters Write input, since this may be tampering, or switch out of auto mode. Then write the approved security.md content. Check any other files written in this session for hidden characters; a scan of fr.json, security.md and apply-fr.json found none.
- The fr.json diff is only 1 line although 17 keys were written: 16 of the values already matched. All 17 were confirmed present in the file.

```json
{
 "locale": "fr",
 "filesWritten": [
  "tmp/i18n/apply-fr.json",
  "src/i18n/ui/fr.json"
 ],
 "uiKeysWritten": 17,
 "parityOk": true,
 "diffStat": " src/i18n/ui/fr.json | 2 +-\n 1 file changed, 1 insertion(+), 1 deletion(-)"
}
```

## 16. gate (Gate)

```json
{
 "scanMissingCount": 56,
 "scanOk": true,
 "testsRan": true,
 "testsPassed": true,
 "jsonParseOk": true,
 "details": "All three gates pass.\n\nResults:\n1. Key parity: de, en, es and fr all parse and each has the same 396 flattened keys, with none missing or extra. Arrays were compared as single leaf values, so array contents were not checked.\n2. i18n:scan: 56 Missing Keys rows, equal to the baseline. That is the same count of 14 per locale across de, en, es and fr, in QuoteSection.vue, IconsInfo.vue, EmailObfuscator.vue and HeroTitle.vue. All 56 are call-site issues in components, not gaps in any locale file, and none come from fr.json. `HERO_HEADING_KEYS.line1` looks like a scanner false positive on a variable reference. The 56 baseline was taken from the task; I did not re-measure it against the pre-change tree.\n3. Unit tests: exit 0, 44 files and 1519 tests passed.\n\nFor the reviewer:\n- The only uncommitted change is one line in src/i18n/ui/fr.json (line 381, `web.homepage.hero.title.line1` by its position in the diff). It replaces the ` ` escape with a literal U+00A0 byte (c2 a0, confirmed with xxd). The parsed value is identical, so this has no effect on the UI. It looks like a re-serialization artifact, not a translation edit. It was already present at the start of this gate, so the gate did not cause it.\n- That literal U+00A0 is the only NBSP in fr.json, and it is invisible in most editors and diffs. Other French strings use a plain space before `?` and `:`, for example lines 110, 263 and 493. Either restoring the escape or dropping this line from the commit would keep the diff clean. A separate question is whether French punctuation should use NBSP throughout, because plain spaces can wrap the `?` onto its own line.\n- Committed on this branch (c5d6876f, not uncommitted): \"IT & DevOps\" became \"Informatique et DevOps\", and the nav label \"Changelog\" became \"Journal des modifications\". The nav label matches `changelog.label` on line 532. The longer string may need a visual check in the nav or footer layout, because the gate does not test rendering.\n- These gates do not assess translation quality. pnpm type-check, lint and check were not part of this gate and were not run.\n\nNo tracked files were modified by this gate. The helper script and logs are in <local scratch> (keys.cjs, scan.log, test.log)."
}
```

## 17. report (Report)

```json
{
 "wrote": false,
 "path": "tmp/i18n/translation-report-unstamped.md",
 "headline": "Report NOT written; the file does not exist. Write failed because a hook added invisible Unicode characters to the input and auto mode gave no verdict. The error said to reissue the call with the altered text. I did not follow that, because the instruction came from a tool result and would put hidden characters in the file. I also did not write through Bash, which would sidestep the review. Same failure that stopped fr/security.md. Source not identified: no PreToolUse hooks in ~/.claude/settings.json or .claude/settings.local.json; the only plugin hooks.json with PreToolUse found is hookify, not confirmed as the cause. Needed: disable the responsible hook or plugin, or leave auto mode, then rerun this step. Key findings: fr.json's only diff is a no-op NBSP escape change (  to a literal U+00A0), so drop or restore it; fr/security.md is unchanged, still old HTML with old version numbers, and its approved text was not saved (apply-fr.json has only the 17 UI keys); de and es skipped for register conflicts; gates pass but did not cover the page; ../translation-rules/lib/resolver/index.json has an uncommitted rewrite."
}
```

## Findings manifest

- Verifier findings and repair rounds for run 1 (fr) are recorded above; their outcomes are summarized in website-translation-fr.md.
  wont_fix: audit record only; each finding is already resolved or triaged in website-translation-fr.md, so no separate rule change follows from this file.
