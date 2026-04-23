title: Update Language Translation Notes
description: Copy-paste this prompt when updating translation notes for any language:
---

Update `src/content/docs/{LANG}/translations/language-notes.md` for **{LANGUAGE_NAME}**.

**Rules:**
1. Include ONLY mistakes translators actually make
2. Show correct ✓ vs incorrect ✗ examples
3. One sentence max per rule (or zero)
4. Must be readable in 20 seconds (25-50 lines max)
5. No overview, no explanations, no fluff

**Include:**
- Critical terminology (word choice that breaks meaning)
- Context rules (buttons vs headings use different forms)
- Technical requirements (punctuation that breaks rendering)
- Date/time formats (standard)
- Capitalization
- Consequential regional variations

**Exclude:**
- Long descriptions


**Before saving, verify:**
- [ ] 25-50 lines total
- [ ] ~20 second read time
- [ ] Every rule prevents actual mistakes
- [ ] No duplicate content from glossary

---

Example input: "For Spanish, translators keep using 'secreto' instead of 'mensaje secreto' for UI elements, and they mix up imperative vs infinitive forms in buttons."

Example output:

```markdown
| Rule | Correct | Incorrect | Example |
|------|---------|-----------|---------|
| "Secreto" → "Mensaje secreto" | mensaje secreto | secreto | ✓ Tienes 3 mensajes secretos nuevos; ✗ Tienes 3 secretos nuevos |
| Botones: Imperativo | Crear, Compartir, Eliminar (buttons); Creación, Compartir, Eliminación (titles) | Mixed forms | ✓ Crear secreto (button); ✗ Creación de secreto (button) |
```
