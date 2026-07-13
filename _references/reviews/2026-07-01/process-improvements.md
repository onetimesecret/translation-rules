# Cutting Wasted Work in the Next Locale-Update Review Wave

Two classes of noise dominated the last wave's review effort. Both are mechanical and preventable; neither reflects a bot accuracy problem. Roughly 40 agent-invocations went to proving negatives that were already true.

## The two noise classes

**1. Stale review base (the `%{date}` false-positive).** The reviewer diffed each PR against a base snapshot predating commit `5049cd5a1` (Wed Jul 1 17:55, "Remove orphaned `email.email_changed.body` locale key"), which deleted the dead `email.email_changed.body` key from all 30 locale `email.json` files. In 11 of those locales the dead key's body had drifted to carry an extra `%{date}` not present in the EN source — a *real* extra-variable mismatch, but in a *dead* key already removed at source. Because the reviewer's base predated the removal, the same "CRITICAL blocker" fired on all 11 open PRs, and each was litigated independently:

- de/#3579, eo/#3582, es/#3583, fr_CA/#3584, fr_FR/#3585, ja/#3589, ko/#3590, nl/#3592, pt_BR/#3594, ru/#3596, zh/#3602.
- 9 of 11 tracked down commit `5049cd5a1` by hash to dismiss it; ja re-ran `git merge-base --is-ancestor`; fr_FR and eo re-ran `i18n validate variables`. de/#3579 never located the removal commit and left the flag unresolved with a "looks stale" note — burning effort *and* failing to explain the discrepancy. The 19 non-drifted locales were never flagged, confirming the flag mapped 1:1 to the drift, not to review coverage. **11 PR passes re-deriving one already-merged negative.**

**2. Expected pipeline state flagged as a defect (missing `source_hash`).** The tail `content hashes --apply` run added 437–597 missing `source_hash` values *per locale* — normal pipeline catch-up that runs *after* PRs merge. The reviewer flagged "new keys missing `source_hash`" as a finding on ~all 29 PRs. This is expected steady-state, not drift. **~29 PR passes on a known non-defect.**

## Fixes for the next wave

1. **Diff against current `origin` HEAD, not a cached snapshot.** Rebase/refresh each branch (or point the reviewer at the PR's live merge-base) before automated review. A fix that lands mid-batch must invalidate the flag for every sibling PR automatically — not be re-discovered per-locale.
2. **Triage shared-base fixes once, centrally.** Dead-key removals and source-drift fixes affecting a fan-out should be resolved one time and the finding suppressed across all siblings, not re-opened in each locale PR.
3. **Teach the review prompt to suppress known-pipeline states.** Add `source_hash`-absent to an allowlist of expected post-merge pipeline conditions. `source_hash` reconciliation is the pipeline's job and runs after merge; it is never a locale-PR defect.
4. **Add cheap integrity gates so these never re-enter as real findings later:** reject non-sha256 placeholder hashes at PR time (the `a1b2c3d4`/`e5f6a7b8`/`d8e9f0a1` branding seeds), and add a CI check that `content_hash == sha256(text)` so hash lag (the Delano→Support Team window) can't masquerade as source drift.

## What genuinely needed human/agent judgment

Not all of the wave was noise. These required real decisions and should be the *focus* of reviewer attention next time:

- **Base-rule gap:** `rule.meta-keys-untranslated` (base.yaml:32–35) enumerates only three top-level `_`-prefixed keys, so flattened `web.auth.…_guidance.context` metadata leaked as translatable `{text:…}` units (28 of 29 locales; some, e.g. ru/de/ja/ko, even *translated* the pipeline note). Broadening the rule to any `_`-prefixed *segment* is a genuine rule change, plus a source-tool fix so nested metadata never flattens into translatable units.
- **Terminology decisions:** de_AT's "Bereich" (72×) vs de's "Domain" for the custom-domains feature is a glossary call, not a lint — and PR #3580 pushed it the wrong way. pt_PT email register (informal "tu/teu/tua") is unenforced and needs a per-locale forbidden-token gate plus a reconciliation decision.
- **Real source defects to fix upstream, not in locale PRs:** the `region domain` jargon (plus its tree-wide `source_hash` desync, `68ec20f8` vs phantom `b588f5b2`), the `%{status}` raw-English-enum leak (an app-layer defect — locales cannot fix it), and the EN `homepage`/`Homepage` casing split. Flagging these against locale PRs wastes effort; route them to source issues.