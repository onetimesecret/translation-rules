# Translation Rules

Authority for translation guidance: rules, registers, and terminology definitions that prevent the change-log-as-guidance failure mode.

## Quick Start

**For translator agents & humans using this repo's generated artifacts:**

This is the authoritative source. The resolver pipeline (SPEC §2.3) produces two outputs consumed by the app (`onetimesecret/onetimesecret`):

1. **Markdown guides**: `locales/guides/for-translators/<locale>.md`
   - Human-readable reference for translators
   - Auto-generated; do not edit
   - **Source of truth**: rules, registers, glossaries in this repo

2. **JSON artifacts**: `locales/.resolved/<locale>.json`
   - Machine-readable structure indexed for agent decision-making
   - Includes `_meta.source_commit`: pinned to submodule SHA for verification
   - Partitioned by translator-time decisions: register (formality/pronouns), glossary (term senses), rules (constraints)

## For Maintainers & Developers

### Directory Layout

```
translation-rules/
├── SPEC.md                        # System design spec (§1-7)
├── README.md                      # This file
├── BACKLOG.md                     # Deferred features
│
├── base.yaml                      # Universal rules (all locales)
├── base/docs/                     # Universal rationale prose
├── schema/                        # JSON schemas (authority contracts)
├── baselines.yaml                 # Per-locale snapshot pins + invariants
│
├── locales/<locale>/
│   ├── rules.yaml                 # Locale-specific rules (inherits base)
│   ├── register.yaml              # Formality, pronouns, forbidden tokens
│   ├── glossary.yaml              # Term definitions + worked examples
│   └── docs/                      # Locale-specific rationale
│
├── retrospectives/                # QA feedback tracker (SPEC §3)
│   ├── <date>-<slug>.md           # Incident/audit record (YAML frontmatter + prose)
│   └── _archive/                  # Superseded retrospectives
│
├── reviews/                       # Raw QA reviews (preserved as-is)
│
├── _archive/                      # Prescriptive/descriptive firewall
│                                  # (files here are never compiled)
│
├── bin/lint-register              # Phase 0 register-token validator
├── resolver/                      # 7-step resolver pipeline
│   ├── resolve.py                 # Entry point
│   ├── loader.py                  # Load + schema-validate
│   ├── validate.py                # Schema bundle
│   ├── inheritance.py             # Build inheritance chain
│   ├── merge.py                   # Deep-merge with provenance
│   ├── ids.py                     # UUID/dotted/retro ID index
│   ├── model.py                   # Assemble model
│   ├── lint.py                    # Lint examples (forbidden tokens, sense targets)
│   ├── lint_embedded.py           # Lint docs (forbidden tokens)
│   ├── retro_lifecycle.py         # Lifecycle gate (orphan timeout, transitions)
│   ├── emit_json.py               # Emit .resolved/<locale>.json
│   └── emit_markdown.py           # Emit guides/for-translators/<locale>.md
│
├── tests/                         # Pure-function test harnesses (no fixtures)
│   ├── schema/run.py              # Schema validation tests
│   ├── inheritance/run.py         # Inheritance chain tests
│   ├── resolver/run.py            # Full resolver pipeline tests
│   └── retro_lifecycle/run.py     # Retrospective lifecycle gate tests
│
├── .github/workflows/
│   ├── schema-validation.yml      # CI: schema + resolver + retro gates (PR + main)
│   ├── python-qc.yml              # CI: ruff format + pyright (PR + main)
│   ├── publish.yml                # CI: tag releases on main merge
│   └── ISSUE_DRAFTS/              # Planned workflows (deployment docs)
│
└── local-guides/                  # Existing raw guides (being migrated)
```

Two `_archive/` directories with distinct purposes:
- `retrospectives/_archive/`: superseded retrospectives (former live issues)
- Top-level `_archive/`: **prescriptive/descriptive firewall** — moving a file out requires explicit approval (SPEC §2.1)

### Resolver Pipeline

Input → Validation → Inheritance → Merge → ID Resolution → Attach Retros → Lint → Output

1. **Load + schema-validate** — YAML against `schema/*.schema.json`
2. **Inheritance chain** — `de_AT → de → base`; cycle detection
3. **Merge** — deep-merge with per-key provenance tracking
4. **Resolve IDs** — UUID→path index; dangling ref detection
5. **Attach retros** — applied retrospectives fold metadata into rules
6. **Lint** — examples forbidden-token check; docs absence check
7. **Emit** — Markdown guides + JSON artifacts

Exit codes: 0 success · 1 validation/resolution error · 2 setup error

### CI Pipeline

**`schema-validation.yml`** (PR + main push)
- Schema fixture suite (34 test cases)
- Inheritance chain tests (9 cases)
- Resolver pipeline tests (6 cases)
- Retrospective lifecycle tests (19 cases)
- Embedded-docs forbidden-token lint
- Retrospective lifecycle gate: orphan timeout (7 days), applied transitions, stale grace waivers

**`python-qc.yml`** (PR + main push)
- `ruff check .` — lint all Python
- `pyright .` — type check

**`publish.yml`** (main push only)
- Creates git tag `v0.0.N` on successful merge
- Tag message includes commit SHA for submodule pinning

### Submodule Integration (App Repo)

The app repo (`onetimesecret/onetimesecret`) consumes this as a submodule:

```bash
git submodule add https://github.com/onetimesecret/translation-rules locales/translation-rules
git submodule update --init --recursive
```

**Contract:**

1. **Submodule pointer is fresh** — app repo CI checks that submodule is current (no drift)
2. **Resolved artifacts match submodule commit** — `.resolved/<locale>.json`'s `_meta.source_commit` equals submodule SHA
3. **Register tokens enforced** — CI grepped against `locales/content/<locale>/*.json` before merge (Phase 0 prevention gate)
4. **Generated guides hash-locked** — `for-translators/<locale>.md` hash matched by CI; hand edits rejected

### Retrospective Lifecycle (SPEC §3)

Four-state machine: `pending → applied | declined | superseded`

- **`pending`** — new issue filed, awaiting closure on any status
- **`applied`** — rules were changed in response; PR must touch every `affected_rules` id
- **`declined`** — investigation concluded no rule change needed; includes `declined_reason`
- **`superseded`** — newer retro closes the old one; links recorded via `supersedes` field

**CI enforcement:**
- `pending` > 7 days blocks next main PR (unless graced via `--grace` in workflow)
- `applied` transition requires PR that also edits every `affected_rules` id
- Grace waivers are per-id, visible in workflow file, auto-detected as stale

### Running Locally

```bash
# Validate a single locale (resolve.py)
python resolver/resolve.py de_AT

# Validate all YAML against schemas
python tests/schema/run.py

# Run full resolver test suite
python tests/resolver/run.py

# Check retrospective lifecycle (requires git history)
python resolver/retro_lifecycle.py --diff-base origin/main

# Lint embedded docs (base/docs/, locale docs)
python resolver/lint_embedded.py
```

### Making Changes

**Add/modify rules:**
- Edit `base.yaml` or `locales/<locale>/rules.yaml`
- Run `python resolver/resolve.py <locale>` to validate
- CI will run full schema + resolver suite on PR

**Add/modify glossary terms:**
- Edit `locales/<locale>/glossary.yaml`
- Examples marked `verdict: good` must not contain `forbidden_tokens` from that locale's register
- Run tests before commit

**File a retrospective:**
- Create `retrospectives/<date>-<slug>.md` with YAML frontmatter
- Schema-validated frontmatter required; prose is reference only
- Set `status: pending` initially
- CI enforces 7-day orphan timeout; file a PR transitioning to `applied` or `declined` before timeout

**Promote a file from `_archive/`:**
- Moving any file out of `_archive/` is a reviewable diff requiring explicit approval
- Archive firewall blocks egress without review

## Dependencies

- Python 3.11+
- `pyyaml>=6,<7` — load YAML
- `jsonschema>=4.21,<5` + `referencing>=0.32,<1` — schema validation
- Git (for retro lifecycle gate)

## Status

Phase 1 implementation in progress (as of 2026-06-12):

- ✓ Phase 0 (register forbidden-token prevention gate) shippable; app repo integration pending (P1-4b)
- ✓ Schemas (P1-1), resolver pipeline (P1-2/P1-3), retrospective lifecycle (P1-4a §3)
- ✓ Embedded-docs forbidden-token lint, archive firewall detection
- ⚠ Findings-manifest validation (deferred)
- ⚠ Retrospective lifecycle automation on merge (deferred; cross-repo work blocking)

## For Questions

See SPEC.md for design rationale. See individual `.md` files in `retrospectives/` and `reviews/` for decision context and incident details.
