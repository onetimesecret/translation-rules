# Rationale — mentions only (fixture)

SEEDED — never address the reader with `du`; that inline code span is a
mention describing the rule, not a use. So is the fenced example below.
Expected: zero findings, lint_ok:true.

```text
Falsch: du hast ein Geheimnis erstellt
Richtig: Sie haben ein Geheimnis erstellt
```
