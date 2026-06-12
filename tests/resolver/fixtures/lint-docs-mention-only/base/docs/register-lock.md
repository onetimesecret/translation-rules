# Rationale — mentions only (fixture)

SEEDED — never address the reader with `du`; that inline code span is a
mention describing the rule, not a use. So is the fenced example below.
Multi-backtick spans are mentions too: ``du `und` du`` carries the token
twice inside a double-backtick span with a literal backtick run between.
Expected: zero findings, lint_ok:true.

```text
Falsch: du hast ein Geheimnis erstellt
Richtig: Sie haben ein Geheimnis erstellt
```
