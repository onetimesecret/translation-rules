## Title
P1-1 — JSON Schema files for all six YAML types

## Labels
`phase-1`, `translation-rules`, `schema`

---

## Context

`SPEC.md` §2.2 specifies YAML-as-source, JSON-Schema-as-contract. The schemas are the authoritative definition of what every rule file can and cannot contain. Without them, the YAML is just prose and the resolver has no stable validation point.

## Acceptance criteria

- [ ] `schema/base.schema.json` — universal rules structure
- [ ] `schema/rules.schema.json` — locale rules with `inherits:` and `merge_strategy:`
- [ ] `schema/register.schema.json` — register lock with `form`, `pronoun`, `forbidden_tokens`, `exceptions` (list, possibly empty but never null), and a `source:` field (string or null, required) documenting where the token set was derived — e.g., `SPEC.md#1`, a `reviews/<date>/` path, or `native-speaker:<initials>`. Per-entry `source:` on individual `forbidden_tokens` items is optional and overrides file-level when present.
- [ ] `schema/glossary.schema.json` — terms and worked examples with sense split and `rule_refs`
- [ ] `schema/baselines.schema.json` — commit pins requiring `retro_id` OR `justification_doc` (one of two)
- [ ] `schema/retrospective.schema.json` — frontmatter with status lifecycle enum (`pending | applied | declined | superseded`)
- [ ] Each schema uses `$schema: https://json-schema.org/draft/2020-12/schema` and validates successfully against at least one hand-written example
- [ ] Schemas reject the specific failure cases documented in `SPEC.md` §2.2 (e.g., `forbidden_tokens: null`, missing `exceptions`)
- [ ] A `tests/schema/` directory contains at least one positive and one negative fixture per schema

## ID format

Mixed-mode per `SPEC.md` §2.2 and §4:
- `rules.yaml`, `register.yaml`, `baselines.yaml`, retrospective `id:` — dotted path regex
- `glossary.yaml` term and example `id:` — `^<kind>\.<key>#[0-9a-f]{8}$` regex

Schemas enforce the right format per file type.

## Dependencies

- None. (All prior open decisions resolved in SPEC.md.)
- Blocks P1-2 (resolver needs schemas to validate inputs).

## Out of scope

- Extensions to the schema for Phase 2 concerns (language-groups layer, non-binary register like ja keigo). Document as TODOs in schema comments if the shape is obvious; otherwise defer entirely.
- Cross-schema validation (`rule_refs` resolution happens in the resolver, not the schema).

## Estimated effort

6–10 hours including fixtures. Schema drafting is tedious; the fixtures are the test.

## Verification

- Valid P0-1 `register.yaml` files validate against `register.schema.json`.
- Invalid fixtures (e.g., `forbidden_tokens: null`, missing `exceptions`) fail validation with clear error messages.
