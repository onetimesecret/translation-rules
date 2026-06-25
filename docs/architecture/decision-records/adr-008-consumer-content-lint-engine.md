---
id: 008
status: accepted
title: ADR-008: Consumer content is linted by the resolver engine, across every governed locale
---

## Status
Accepted

## Date
2026-06-25

## Context
The project exists to prevent the register-flip class **across locales**
(translation-rules#2). Yet the only gate that scanned **shipped app content**
for forbidden register tokens — onetimesecret `validate-register.yml` →
`bin/lint-register` — ran for **de_AT only**. The other ~28 governed locales
shipped unchecked.

`bin/lint-register` cannot simply be pointed at them: it is a Phase-0
`LC_ALL=C` byte-grep built for German/ASCII-ish word boundaries. Measured
against live app content it **hard-errors** on the CJK `substring` rules
(ja/ko/zh: `error: unknown context 'substring'`) and **floods false positives**
elsewhere — 291 on Vietnamese (`bà` inside `bài`), 59/57 on French (`te` inside
`Hôte`) — while simultaneously *mis*-counting the locales it can read (cs 15≠13,
nl 26≠34) because byte `\b` drifts under UTF-8. It is the wrong tool for 30
scripts.

The resolver already owns the right matcher. `resolver.matching.find_spans` is
Unicode-correct, casefolded over NFC, `substring`-capable, and the lint layer's
`_exception_spans`/`_hit_allowed` honour the register `exceptions` allowlist by
span containment (`du` inside `Duden` is spared; a standalone `du` beside it is
not). But `resolver.lint.lint_model` points that engine at the **authority's**
resolved model (good examples + embedded docs) — not at consumer content.

## Decision
Lint consumer content with the **same engine**, never a second matcher.
`lib/resolver/lint_content.py` reuses `find_spans` + `_exception_spans` +
`_hit_allowed` and:

1. takes each locale's **resolved** register (post-inheritance) from the derived
   `.resolved/<locale>.json` — the shared derive action's output (ADR-006) — so
   the gate enforces exactly what the authority resolved, not a re-parse of raw
   YAML;
2. walks **rendered** content strings, reporting `{file, key, token, context,
   snippet}` with a clear pass/fail exit (SPEC §6.2), mirroring `bin/lint-register`'s
   exit codes (0 clean · 1 hit · 2 config · 3 empty-glob) for drop-in CI use;
3. is wired into the app's content gate for **every** governed locale via the
   derive action, replacing the de_AT-only byte-grep path.

**Scan surface (`SKIP_KEYS`).** The register governs rendered, end-user-facing
copy, so only those string values are scanned. The content schema's
non-rendered keys are skipped — `source_hash` (a hash), `renderer` (a mode tag),
`skip` (a flag), `context`/`note` (translator guidance, never shown), and any
`_`-prefixed metadata block. This avoids false positives on English translator
notes and is a named module constant, not a buried heuristic, so the surface
stays reviewable.

This is deliberately the engine the authority-model lint already trusts: one
matcher, two callers (authority model + consumer content), so the gate can never
disagree with the rules it derives from.

## Measured exposure (evidence)
Scanning every `onetimesecret/locales/content/<locale>/*.json` against the
resolved register with this engine: **49 genuine violations, zero false
positives**, all in three locales — the rest of the ~28 are clean, *including*
every locale the byte-grep flagged.

| locale | hits | tokens | nature |
|---|---|---|---|
| **cs** | 13 | `vámi, vaši, vašem, vašimi` | formal `váš`-family in informal-locked Czech — the exact formal-in-informal flip translation-rules#2 exists to catch |
| **ja** | 2 | `してくれ, ぜ` | informal/rough forms in keigo-locked Japanese — `substring`-only; **no grep gate could ever see these** |
| **nl** | 34 | `u, uw` | formal V-forms in informal-locked Dutch — overlaps the register's noted B2B/marketing carve-out; **needs a maintainer policy call** |

Full per-hit remediation list: onetimesecret#3530 (native-speaker review;
cs/ja are clear regressions, nl needs the carve-out decision first). Reproduce
with the derive action (or `resolve.py --all --emit=json`) then
`lint_content.py --resolved .derived/.resolved/<locale>.json <content-glob>`.

## Consequences
- The gate now **blocks** a forbidden register token entering *any* governed
  locale's content, not just de_AT — closing the cross-locale gap that left the
  founding bug-class invisible.
- Flipping to blocking surfaces the existing 49 as failures rather than burying
  them. cs/ja must be fixed to their locked register; **nl's B2B-formal
  carve-out must be encoded as register `exceptions` (or a `register_spec`)**
  before its 34 stop blocking — recording the policy where the engine reads it,
  which is the point. Remediation is tracked in onetimesecret#3530.
- `bin/lint-register` is not deleted: it remains the dependency-free Phase-0
  smoke check (its `lint-register.yml` `--dry-run` self-test still proves every
  register parses). The engine-based gate is the load-bearing one for content.
