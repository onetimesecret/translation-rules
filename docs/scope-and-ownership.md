# Scope and ownership

The working stance behind how this project treats inherited defects and change
size. Recorded because it governs triage decisions that would otherwise be
re-litigated per contributor.

## No "pre-existing" issues

This project does not recognize a "pre-existing issue" as grounds to leave a
defect in place. A problem that predates your branch, that another author
introduced, or that a prior wave missed, is not someone else's problem — it is
an issue **we are responsible to resolve**. The only distinction that matters
is whether we have *found* it yet.

The translation tree is inherited work: 29 locales, much of it machine- or
agent-authored, reconciled across many waves. Treating any of it as untouchable
"legacy" is how drift compounds. When a review surfaces a partial translation, a
register slip, a collapsed sense, or a stale hash — inside or outside the diff
that surfaced it — it is in scope to fix.

## Correctness over convenience

We optimize for the **long-term value of the codebase**, not the size of the
current change:

- Take **as much time, and as many revisions or stacked PRs, as it takes** to
  get a change right. A large correct change delivered as a reviewed stack beats
  a small convenient one that leaves the tree inconsistent.
- Fix the **class, not just the instance.** When one locale's rendering is
  wrong, check the sibling locales for the same failure and encode the decision
  (glossary term, rule, retrospective) so the next wave inherits the fix, not
  the bug.
- Prefer fixing at the **source or the authority** (English source, glossary,
  base rule) over patching each locale, so one correct change propagates.

This is why findings become retrospectives and rules here rather than one-off
edits: the durable artifact is what stops the issue from recurring. See
[terminology.md](terminology.md) for the terminology-specific application of
this stance (the brand-vs-translatable anchor test).
