# Handoff — Cross-Property Translation Workflow Design

## Context
- **Repo/branch:** `translation-rules` @ `phase-1/p1-2-resolver`
- **Working dir:** `/Users/d/Projects/dev/onetimesecret/translation-rules`
- **Task:** Design a next-gen translation process spanning all three OTS properties (app, docs, website). Diagnose → design only; no production code written this session.

## What we're doing
Extend the app-only `SPEC.md` (rule-system that prevents the 2026-04-12 de_AT formality regression) to cover the two supporting sites. Deliverable is **`SPEC-cross-property.md`** — a companion design doc, not a rewrite of SPEC.

**Core thesis (committed to):** `translation-rules` is the property-*agnostic* authority. Register/glossary/rules describe the *language*, not a file format. Each property keeps its own plumbing; all three consume the same `.resolved/<locale>.json` via the same `saas-translator` skill (reading resolved JSON, not hardcoded conventions).

**Three findings that shaped the design:**
1. **Inverted source-of-truth (the real drift engine).** OTS guidance source physically lives in the *docs repo* (`docs.onetimesecret.com/src/content/docs/en/translations/`); `translation-rules/en-translation-docs/` is a copy; a 3rd glossary sits at docs `docs/localization/glossary/core-terms.json`. Migration must invert this: authority = source, docs `en/translations/` = resolver emit. Made the first act of Phase 1.5.
2. **"harmonize = keys only" is concrete** = website's `.github/workflows/harmonize-locales.yml` (jq key-sync, preserves text). Safe; leave running. Incident was a *manual* harmonize that rewrote text.
3. **Website is mixed-surface** (`ui` in `src/i18n/ui` + marketing `prose`). Surface cut (`ui`/`prose`) runs *through* one property. Marketing-vs-docs register = possible 3rd surface, deferred.

**Terminology:** `surface` = `ui` | `prose` (the one new schema facet proposed: `surfaces:` on glossary terms + `resolve.py --surface`). Formality is surface-neutral, stays in `register.yaml`.

## Current state
- **Done (committed):** P1-1 (6 JSON schemas), P1-2 (resolver: load/validate/inheritance/merge/ids — tested). No production YAML content yet by design.
  - `SPEC-cross-property.md` (the deliverable), `HANDOFF.md`. `en-translation-docs/` also shows untracked.
- **Two decisions (DECIDED 2026-05-29):** (1) source inversion runs as the **first act of Phase 1.5** (after P1-3 emit), short docs-guidance freeze during cutover; (2) `surface` facet lands **at first prose migration** (first docs locale, Phase 1.5) per SPEC §8 — not now. Both per the doc's recommendations.
- **Not started:** P1-3 (resolver lint + dual emit md/JSON) — blocks everything downstream including the inversion.

## Key files
- `SPEC.md` — app-scoped authority design (the spine; don't rewrite)
- `SPEC-cross-property.md` — this session's deliverable
- `P1-3-PLAN.md`
- `.github/ISSUE_DRAFTS/00-clearinghouse.md` — phased rollout
- `resolver/{resolve,merge,inheritance,loader,ids,validate}.py` — P1-2, done
- `schema/*.schema.json` — P1-1, done
- Memory: `~/.claude/projects/-Users-d-Projects-dev-onetimesecret-translation-rules/memory/translation-rules-architecture.md`

## Cloned this session (siblings, shallow, not in this repo)
- `../docs.onetimesecret.com/` — Astro Starlight docs. Translation: `bin/translation-pluribus-util`, `bin/generate-for-translators`, guidance at `src/content/docs/en/translations/`.
- `../onetimesecret.com/` — Astro+vue-i18n website. `src/i18n/ui/<locale>.json`, `harmonize-locales.yml`, `generate-markdown-content.mjs`.
- App pipeline: `../onetimesecret/locales/scripts/` (SQLite tasks, hash staleness).

## Resume commands
```bash
cd /Users/d/Projects/dev/onetimesecret/translation-rules
git status -s                          # see uncommitted deliverable
git --no-pager log --oneline -5
# resolver tests:
python tests/schema/run.py && python tests/inheritance/run.py
```

## Next steps
1. Proceed with P1-3 (lint + emit) — prerequisite for the inversion and all property consumption.
