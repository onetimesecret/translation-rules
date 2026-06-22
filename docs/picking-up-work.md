# Picking up work after a gap

A cold-start ritual for returning to this project (or any of its consumers)
after days or weeks away, without having to remember where you left off.

## Principle

**The repo is your memory.** You don't recall the next step — you *look it up*,
in four places, in order. Each place answers one question. Decisions live in
ADRs, intentions and dependencies live in issues, in-flight work lives in PRs,
and loose ends live in branches.

## The cold-start scan

Run top to bottom. The arc is **decided → in-flight → ready-to-start → cleanup.**

1. **What did I already decide?** — skim the ADR index
   (`docs/architecture/decision-records/`). Reloads the *why* so you don't
   relitigate or accidentally undo a settled call.
2. **What's almost done?** — open **PRs**. A nearly-mergeable PR is usually the
   real next step; finish in-flight work before starting anything new.
3. **What's unblocked?** — open **issues**, and find the *leaf*: the one whose
   linked dependencies are all closed. That's what you can actually start. Prefer
   the leaf that unblocks the most others.
4. **What's dangling?** — **branches** with no PR. Keep or kill, so the workspace
   doesn't accumulate ghosts.

## The habit that makes it work

The scan only works if a breadcrumb exists. Two cheap conventions:

- **Leave a breadcrumb when you stop.** Before ending a session, write the next
  step — *and its blocker* — as a comment on the workstream's tracking issue.
  "Future-you" reads it cold in 30 seconds.
- **One tracking (epic) issue + one label per workstream**, with children listed
  **in dependency order** and each child stating its dependencies ("Depends on
  #38"). Then the cold-start scan collapses to *opening one filtered list*.

## Live example: the i18n cross-repo workstream

- **Decisions:** `docs/architecture/decision-records/` — ADR-003 (single
  authority), ADR-004 (pin + automated bump), ADR-005 (no vendored output).
- **Label / filter:** `i18n-arch` (issues are also title-prefixed `[i18n-arch]`).
- **Tracking issue:** the `[i18n-arch] Epic` issue lists the open items in
  dependency order and is the one-click entry point for the scan above.
