# Rationale — unclosed fence (fixture)

SEEDED — the fence below never closes, so everything after it is blanked.
A bare forbidden token past this point would be silently missed; the gate
must instead fail loudly with `unclosed_code_fence`.

```text
Falsch: du hast ein Geheimnis erstellt
und danach kommt nie ein schließender Zaun — du bleibst sonst unsichtbar.
