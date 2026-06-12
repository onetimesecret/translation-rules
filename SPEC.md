# Translation Rules — System Design Spec

**Purpose.** Prevent the change-log-as-guidance failure mode and route QA insights into enforceable rules. This repo is the authority for translation guidance; generated artifacts are consumed by translation agents and human translators in the companion app repo (`onetimesecret/onetimesecret`).

**Status.** Draft v1. The target architecture is specified; Phase 0 is shippable immediately. Later phases depend on Phase 0 operating for >1 incident cycle without reversal.

---

## 1. Phase 0 — Minimum Viable Prevention

The single smallest implementation that would have blocked the 2026-04-12 de_AT regression if it had existed at `b08e59838`. Ship this first; everything else is scaffolding around it.

**Artifacts (≈70 lines total):**

- `locales/de_AT/register.yaml` with `forbidden_tokens: [du, dein, deine, deinen, deinem, deiner, dich, dir, euch, euer]` and `form: formal`
- Same file for the three other contaminated locales: `pt_PT`, `uk`, `hu`
- `bin/lint-register` — shell script that greps forbidden tokens against locale content files given a path
- `retrospectives/2026-04-12-de_AT-register-flip.md` with `affected_rules: [register.de_AT.formality]` and `status: applied`
- One-line anti-pattern in the existing UX guide: "harmonize = keys only; never text rewrites"

**Gate (planned — not yet wired; see §2.4 Status).** App repo CI invokes `bin/lint-register` against `locales/content/<locale>/*.json` for every PR that touches locale content. Zero tolerance. PR blocked if any forbidden token appears. This is the load-bearing gate and does not exist in the app repo today.

**Reversibility.** All Phase 0 artifacts are additive. Removing them restores current state.

---

## 2. Target Architecture

### 2.1 Directory layout

```
translation-rules/
├── SPEC.md                              # this file
├── schema/                              # JSON Schema — authoritative contract
│   ├── base.schema.json
│   ├── rules.schema.json
│   ├── register.schema.json
│   ├── glossary.schema.json
│   ├── baselines.schema.json
│   └── retrospective.schema.json
├── base.yaml                            # universal rules
├── base/docs/                           # rationale prose, embedded by resolver
├── baselines.yaml                       # {locale: {commit, invariants, retro_id}}
├── locales/<locale>/
│   ├── rules.yaml
│   ├── register.yaml                    # hard enums (forbidden tokens, formality)
│   ├── glossary.yaml                    # senses + worked examples
│   └── docs/                            # locale rationale prose
├── retrospectives/
│   ├── README.md                        # frontmatter spec + template
│   ├── <date>-<slug>.md                 # YAML frontmatter + prose
│   └── _archive/                        # superseded retros
├── reviews/                             # existing raw QA reviews; preserved as-is
├── _archive/                            # prescriptive/descriptive firewall
├── resolver/
│   ├── resolve.py                       # CLI entry: merge + lint + emit
│   ├── merge.py
│   ├── lint.py
│   ├── emit_markdown.py
│   ├── emit_json.py
│   └── ids.py                           # UUID index + lookup
├── tests/
├── bin/
│   ├── generate-for-translators         # legacy, retired after resolver parity
│   ├── translation-pluribus-util        # kept: external translator roundtrip
│   ├── lint-register                    # Phase 0 shim
│   └── mint-id                          # generates stable UUIDs
└── .github/workflows/
```

Two `_archive/` directories with distinct purposes. `retrospectives/_archive/` holds superseded retros. Top-level `_archive/` is the prescriptive-vs-descriptive firewall: anything inside is never compiled into output. Moving a file out of `_archive/` is a reviewable diff requiring explicit label approval.

### 2.2 File formats

**YAML as source, JSON Schema as contract.** Schema is authoritative; YAML is the human-authored surface validated at resolver entry. Alternatives rejected: JSON-as-source (too noisy for prose fields), YAML-without-schema (implicit coercion is exactly the drift vector the system exists to prevent).

Minimal `register.yaml`:

```yaml
id: register.de_AT
form: formal
pronoun: Sie
possessive: [Ihr, Ihre, Ihren, Ihrem, Ihrer]
forbidden_tokens:
  - { token: du,   context: standalone_word, severity: error }
  - { token: dein, context: word_prefix,     severity: error }
  - { token: dich, context: standalone_word, severity: error }
  - { token: dir,  context: standalone_word, severity: error }
exceptions: []                           # required field, may be empty list
rule_ref: register.de_AT.formality
baseline_ref: baselines.de_AT
retro_refs: [2026-04-12-de_AT-register-flip]
```

Minimal `glossary.yaml` entry with sense split:

```yaml
id: glossary.de_AT
terms:
  - id: term.secret_object#7f3a91c2
    key: secret_object
    en: secret
    de_AT: Geheimnis
    disambiguation:
      heuristic: "Lifecycle verb (create/share/burn/expire) → object"
      key_patterns: ["*.burn*", "*.share*", "*.expire*"]
    examples:
      - id: ex.burn#a12b45ef
        source: "Burn this secret"
        target: "Dieses Geheimnis verbrennen"
        verdict: good
        rule_refs: [register.de_AT.formality, glossary.de.object-content-split]
```

Schemas forbid `null` where an empty list or explicit absence field is required. Dangling `rule_refs` are a hard error at resolve time.

### 2.3 Resolver mechanics

**Implementation language:** Python 3.11+ (matches existing `bin/*` tooling; uses `jsonschema` for validation and `PyYAML` for parsing).

**Output commit policy:** Generated artifacts (`for-translators/<locale>.md` and `.resolved/<locale>.json`) are committed to the app repo, not CI-generated-only. This is required for the file-hash CI check in §2.4 to have a baseline to compare against, and so translators and external reviewers can browse the current guide without running the resolver.

`resolver/resolve.py <locale> [--lint] [--emit=md,json] [--all]` drives everything:

1. **Load + schema-validate.** Reject malformed input at this boundary.
2. **Compute inheritance chain.** `de_AT → de → base`. Cycle-detected.
3. **Merge.** Deep-merge for maps, replace for scalars, `merge_strategy` for lists (`append | replace | prepend | dedup`). Record per-key provenance.
4. **Resolve IDs.** Build UUID→path→key index. Dangling refs fail here.
5. **Attach retros.** Applied retrospectives fold metadata into referenced rules.
6. **Lint.** Examples must pass their own register lint. Forbidden tokens must be absent from embedded docs. Every example's target must match its sense's target (substring/morphological).
7. **Emit.** Two outputs:
   - Markdown: `onetimesecret/locales/guides/for-translators/<locale>.md`, headed `# GENERATED from translation-rules@<sha> — do not edit, do not cite as source`
   - JSON: `onetimesecret/locales/.resolved/<locale>.json` — stable key order, `_meta.source_commit` carries the pin

**Resolved JSON shape is indexed for agent consumption** — partitioned by the decisions an agent makes at translation time, not by severity:

```yaml
_meta: { source_commit, schema_version, generated_at }
register: { form, pronoun, forbidden_tokens, rule_ref }
glossary:
  <term>:
    en: <source>
    senses: { <sense>: { target, rule_ref } }
    examples: [...]   # term-level (not sense-nested); each annotated with the
                      # senses its target matches. See resolver/model.py header.
rules: [...]        # MUST/MUST NOT items, severity, rule_ref
context: [...]      # project-specific info, not binding
rationale_index: { rule_id: [doc_paths] }   # fetch on demand
declined_index: [...]                        # per-locale decline summaries
anti_patterns_ref: [...]
```

The `rules`/`context`/`rationale` partition is the surface-level cue that prevents the change-log-as-guidance failure. Only `rules` and `register` bind behavior. Conversational prose cannot reach the `rules` partition without passing through a human-authored YAML file with a schema.

### 2.4 CI gates

**Status (2026-06-12).** Implemented: `schema-validation.yml` (schema, inheritance, resolver merge/lint/emit tests, retro lifecycle gate), `lint-register.yml` (a `--dry-run` plumbing self-test plus `tests/lint-register.sh`), `python-qc.yml` (ruff lint/format, pyright), `publish.yml` (release tagging on main merge), and the §3 retrospective lifecycle gates (`resolver/retro_lifecycle.py`: 7-day orphan timeout, applied-transition diff check, archive-firewall egress detection). Embedded-docs forbidden-token lint (`resolver/lint_embedded.py`) is wired into `schema-validation.yml`. Still planned in this repo: review findings-manifest validation. Every gate in the App-repo block is **planned** — including the load-bearing one (app-repo forbidden-token grep against real content). No app-repo integration exists yet (no submodule, no content gate). Phases below depend on these landing.

**App repo (planned — none built):** submodule pointer freshness on locale-content PRs; `.resolved/<locale>.json`'s `_meta.source_commit` equals submodule SHA; `forbidden_tokens` grep against `locales/content/<locale>/*.json`; `for-translators/*.md` hash matches resolver output — hand edits rejected.

**Cross-repo pipeline gate (planned).** A locale content PR is blocked unless the submodule is current, resolved JSON was regenerated in the same PR, and lint passes. This is what mechanically prevents the next class of "bypass by direct edit."

**How the 2026-04 failure mode is mechanically prevented (by design — see Status above for what is wired today):**
1. Change-log-style prose physically lives in `_archive/` or `retrospectives/` — neither is compiled into output.
2. `for-translators/*.md` is generated and hash-locked. A report cannot be pasted in.
3. Rules are YAML with schema. Prose cannot reach the `rules` partition without authoring a schema-valid file.

---

## 3. Feedback Cycle

The critical ask. Every edge labeled machine-enforced or human-in-the-loop.

**Status (2026-06-12).** The 7-day orphan timeout and the applied-transition PR check are wired (`resolver/retro_lifecycle.py`, run by `schema-validation.yml`; one pre-existing pending retro carries an explicit, per-id grace in the workflow until its cross-repo closure lands). Still not wired: retro→applied automation on merge, and the cross-repo lint/hash gates — see §2.4 Status. Read the remaining `[CI-ENFORCED: ...]` annotations accordingly.

```
            (incident signal OR scheduled audit)
                        │ [HUMAN]
                        ▼
                ┌────────────────┐
                │ raw QA review  │  stored as-is in reviews/<date>/
                │ (prose)        │  [HUMAN writes; no schema]
                └────────────────┘
                        │ [HUMAN files retro; review document must
                        │  end with a findings manifest listing
                        │  retro_id or wont_fix per finding]
                        ▼
                ┌────────────────┐
                │ retrospective  │  schema-validated frontmatter
                │ status: pending│  [CI: schema, ref resolution]
                └────────────────┘
                        │ [CI-ENFORCED: 7-day orphan timeout;
                        │  applied transition requires PR that
                        │  also edits every id in affected_rules]
                        ▼
                ┌────────────────┐
                │ rule change PR │  touches affected_rules
                │ (YAML edits)   │  [CI: schema, resolver tests,
                └────────────────┘   lint against resolved tree]
                        │ [CI-ENFORCED: retro → applied on merge]
                        ▼
                ┌────────────────┐
                │ app repo bump  │  submodule advances;
                │ PR (scheduled) │  resolver regenerates artifacts
                └────────────────┘  [MACHINE opens, HUMAN approves]
                        │ [CI: full lint against current locale
                        │  content; hash match on generated files]
                        ▼
                ┌────────────────┐
                │ resolved       │  for-translators/<locale>.md
                │ artifacts      │  .resolved/<locale>.json
                └────────────────┘  [consumed read-only by agents
                        │            and human translators]
                        ▼
            (next audit cycle, loop)
```

**Retrospective lifecycle states:** `pending | applied | declined | superseded`.

- `pending → applied`: requires PR to also touch every ID in `affected_rules` and populate `resolved_in_commit`. CI-enforced.
- `pending → declined`: requires `declined_reason` and `would_change_decision_if` fields. Human-gated.
- `applied → superseded`: only via a newer retro whose `supersedes` list contains this id.
- `pending` with no transition after 7 days blocks next main PR. A retro whose closure is blocked on work outside this repo may carry an explicit per-id waiver in the CI workflow (`--grace <retro-id>`): the overdue retro then reports as a non-fatal warning, the waiver itself is a reviewable diff, and the gate flags the waiver as stale once the retro leaves `pending`.

**Declined retros stay as active guardrails** (not archived). Resolver emits per-locale decline index surfacing summaries to agents. Before an agent proposes changing a locale's register or glossary, it checks the decline index — if covered, the agent must either match a `would_change_decision_if` condition or escalate.

**Existing `reviews/` directories remain as-is.** Historical QA reviews are preserved as raw input; no backfill into retrospective format. New incidents file retrospectives in `retrospectives/`. Unactioned findings in existing reviews are triaged opportunistically into new retrospectives when touched.

**Every new review document must end with a findings manifest** — a bulleted list where each item maps to a retrospective id or `wont_fix` tag with reasoning. CI checks: for each review doc, every finding has a tracking tag. Prevents the "insights die in prose" failure that produced the current unactioned state.

---

## 4. Pluribus Integration

`translation-pluribus-util` is not replaced by the resolver. Two integration points:

**UUID pattern for stable IDs.** Adopt pluribus's 8-char-UUID scheme for rename-survivable identity. Every rule, term, example, and retrospective carries a stable ID of the form `<kind>.<key>#<8char>` (e.g., `term.secret_object#7f3a91c2`, `ex.burn#a12b45ef`, `rule.register-lock#c81d44e0`). The human-readable key is the grep target; the 8-char suffix survives renames, file moves, and reorganizations. `bin/mint-id` generates them on first authoring. The resolver emits `resolver/index.json` committed to the repo so both grep-by-key and grep-by-id remain fast.

**Bundle/split for cross-locale operations.** Pluribus's prepare → combine → split → restore pipeline maps onto cross-locale review workflows:

- `resolve.py --all --emit=bundle` produces a single combined JSON with UUID-delimited locale sections, suitable for sending to an external review service (human native-speaker audit across multiple locales) or loading into an agent context for cross-locale consistency checks.
- `resolve.py --split <bundle>` restores per-locale JSONs, tolerant of filename mangling because locale identity is carried in the delimiter, not the filename.

This is how the system "works with app repo sources" per the user's brief: pluribus roundtrip for source English strings stays intact; the rule system uses pluribus patterns (UUIDs, bundle/split) internally for cross-locale artifact operations.

**Two distinct ID namespaces.** Pluribus file-mapping IDs are short-lived (one translation batch). Rule-system IDs are permanent. Do not cross them.

---

## 5. Contract with the `saas-translator` Skill

The skill lives in `~/.claude/skills/saas-translator/` — out of this repo's reach. The contract is narrow and explicit:

- Skill reads `onetimesecret/locales/.resolved/<locale>.json` for binding rules.
- Skill reads `onetimesecret/locales/guides/for-translators/<locale>.md` only as human-readable reference. Never parses it as rule source.
- Skill never writes into `onetimesecret/locales/.resolved/` or `translation-rules/`. Findings are filed by a human as retrospectives or as agent proposals at `retrospectives/<date>-proposed-<slug>.md` with `status: pending` — the status transition to `applied` is always human-gated.

The eight diagnosed gaps in `reviews/2026-04-12/advice-for-saas-translator-skill.md` are addressed either by this system (gaps 1, 2, 5, 6) or by skill changes tracked outside this repo (gaps 3, 4, 7, 8). The skill's own updates are tracked in a separate retrospective per gap.

---

## 6. Downstream Execution Integration

The rule system produces artifacts; two existing workflows consume them. Design choices for the resolved outputs are constrained by what these consumers need.

### 6.1 Translator agent workflow (`start-translation-session`)

`/d:start-translation-session` orchestrates up to 5 parallel background `saas-translator` agents. Each agent claims per-string tasks from the app repo's SQLite task DB (`onetimesecret/locales/scripts/tasks/*.py`), translates, updates task status. The command currently inlines a "Locale Conventions Reference" table in its prompt text — hand-maintained, duplicative, and itself a drift vector (the table's entry for `de` says `informal "du"`, the same class of error as the 2026-04-12 incident).

**Post-Phase 1 contract:**
- Agent prompts load `onetimesecret/locales/.resolved/<locale>.json` as the single source for register, glossary, rules, and declined decisions.
- The inlined conventions table is removed from the command; agents rely only on resolved JSON.
- The resolved JSON shape (§2.3) is indexed by the decisions an agent makes at translation time — register lookup, term sense disambiguation, anti-pattern checks — so agents don't need to re-merge sources at read time.

**Design constraint this places on the resolver:**
- Output must be small enough to fit comfortably in a prompt alongside the claimed task (target: under 20 KB per locale).
- Key paths in resolved JSON must be greppable by human-readable names, not just UUIDs.
- `_meta.source_commit` must be machine-parseable so agents can detect stale context.

### 6.2 Migration execution workflow (`work-tasks-db`)

`/d:work-tasks-db` runs parallel agents against a SQLite task DB with modulo-based sharding (`id % agent_count = agent_index` — no lock contention). This is how the Phase 2 fan-out to 34 locales will run: one task per locale, shard N ways, agents claim and resolve independently.

**Design constraint this places on the locale conversion work:**
- Each per-locale migration ticket must be self-contained. Task description carries the template; no cross-ticket state.
- The migration from prose (`glossary.md`, `language-notes.md`) to YAML must be executable by a `general-purpose` or `saas-translator` agent given only the ticket, the resolver schema, and the per-locale source files.
- Resolver lint must produce a clear pass/fail so agents know when a locale conversion is done.

### 6.3 Two task DBs, distinct scopes

- **App repo task DB** (`locales/scripts/tasks/*.py`): per-string translation work; consumed by `start-translation-session`.
- **Rule system migration DB** (`.claude/tasks/<name>.db`): implementation work items; consumed by `/d:work-tasks-db`.

Neither is part of this repo's design. Both are execution substrate. No cross-referencing between them.

### 6.4 Drift finding already identified

`/Users/d/.claude/commands/d/start-translation-session.md` lines 124-139 contain a "Locale Conventions Reference" table that has already drifted from current guidance for the de family. Filing a retrospective for this is a Phase 0 side task — same failure pattern as the original incident, different location.

## 7. Migration Path

**Phase 0 (this week).** Four `register.yaml` files, one shell lint, one retrospective. See §1.

**Phase 1 (MVP end-to-end for de_AT).**

1. Land `schema/` and `resolver/` skeletons.
2. Write `base.yaml` by absorbing mechanical rules from existing UX and security guides. Leave rationale in `base/docs/`.
3. Hand-convert `locales/de_AT/{rules,register,glossary}.yaml`. Draft `locales/de/rules.yaml` as inheritance parent.
4. Implement merge + lint + emit. Test fixtures for de → de_AT.
5. Move existing `reviews/2026-04-12/` retrospective content into new `retrospectives/` format with validated frontmatter. Preserve raw reviews/.
6. Move `de-translation-notes.txt` into `_archive/`. Reversibility checkpoint: no app repo change yet.
7. Add the submodule in the app repo. Run resolver. Regenerate de_AT artifacts. Observe lint flags known violations.
8. Fix content or log exceptions. Lint goes green.

**Reversibility checkpoint** — only de_AT is in the new system. Other locales still use frozen guides.

**Phase 2 (fan-out).**

9. de, then pt_PT / uk / hu (other contaminated locales), then da_DK / zh (lighter).
10. Remaining 28 locales. Mostly mechanical — `locale → base` without intermediate tier.
11. Retire `bin/generate-for-translators`. Keep `translation-pluribus-util`.

**Phase 2 note on existing `local-guides/for-translators/*.md`.** The 35 frozen files contain prose glossary tables and language notes not yet in YAML. One-way conversion prose → YAML schema is significant per-locale work. It happens per-locale as part of each locale's Phase 2 migration — not bundled, not automated.

---

## 8. Out of Scope (v1)

Each deferred with rationale; revisit after Phase 1 ships.

- **Language-groups layer** (e.g., pt_PT + pt_BR sharing decisions). Adds complexity before earning value. Handle cross-locale coordination via retrospectives until a concrete pattern emerges.
- **Authorities subsystem** (OQLF, etc.). Encode as a flat `authority_refs: [OQLF]` field in `register.yaml` when fr_CA is touched. Don't build a subsystem up front.
- **Per-key baseline checkpoints.** File-level baselines suffice until we hit a revert that throws out legitimate work.
- **Non-binary register** (ja keigo, ko politeness levels). Extend `register.yaml` schema with a free-form `register_spec:` field when the first CJK locale is touched.
- **Cold-start template for new locales.** Manual bootstrap is acceptable through locale #40.
- **Retrospective pruning cadence.** Revisit when the directory exceeds 50 entries.
- **Agent-filed retrospectives.** Proposed retros from agents are accepted as PRs with `status: pending`; humans own all transitions. No automation beyond this.

---

## 9. Known Failure Modes the Design Does Not Handle

Flagged for honesty, not solved.

- **Direct edits to uncommitted resolved files** — a developer pastes into `.resolved/<locale>.json` locally. CI catches commits; local agent runs don't. Pre-commit hook is the partial mitigation.
- **Agents that ignore the `# GENERATED` header.** The header is a hint. An agent round-tripping through an edit surfaces only at CI time.
- **Changes to English source strings** bypass this repo entirely. A new interpolation variable only surfaces at resolver run in the app repo.
- **Retrospective fatigue.** If every finding requires a retro, friction discourages filing. Short-form retros (three sentences) are the answer; adoption depends on ergonomic `bin/mint-retro` tooling not specified here.
- **Cross-rule interaction bugs.** Lint asserts per-rule. Interactions ("if register is formal AND term has a legal variant, use the legal variant") require a richer lint language.
- **Submodule update lag.** Between rule merge and app repo bump, there's a window where lint runs against stale rules. Scheduled bump PRs reduce but do not eliminate it.
