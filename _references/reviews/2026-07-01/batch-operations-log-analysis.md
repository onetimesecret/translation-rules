# _references/reviews/2026-07-01/batch-operations-log-analysis.md

Read the full log plus this repo's rule/retro mechanism. Here's the value, and it's real.

What the log actually is

29 Sonnet agents, each independently re-deriving the same ~6 cross-locale facts from scratch because none of those facts lived in this rules authority. That re-derivation is exactly the cost the resolver exists to eliminate. Most "left as-is, with reasoning" notes are an agent rediscovering something that should already be a rule, a glossary term, or a known-source-defect record. Mine it and you convert ~40 wasted agent-invocations into a handful of durable artifacts.

Three buckets:

A. Source-side (English) defects — fix once in en/, all 29 locales benefit

Every locale faithfully mirrored a broken source. These recur on every future wave until fixed upstream:

1. en/admin-colonel.json:7 — raw JS ternary/template-literal shipped as literal translatable text. Independently confirmed pre-existing by eo, da_DK, hu, uk, vi. Not a translation bug.
2. SSO terminology in en/workspace-billing.json — features.manage_sso="SSO", features.sso/entitlements.manage_sso="Single Sign-On (SSO)", entitlements.sso="Single Sign-On". Five agents (es, fr_CA, pl, pt_BR, vi) correctly refused to fix per-locale because it'd desync from source and get overwritten on next hash sync. Normalize the source.
3. _guidance.context dotted flat-keys leaking as translatable strings (export-tool artifact). Handled inconsistently — deleted in it_IT/ko/sv_SE/mi_NZ, left as pre-existing in uk/vi. That inconsistency is itself the tell: no rule says whether nested _guidance.* keys are meta-keys. base.yaml's rule.meta-keys-untranslated only covers top-level _-prefixed. Gap.

B. Review-process noise — the bot billed you for false positives

4. Stale %{date} "CRITICAL blocker" flagged across ~11 locales (de, eo, es, fr_CA, fr_FR, ja, ko, nl, pt_BR, ru, zh) — but commit 5049cd5a1 had already removed the key before review ran. The reviewer's base was stale; 11 agents each independently proved the same negative.
5. Missing source_hash on new keys flagged on nearly every locale — expected pipeline behavior (the closing content hashes --apply added 437–597 per locale). Pure noise on 29 PRs.

Process fix, not a rule: the review bot must diff against current HEAD (or branches rebase before review), and suppress the source_hash-absent class. That's the single biggest cost reduction for the next 25-language wave.

C. Genuine convention decisions the agents coin-flipped

These are the ones that belong in this repo:

6. email.feedback_email.signature = "Secret Support" — the clearest finding. Directly contradictory handling: translated in he, sl_SI, sv_SE, tr, mi_NZ; left English in ar, da_DK, es, pt_PT. Is "Secret Support" a brand name (untranslated) or a support-team label (translated)? rule.brand-names-untranslated doesn't list it, so translating is defensible — but half didn't. One glossary term ends the coin-flip.
7. "Workspace" — nl translated (Werkruimte), ptd term. Same class as #6.
8. Parenthetical X(s) vs pipe-plural — pt_PT coarenthetical because the source uses it. Note:
base.yaml rule.pluralization-syntax mandates piolates your own rule (session(s)). Source fix + a rule clause on what to do when source is parenthetical.
9. French NBSP before ?!:; — fr_CA flagged, dec Candidate for an explicit fr* locale rule or adeclined guardrail retro.

My recommendation

Don't file 10 things. Highest leverage, in order:

1. One upstream issue in onetimesecret bundling the three source defects (A1–A3). Verify they still exist in en/ first — the
log is secondhand evidence.
2. One pending retrospective here capturing the meta-lesson (29 agents re-derived ~6 shared facts) and locking the two clean glossary decisions (#6 "Secret Support", #7 "Workspace") — that's the durable payload this repo is built for.
3. One process note on the stale-base + source_s review harness diffs against HEAD.

Want me to (a) verify A1–A3 against the live en worktree, (b) draft the retrospective for #6/#7, or both? I'd do both — (a) first so the  retro cites confirmed facts.

## Findings manifest

- Lock the two clean glossary decisions (#6 "Secret Support", #7 "Workspace").
  retro: 2026-07-02-signature-brand-vs-translatable
- Meta-lesson (29 agents re-derived shared facts) + stale-base review harness.
  wont_fix: reviewer-workflow guidance captured in process-improvements.md;
  no rule or retro change.
