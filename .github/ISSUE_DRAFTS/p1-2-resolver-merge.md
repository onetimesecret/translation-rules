## Title
P1-2 — Resolver skeleton + merge algorithm

## Labels
`phase-1`, `translation-rules`, `resolver`

---

## Context

`SPEC.md` §2.3 specifies the resolver's seven-step pipeline: load + schema-validate → inheritance chain → merge → resolve IDs → attach retros → lint → emit. This ticket covers steps 1–4 (through ID resolution). Emit is P1-3.

## Acceptance criteria

- [ ] `resolver/` directory with package structure (`__init__.py`, `resolve.py` CLI, `merge.py`, `ids.py`)
- [ ] `resolve.py` accepts `<locale>` positional arg and `--validate-only`, `--locales-dir`, `--base-file` flags
- [ ] Step 1 (load + schema-validate): loads `base.yaml` and every `locales/<locale>/*.yaml` in the inheritance chain; validates each against its schema from P1-1; rejects malformed input with clear messages
- [ ] Step 2 (inheritance chain): follows `inherits:` keys; detects cycles; rejects undefined parents
- [ ] Step 3 (merge): deep-merge for maps; replace for scalars; `merge_strategy` for lists (`append | replace | prepend | dedup`, default `replace`); records per-key provenance in a `_provenance` sidecar
- [ ] Step 4 (resolve IDs): builds UUID/path index; every `rule_refs`, `affected_rules`, `retro_refs` resolves to a concrete node; dangling refs are hard errors
- [ ] `resolver/index.json` (inside the `resolver/` directory, per `SPEC.md` §4) is emitted, regenerated on every run, committed (so grep-by-key and grep-by-id both work without running the resolver)
- [ ] `resolver/ids.py` owns the UUID minting logic (8-char hex, deterministic from a `<kind>.<key>` seed or random with collision check against `index.json`)
- [ ] `bin/mint-id <kind> <key>` is a thin CLI wrapper over `resolver/ids.py` for human authors minting ids during P1-5 and beyond. Prints `<kind>.<key>#<8char>` to stdout.
- [ ] Test fixtures in `tests/inheritance/` cover: de_AT → de → base chain; cycle detection; merge strategies; dangling ref detection

## Dependencies

- Blocked by P1-1 (needs schemas)
- Blocks P1-3 (emit), P1-5 (de_AT end-to-end)

## Out of scope

- Emit logic (P1-3)
- Lint assertions beyond ID resolution (P1-3 or later)

## Implementation

Python 3.11+ per `SPEC.md` §2.3. Use `PyYAML` for parsing and `jsonschema` for validation.

## Estimated effort

12–20 hours. Merge algorithm with provenance tracking is the long pole.

## Verification

Given `locales/de_AT/*.yaml` + `locales/de/rules.yaml` + `base.yaml` from P0-1 and P1-5 drafts, `resolve.py de_AT --validate-only` exits zero and prints the merged tree to stdout.
