# Retrospectives

Structured records of translation incidents and the rule changes they motivate.
Raw QA reviews live in `reviews/<date>/` and are preserved as-is — see `SPEC.md`
§3. Retrospectives are the machine-readable companions: each carries YAML
frontmatter that the resolver and CI can act on.

## Lifecycle

```
pending ──► applied ──► superseded
   │
   └──► declined  (still active as a guardrail)
```

- **pending** — filed, awaiting rule change. CI blocks the next main PR if a
  retrospective stays `pending` more than 7 days without transition.
- **applied** — the PR that flips status to `applied` must also touch every id
  in `affected_rules` and populate `resolved_in_commit`. CI-enforced.
- **declined** — requires `declined_reason` and `would_change_decision_if`.
  Human-gated. Declined retros stay as **active guardrails** (not archived) —
  the resolver emits per-locale decline summaries so agents see them.
- **superseded** — only via a newer retro whose `supersedes:` list contains
  this id. Superseded files move to `_archive/`.

Schema enforcement of frontmatter lands in P1-1; for now the format is a
shared convention.

## Frontmatter template

Copy this into a new `<date>-<slug>.md` file and fill in.

```yaml
---
id: YYYY-MM-DD-<slug>            # matches the filename, no .md
date: YYYY-MM-DD
status: pending                  # pending | applied | declined | superseded
triggered_by:
  commits: []                    # SHAs that introduced or surfaced the issue
  incident: ""                   # one-line description
affected_locales: []
affected_rules: []               # dotted IDs, e.g. register.de_AT.formality
examples_added: []               # ex.<key>#<8char> — populated as glossary grows
baseline_pins: []                # baselines.<locale> — forward-ref ok in Phase 0
resolved_in_commit: null         # PR merge SHA, populated when status: applied
supersedes: []                   # retro ids this one replaces
declined_reason: null            # required iff status: declined
would_change_decision_if: null   # required iff status: declined
---

<prose body — what happened, root cause, the rule change. Link to the raw
review under `reviews/<date>/` rather than duplicating its content.>
```

## Filing a new retrospective

1. Pick a slug. Filename: `YYYY-MM-DD-<slug>.md`. The `id` matches.
2. Fill the frontmatter. `status: pending` is the entry point.
3. Body should link the corresponding `reviews/<date>/` directory, summarize
   the failure mode in three to ten sentences, and name the rule change
   required to close it.
4. Open a PR. The PR that transitions `pending → applied` must include the
   YAML edits to every id in `affected_rules`.

## Existing reviews stay as-is

Per `SPEC.md` §3, historical `reviews/` directories are not back-filled into
this format. Only new incidents file retrospectives here. Unactioned findings
in old reviews get triaged opportunistically into new retrospectives when the
underlying issue resurfaces.
