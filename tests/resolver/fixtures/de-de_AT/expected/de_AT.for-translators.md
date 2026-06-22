# GENERATED from translation-rules@TESTSHA0 — do not edit, do not cite as source

Locale: `de_AT` · schema v1

## Register

- Form: **formal**
- Pronoun: `Sie`
- Possessive: `Ihr`, `Ihres`
- Forbidden tokens:
  - `du` (standalone_word, error) — informal pronoun; de_AT is locked to formal Sie
- Exceptions:
  - `Duden` — proper noun (the German dictionary); contains the 'du' substring

## Glossary

### link (en: link)
- _noun_: **Link**
  - ✓ Open the link to view your secret. → Öffnen Sie den Link, um Ihr Geheimnis anzuzeigen.
### secret_object (en: secret)
- _noun_: **Geheimnis**
  - ✓ Your secret has been created. → Ihr Geheimnis wurde erstellt.
  - ✓ The secret's link has expired. → Der Link des Geheimnisses ist abgelaufen.
  - ✗ Your secret has been created. → Dein Geheimnis wurde erstellt.

## Rules (binding)

- **MUST** (error): Use the locale's locked register form in all UI and email content. `[rule.register-lock]`
- **MUST** (error): German content uses the formal Sie form. `[rule.de-sie]`
- **MUST** (error): de_AT uses the formal Sie-form throughout product UI and email content. `[rule.de_AT-formality]`

## Context (non-binding)

- Generated artifact; do not edit by hand.
- [SHOULD] Prefer concise phrasing where meaning is preserved.

## Anti-patterns

- Do not treat change-log prose as translation guidance. `[anti.changelog-as-guidance]`

## Declined decisions (active guardrails)

- `2026-05-01-decline-du-for-marketing`: Marketing requested informal du; rejected to keep register consistent across UI and email.
  - would change if: A native-speaker audit shows the formal Sie-form measurably harms conversion.
