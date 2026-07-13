# Rationale — terminology consistency

Each product concept maps to one glossary term per sense, used consistently.
Drift between near-synonyms (e.g. the secret *object* vs. its message
*payload*) erodes meaning and was a contributing factor in the 2026-04-12
incident, where the object term was collapsed into the payload term. The
glossary's sense split and disambiguation heuristics are the source of truth
for which term applies in a given context.

## Brand names vs. translatable labels — the anchor test

Not every capitalized English string is a brand name to keep in English. Apply
the **cross-surface anchor test**: a term stays in English only when users meet
it as a fixed identifier across multiple surfaces — UI, URLs, marketing,
billing — so the English form carries recognition worth preserving. *Onetime
Secret* passes: it is the product name, seen everywhere, and an Arabic or
Japanese reader benefits from seeing the same string that appears in the
address bar.

A label that appears on only one surface, is not self-explanatory, and has no
cross-surface anchor fails the test. *Secret Support* — an email-signature-only
sign-off — is the worked example: it reads as jargon unless you already know
the product, and a fully localized email that ends in two English words reads
as an untranslated *leftover*, not a brand signal — most acutely in non-Latin
and RTL locales. Such labels are **translated by meaning**: not kept in
English, and not rendered literally word-for-word. *Secret Support* means *the
Secret product's support team*; a good target conveys that, not a splice that
keeps the English word "Secret" (`Suporte Secret`, `Wsparcie Secret` are wrong
for exactly this reason) and not a collapse onto the generic *Support Team*
rendering, which erases the distinction the source encodes with a separate
`content_hash`.

Encode the decision so it survives parallel authoring: give the term a glossary
entry with an idiomatic-meaning `rationale`, `key_patterns` scoping it to the
keys it governs, and `good`/`bad` examples — the `bad` examples being the exact
partial and collapsed renders to avoid. A decision left in a prose guide gets
re-litigated per agent; a decision in the glossary is enforced by
`rule.terminology-consistency`. See the
`2026-07-02-signature-brand-vs-translatable` retrospective.
