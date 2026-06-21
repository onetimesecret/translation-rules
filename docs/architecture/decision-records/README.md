## Architecture Decision Records (ADRs)

Documents that capture important architectural decisions in the
translation-rules authority — the schema contract, the resolver, the quality
gates, and the artifacts consumed by the app repo — along with their context
and consequences. They are a best practice for technical documentation in
open-source projects.

**Lifecycle:**
- Proposed: Under discussion
- Accepted: Decision approved and implemented
- Deprecated: No longer relevant but kept for history
- Superseded: Replaced by a newer ADR (reference the new one)

### Keys to Success

- **Be courteous**: ADRs should be readable in 2-3 minutes, so focus on why. The decision itself is less important than the reasoning.
- **Avoid formulaic sections**: Don't force content into rigid templates. If your core argument is complete in Context and Decision, stop there. Skip sections that merely reorganize the same points.
- **Combine related content**: Merge rationale directly into the Decision section. Trade-offs are optional—only include them when they add genuine insight.
- **Immutable**: Once accepted, don't edit the decision; that's like re-writing history. Use Implementation Notes or create another ADR to supersede.
- **Numbered sequentially**: Makes referencing easy (`ADR-001`, `ADR-002`, etc.)
- **One decision per ADR**: Don't bundle multiple choices together

### Implementation Notes Section

Optional addenda for clarifications and execution details. Use it for:

- **Clarifications**: Technical details or edge cases discovered during implementation
- **Rollout timelines**: When the decision will be implemented relative to when it was accepted
- **Migration notes**: How to transition from the old state to the new one

This section is mutable. Each note should be dated and titled.

### When to Write ADRs

Write ADRs for decisions that:
- Are expensive to reverse or constrain future options
- Affect both this repo and the consuming app repo (e.g. the resolved-artifact contract, the cross-repo gate mechanism)
- Establish patterns for others (schema shape, resolver pipeline semantics, retrospective lifecycle)
- Resolve technical debates

Don't write ADRs for:
- Trivial or easily reversible
- Implementation details within a single module
- Non-contentious or standard practice decisions

This repo already records several such decisions inline (e.g. SPEC.md §2.4
"read-only pinned checkout, not a submodule"; §2.3 "artifacts committed to the
app repo, not CI-generated-only"). New cross-cutting decisions belong here as
numbered records; existing inline ones can be promoted to ADRs when next
revisited.

### Filename & Numbering

`adr-NNN-kebab-slug.md`, numbered sequentially, slug derived from the title.
`adr-000.md` is the template — copy it to start a new record.
