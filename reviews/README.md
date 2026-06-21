# Reviews

Raw QA review prose, stored as-is in `reviews/<date>/`. Per `SPEC.md` §3 this
directory is the human-written input end of the feedback cycle — no schema,
no rewriting. The machine-readable companions are retrospectives; see
`retrospectives/README.md` for how findings become rule changes.

## Review vs retrospective

**Review** = raw observation. Prose, no schema, human/agent-authored, lives in
`reviews/<date>/`. Answers *"what did we see?"* Can be one locale or a 29-locale
roll-up — both are reviews. Ends in a findings manifest.

**Retrospective** = the decision a finding drives. Schema'd frontmatter,
lifecycle-tracked (`pending→applied`), lives in `retrospectives/`. Answers
*"what rule changes because of it, and is it done?"*

A cross-locale roll-up file is a second review document (observation), sitting
alongside the per-locale ones. Its job is to *name* the patterns that span
locales; each pattern then gets one retro that the relevant per-locale manifests
tag.

Rule of thumb: **many reviews can point at one retro; one retro can be cited by
many reviews.** Observation is many-to-one with decision. If you're recording
what you noticed → review. If you're committing to a rule/lint change and
tracking it to closure → retro.

## Grandfather clause

Documents that predate the findings-manifest gate are preserved byte-for-byte
(SPEC §3: "Existing `reviews/` directories remain as-is ... no backfill into
retrospective format"). The frozen inventory lives in
`resolver/review_manifest.py` (`GRANDFATHERED`); never add paths to it. The
freeze is by path, not by date: a document added later into an old dated
directory is still a new review and must carry a manifest.

`README.md` files — this one and per-directory indexes like
`2026-04-12/README.md` — are directory indexes, not review documents, and
are exempt.

## Findings manifest

Every new review document must end with a findings manifest: the last
`##`-level heading is exactly `## Findings manifest`, followed only by `- `
bullets (indented continuation lines and blank lines are fine — anything
else fails CI). Each bullet maps one finding to exactly one tracking tag:

- `retro: <id>` — the id of a retrospective in `retrospectives/`
  (including `_archive/`; superseded retros are still valid tags), or
- `wont_fix:` followed by non-empty reasoning for not acting.

A review with zero findings closes with the single literal bullet `- none`.

Worked example:

```markdown
## Findings manifest

- Sie-form flipped to du in checkout strings.
  retro: 2026-04-12-de_AT-register-flip
- Two screenshots show the old navigation. wont_fix: UI rewrite ships next
  quarter; retranslating against the dead layout is wasted effort.
```

Or, for a clean review:

```markdown
## Findings manifest

- none
```

## CI

`.github/workflows/schema-validation.yml` runs `resolver/review_manifest.py`
on every PR: a new review document missing its manifest, tagging an unknown
retro id, or leaving a finding untagged fails the build. This is what
prevents the "insights die in prose" failure (SPEC §3) that produced the
pre-2026 unactioned review backlog.
