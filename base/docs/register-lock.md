# Rationale — register lock

A locale's register (formality level, pronoun, possessives) is a fixed
linguistic decision, not a per-string stylistic choice. Once locked, every UI
and email string in that locale must honour it. The 2026-04-12 de_AT incident
happened because a register decision was treated as editable text during a
"harmonize" pass. Locking the register at the rule layer — and enforcing it
with `forbidden_tokens` — removes that degree of freedom from string-level work.

Rationale is reference only; the binding statement lives in the rule itself.
