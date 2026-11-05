# Hand edits after approval (2026-11-04)

What changed between the text the workflow approved and what was committed to onetimesecret.com (`3d0dcb53`). Approved text is the last translator or repair output for each page; the committed text is the merged file. A diff line starting with `-` is the approved text, `+` is the committed text.

## UI keys

**de:** 18 keys approved, 1 differ from the committed value.

| Key | Approved | Committed |
|---|---|---|
| `navigation.docs` | Dokumentation | Docs |

**es:** 11 keys approved, 1 differ from the committed value.

| Key | Approved | Committed |
|---|---|---|
| `navigation.docs` | Documentación | Docs |

**fr:** 17 keys approved, 0 differ from the committed value.

## Pages

### de/security.md

```diff
--- approved/de/security.md
+++ committed/de/security.md
@@ -47,2 +47,2 @@
 
-Vielen Dank, dass Sie uns helfen, Onetime Secret sicher und hervorragend zu halten!
+Vielen Dank, dass Sie uns helfen, Onetime Secret sicher und zuverlässig zu halten!
```

### es/security.md

```diff
--- approved/es/security.md
+++ committed/es/security.md
@@ -29,3 +29,3 @@
    - Los pasos para reproducir el problema.
-   - Cualquier posible impacto.
+   - El posible impacto.
    - Sus datos de contacto para el seguimiento.
```

### fr/security.md

```diff
--- approved/fr/security.md
+++ committed/fr/security.md
@@ -11,7 +11,7 @@
 
-| Version  | Pris en charge |
-|----------|----------------|
-| 0.22.x+  | ✅             |
-| 0.21.x   | ✅             |
-| < 0.20.x | ❌             |
+| Version  | Prise en charge |
+|----------|-----------------|
+| 0.22.x+  | ✅              |
+| 0.21.x   | ✅              |
+| < 0.20.x | ❌              |
 
@@ -25,4 +25,4 @@
 
-1. **Adresse e-mail&nbsp;:** Envoyer un e-mail à [security@onetimesecret.com](mailto:security@onetimesecret.com?subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D) avec pour objet «&nbsp;Rapport de vulnérabilité&nbsp;: [Brève description]&nbsp;».
-2. **Détails&nbsp;:** Inclure autant d'informations que possible sur la vulnérabilité&nbsp;:
+1. **Adresse e-mail&nbsp;:** Envoyez un e-mail à [security@onetimesecret.com](mailto:security@onetimesecret.com?subject=Vulnerability%20Report%3A%20%5BBrief%20Description%5D) avec pour objet «&nbsp;Vulnerability Report: [Brief Description]&nbsp;».
+2. **Détails&nbsp;:** Incluez autant d'informations que possible sur la vulnérabilité&nbsp;:
    - Description détaillée de la vulnérabilité.
@@ -34,4 +34,4 @@
 
-1. **Accusé de réception&nbsp;:** Vous recevrez un accusé de réception dans les 5 jours ouvrables.
-2. **Évaluation initiale&nbsp;:** Nous procéderons à une première évaluation dans un délai de 14 jours ouvrables.
+1. **Accusé de réception&nbsp;:** Vous recevrez un accusé de réception dans les 5 jours ouvrés.
+2. **Évaluation initiale&nbsp;:** Nous procéderons à une première évaluation dans un délai de 14 jours ouvrés.
 3. **Mises à jour&nbsp;:** Vous recevrez des mises à jour sur l'état d'avancement au moins une fois tous les 7 jours jusqu'à ce que le problème soit résolu ou qu'une décision soit prise.
```

## Findings manifest

- Hand edits made after the workflow approved the text (recorded above): verifier warnings applied, nav label kept short, trailing whitespace.
  wont_fix: audit record only; each edit and its reason is listed in website-translation-fr.md and website-translation-de-es.md, so no rule change follows from this file.
