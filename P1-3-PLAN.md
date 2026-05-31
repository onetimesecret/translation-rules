# P1-3 Implementation Plan — Resolver lint + dual emit

**Status.** Plan for review. Implements SPEC §2.3 steps 5–7 on top of P1-2 (steps 1–4, committed). No code yet.

**Why it blocks everything.** Both cross-property decisions (HANDOFF, 2026-05-29) wait on this: the guidance-source inversion is "first act of Phase 1.5, *after* P1-3 emit," and every property consumes `.resolved/<locale>.json` — which only exists once emit lands.

---

## 1. What exists vs. what P1-3 adds

`resolve.py` runs SPEC steps 1–4: load+validate → inheritance chain → merge w/ provenance → ID resolution + `index.json`. It stops there. Retros are loaded and ref-checked but **not folded into rules** (step 5 is a stub).

P1-3 adds steps 5–7 and two CLI flags. New modules per SPEC tree (§ lines 58–60):

| Module | SPEC step | Responsibility |
|---|---|---|
| `resolver/retros.py` *(or fold into resolve)* | 5 | Attach applied retrospectives: fold their metadata into referenced rules; build `declined_index` from declined retros |
| `resolver/lint.py` | 6 | Three assertions (below). Returns structured pass/fail (SPEC §3 line 282: "clear pass/fail so agents know when a locale conversion is done") |
| `resolver/emit_json.py` | 7b | `.resolved/<locale>.json` in the §2.3 indexed shape, stable key order, `_meta.source_commit` pin |
| `resolver/emit_markdown.py` | 7a | `for-translators/<locale>.md`, `GENERATED from …@<sha>` header, hash-stable |

CLI: `resolve.py <locale> [--lint] [--emit=md,json] [--all]`. `--validate-only` stays.

---

## 2. The two gaps that need a decision before coding

### Gap A — "morphological match" (SPEC step 6, item 3)

SPEC: *"Every example's target must match its sense's target (substring/morphological)."* "Morphological" is undefined and German inflects ("Geheimnis" → genitive "Geheimnisses"), so naive substring fails on `good` examples.

**Proposal: do not invent stemming. Reuse the existing `forbiddenToken.context` enum** (`standalone_word | word_prefix | substring | any`), which the schema already defines for exactly this matching problem. The example-target check:

- Only `verdict: good` examples are checked for *presence* of the sense target. `bad` and `borderline` are **not** content-linted here (see below) — they are covered only by the independent forbidden-token pass.
- The match mode is the open question. `word_prefix` (whole-word prefix, case-insensitive, Unicode boundary) handles **head-position** inflection: "Geheimnis" → "Geheimnisses", "Geheimnis-Link". But German closed compounds put the term in the **tail/interior**: "Verschlüsselungsgeheimnis", "Linkgeheimnis" — `word_prefix` *falsely flags* those, a lint false-positive on legitimate content (the trust-killer).
- `substring` matches tail compounds but over-matches ("ageheimnis"). Neither default is safe blind.

**The discriminating fact is checkable, not guessable: do real de/de_AT `good` examples place the sense term in tail/interior compound position?** Before pinning the default, grep the actual examples (`en-translation-docs/glossary.md`; the `de.md` Geheimnis/Nachricht cases SPEC-cross-property §3 cites). If tail compounds occur → `substring` with a length-floor or a per-sense override; if not → `word_prefix`. A per-sense override field is deferrable (SPEC §8) only if the default fits the observed data.

This needs your sign-off because it pins a semantics the SPEC left open.

### Gap B — does step 5 (attach retros) land in P1-3 or split to P1-4?

Emit needs step 5 for `declined_index` and for retro-folded rule metadata to appear in the resolved JSON. Options:

- **Fold into P1-3** (recommended): emit is incomplete without it; `declined_index` shipping empty would be a silent gap. Adds ~1 module.
- **Split to P1-4**: P1-3 emits with `declined_index: []` and a logged TODO. Smaller PR, but the inversion would consume incomplete resolved JSON.

---

## 3. Fixtures + tests

**Finding (stale resume cmd):** HANDOFF §Resume says `python tests/inheritance/run.py` — that path does not exist. Only `tests/schema/run.py` exists; `tests/fixtures/de_AT/*.json` are forbidden-token fixtures for the Phase 0 `bin/lint-register` shim, not resolver inheritance fixtures. P1-3 needs its own.

Proposed layout, mirroring `tests/schema/`:

```
tests/resolver/
  run.py                         # harness, same style as tests/schema/run.py
  fixtures/
    de-de_AT/                    # minimal de → de_AT → base chain
      base.yaml
      locales/de/{rules,register,glossary}.yaml
      locales/de_AT/{rules,register,glossary}.yaml
      retrospectives/2026-04-12-de_at-formality.md   # one applied, one declined
      expected/de_AT.resolved.json                   # golden, key-stable
      expected/de_AT.for-translators.md              # golden, header SHA stubbed
```

Test cases: (1) emit JSON matches golden byte-for-byte; (2) emit MD matches golden modulo the `@<sha>` token; (3) lint passes on clean fixture; (4) lint fails with correct structured error on a seeded forbidden-token + a `good` example missing its sense target; (5) declined retro appears in `declined_index`.

**Note on `bad` examples:** the sense schema models only `target`/`rule_ref`/`rationale` — there is no "forbidden alternative" field. So a `bad` example carries no machine-checkable negative target; lint cannot assert it demonstrates the *wrong* form. `bad` examples are therefore not content-linted in P1-3 (they remain human-readable documentation, and any forbidden token they contain is caught by the independent forbidden-token pass). Adding a per-sense negative-target field is a SPEC §8 "extend when touched" change, deferred.

**Hash-stability for the MD header (SPEC §2.4):** the `@<sha>` is the *source* commit (the rules repo SHA), injected via `--source-commit` arg (default: `git rev-parse HEAD` of the rules repo, or `UNPINNED` when not a git tree). Golden compares with that token masked.

---

## 4. Resolved-JSON shape (emit_json target, from SPEC §2.3 lines 137–148)

```
_meta:   { source_commit, schema_version, generated_at }
register:{ form, pronoun, forbidden_tokens, rule_ref }
glossary:{ <term>: { <sense>: { target, rule_ref, examples: [...] } } }
rules:   [ { id, severity, text, rule_ref } ... ]    # MUST / MUST NOT only
context: [ ... ]                                      # non-binding
rationale_index: { rule_id: [doc_paths] }
declined_index:  [ ... ]                              # ← needs Gap B
anti_patterns_ref: [ ... ]
```

`generated_at` is the one non-deterministic field → must be excluded from the §2.4 file-hash check, or the hash check compares everything *except* `_meta.generated_at`. Flag: the SPEC says the MD file is hash-checked; confirm the JSON is too, and if so, which fields are masked.

---

## 5. Build order (when approved)

1. `emit_json.py` against a hand-written golden — forces the resolved shape to be concrete first.
2. `lint.py` — depends only on merged tree + register, not on emit.
3. Step 5 retros (if Gap B = fold-in) — feeds `declined_index` into emit.
4. `emit_markdown.py` — last; it is a projection of the resolved JSON.
5. Wire `--lint` / `--emit` into `resolve.py main()`; `tests/resolver/run.py`.

Each step is independently testable. No production YAML content is created — fixtures only — so this stays inside the "spine, not content" boundary the project has held to.

---

## 6. Open questions for sign-off

1. **Gap A**: accept reusing `forbiddenToken.context` semantics for example/target match — and the match mode (`word_prefix` vs `substring`) decided by grepping real de/de_AT examples for tail-position compounds first?
2. **Gap B**: fold step 5 into P1-3, or split to P1-4?
3. **§4 hash scope**: is `.resolved/<locale>.json` hash-checked like the MD, and which `_meta` fields are masked?
