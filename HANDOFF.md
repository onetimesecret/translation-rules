# Handoff — P1-3 Resolver Lint + Dual Emit (DONE, uncommitted)

## Context
- **Repo/branch:** `translation-rules` @ `phase-1/p3-1`
- **Working dir:** `/Users/d/Projects/dev/onetimesecret/translation-rules`
- **Task:** Implement SPEC §2.3 steps 5–7 (attach retros, lint, dual emit md/JSON) on top of P1-2.

## What we did
Implemented P1-3. Plan was `P1-3-PLAN.md`; three sign-off questions resolved by a grounding workflow + advisor (2026-05-29):
- **Gap A (match mode) → `word_prefix`.** Empirical: all German `good` examples place sense terms in head position (Geheimnis→Geheimnisses), zero tail/interior compounds → `word_prefix` never false-positives. Per-sense override deferred (SPEC §8).
- **Gap B → fold retros into P1-3** (not split). P1-2 already loaded retros; only the fold was missing.
- **Q3 → JSON is NOT content-hash-checked** like the MD. App-repo CI checks `_meta.source_commit == submodule SHA` only (SPEC §2.4). `generated_at` injectable for deterministic goldens.

**Architecture decision (advisor steer):** assemble ONE in-memory model (`resolver/model.py`) from merge + register + glossary + retro-fold; emit_json / emit_markdown / lint are pure projections. Per-locale filtering on `declined_index` AND retro-fold AND retro ref-checking.

**Two deliberate SPEC §2.3 deviations (noted in-code):**
1. Glossary shape: SPEC draws `glossary.<term>.<sense>.examples`, but examples are TERM-level in the schema with no sense linkage and bad/borderline carry wrong forms. Shipped: `<term>: {en, senses:{<sense>:{target,rule_ref}}, examples:[{...,senses:[matched]}]}`.
2. Advisory rules (SHOULD/SHOULD_NOT/MAY) → `context` as rendered strings; `rules` stays pure MUST/MUST_NOT (the anti-drift cue).

## Current state
- **Done, NOT committed** (working tree): the 5 new modules + `resolve.py` mods + `tests/resolver/`. 47 tests green (schema 34 · inheritance 9 · resolver 4).
- **Committed this session:** merge of `phase-1/p1-2-resolver` into `phase-1/p3-1` (clean, additive — brought resolver + `tests/inheritance/`). The prior HANDOFF's "stale" `tests/inheritance/run.py` was just unmerged; now present.
- **DECIDED (user, 2026-05-29):** keep the per-locale retro-ref-check edit + `--all`. **CI MUST run `resolve.py --all`** to keep retro-ref coverage global (memory: `p1-3-retro-refcheck-per-locale.md`).

## Next steps
1. **Commit the P1-3 implementation** (user gates this — not yet asked).
2. Open PR for `phase-1/p3-1`. P1-2 is NOT on main either — sequence the merges.
3. Then Phase 1.5 first act: the **guidance-source inversion** (docs `en/translations/` becomes resolver emit, not authority). Blocked on P1-3 emit, now unblocked.
4. No production locale YAML exists yet (spine, not content) — real `locales/de_AT/*.yaml` + retros are the first content migration.

## Key files
- `resolver/model.py` — assemble step (fold, per-locale, glossary shape). Start here.
- `resolver/lint.py` · `resolver/matching.py` (word_prefix) · `resolver/emit_json.py` · `resolver/emit_markdown.py`
- `resolver/resolve.py` — CLI (`--lint --emit=md,json --all --emit-dir --source-commit --generated-at`); retro-ref-scope edit ~line 407.
- `tests/resolver/run.py` + `fixtures/{de-de_AT, lint-violations, superseded-orphan, dangling-retro-ref}/`
- `SPEC.md` §2.3/§2.4 · `P1-3-PLAN.md` · memory dir.

## Resume commands
```bash
cd /Users/d/Projects/dev/onetimesecret/translation-rules
git status -s                                  # uncommitted P1-3 impl
RUN="uv run --with jsonschema --with referencing --with pyyaml python"
$RUN tests/schema/run.py && $RUN tests/inheritance/run.py && $RUN tests/resolver/run.py
# regenerate de_AT artifacts (pinned, reproducible):
F=tests/resolver/fixtures/de-de_AT
$RUN resolver/resolve.py de_AT --base-file $F/base.yaml --locales-dir $F/locales \
  --retrospectives-dir $F/retrospectives --project-root $F --index-path /tmp/i.json \
  --emit md,json --lint --emit-dir /tmp/out --source-commit TESTSHA0 \
  --generated-at 2026-05-29T00:00:00+00:00
```

## Caveats
- Goldens are self-generated → byte-for-byte test is a **regression** guard; correctness rests on the `declined`/`fold`/lint property assertions + inspection.
- `--all` treats every `locales/<dir>` as a target (incl. parent-only layers like `de`, which emit thin output). Fine; not a bug.
