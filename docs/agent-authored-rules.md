# Agent-Authored Rules

*A model for letting agents author translation rules that bind the task pipeline and cannot be violated — the merged conclusion of two parallel agent design notes.*

> **Status — non-binding. Combined AI-agent analysis, not human input.**
> This note was produced by merging the design write-ups of two parallel Claude Code
> agent sessions (`agent-authored-rules.md` and `enforcement-model.md`). It is
> descriptive: it argues for a direction. It is **not** direct human input, and it
> binds nothing — no translation, no rule, no task. Per this repository's own firewall
> (`SPEC.md` §2.1), only schema-validated YAML under `locales/` binds; prose like this
> never does, regardless of who or what wrote it.

## Thesis

The system that exists today requires a human to hand-author every word-level decision
— register, terminology, forbidden words — as YAML. That is unusable in practice: the
people who own the product cannot sit and adjudicate word choices per locale.

The system that is needed inverts the authorship. **Agents author the rules as a
byproduct of doing the translation work**; the rules are structured and
schema-validated; and they are pinned into each translation task and enforced so they
cannot be violated. The boundary that prevents the original failure is not *human vs.
agent* — it is *structured channel vs. loose prose*.

## 1. The axis that matters

```
                  UNSTRUCTURED prose            STRUCTURED + schema-enforced
                  (changelog · retro · chat)    (validated YAML → resolved ruleset)
                ┌────────────────────────────┬────────────────────────────────────┐
  HUMAN author  │ drifts whenever the prose  │ the intended state today            │
                │ is cited as guidance       │ → binds safely                      │
                ├────────────────────────────┼────────────────────────────────────┤
  AGENT author  │ the 2026-04 de_AT flip:    │ the TARGET state:                   │
                │ prose read as a rule       │ agent writes a gated rule           │
                │ → silent register flip     │ → cannot be violated                │
                └────────────────────────────┴────────────────────────────────────┘
```

The 2026-04 de_AT incident — formal `Sie` silently flipped to informal `du` across UI
and email — is usually attributed to "an agent wrote the rule." That is the wrong axis.
The failure lived in a single cell: **agent author + unstructured prose** (a
conversational changelog read as prescriptive guidance). The columns are what matter,
not the rows.

The current design reacts by banning the entire agent row ("only human-authored YAML
may bind"). That discards the one cell the product actually needs — **agent author +
structured, enforced rule** — and puts a human back in front of every word. Agent
authorship was never the danger; unstructured authorship was.

## 2. The binding model

A rule earns the word "rule" by being **pinned into the task** and enforced at two
points — not by being a detached lint that runs afterward.

```
        agent codifies a finding
        as a STRUCTURED RULE
                  │
                  ▼
   ╔═══════════════════════════════════════════════════════╗
   ║                   RULES AUTHORITY                       ║
   ║   locales/de_AT/*.yaml           (schema-validated)     ║
   ║          │  resolve                                     ║
   ║          ▼                                              ║
   ║   .resolved/de_AT.json     →   pinned as ruleset@<hash> ║
   ╚════════════╤══════════════════════════════╤════════════╝
                │ (A) binds the INPUT           │ (C) binds the OUTPUT
                ▼                               ▼
 ┌────────┐  ┌──────────────────────┐   ┌────────────────────┐
 │TASK DB │─▶│   TRANSLATOR AGENT    │─▶ │ DETERMINISTIC GATE │─▶ task closes ✓
 │de_AT #n│  │ (B) rules in-context: │   │ tokens · glossary  │
 └────────┘  │  Sie · no du/dein ·   │   └─────────┬──────────┘
      ▲       │  secret = Geheimnis  │             │ violation
      │       └──────────────────────┘             ▼
      └───────────────  task cannot close  ◀─────── ✗
```

- **(A/B) Input binding — prevention.** The translator agent receives the locale's
  resolved ruleset *as constraints in its context* before it produces a single string.
  Register, forbidden tokens, and glossary senses are present at generation time.
- **(C) Output binding — guarantee.** A deterministic gate is the task's *definition of
  done*. A task cannot close while its output violates the ruleset pinned to it
  (`ruleset@hash`).

Enforcement's home is the task itself — this is the `SPEC.md` §5–§6 pipeline
(`saas-translator`, `start-translation-session`, `work-tasks-db`) consuming
`.resolved/<locale>.json`. App-repo PR CI (the forbidden-token lint) is a **backstop**,
not the primary gate.

## 3. Why two points and not one

```
   RULES IN PROMPT ONLY        GATE ONLY                 BOTH  (this model)
   ────────────────────        ─────────────────         ──────────────────────
   agent usually complies      agent may emit du         agent rarely emits du,
   but CAN still slip          gate blocks it, but       AND the gate blocks any
   → a violation can ship      only after wasted work    slip → cannot ship
        probabilistic              deterministic              prevention + guarantee
```

In-context rules make the agent *usually* comply — prompt adherence is probabilistic,
so a violation can still ship. A gate alone catches violations, but only after wasted
work. Both together turn "usually fine" into a guarantee: the rule is present before the
word is written, and any slip is rejected at task close.

## 4. The firewall, restated

The original firewall conflated two separable ideas. Only one is load-bearing.

```
   WHO may author a rule?   a human OR an agent      — not the dividing line
   WHAT may bind a task?    only the structured      — THIS is the dividing line
                            channel

   ┌─ BINDS ───────────────────────┐   ┌─ NEVER BINDS (explanatory only) ──────────┐
   │ locales/**/*.yaml             │   │ retrospectives/**   _archive/**           │
   │   → resolve → ruleset@hash    │   │ chat · changelog · PR descriptions        │
   │                               │   │ THIS document                             │
   └───────────────────────────────┘   └───────────────────────────────────────────┘
              ▲                                       │
   the 2026-04 flip is impossible                     └─ 2026-04-12: a changelog
   on this side — prose cannot cross                      crossed the line → flip
```

- **Keep:** *prose never binds.* Retrospectives, archives, changelogs, chat, PR
  descriptions — and this document — are explanatory. They never compile into a ruleset.
  This is the structured-vs-prose line, and it is exactly what the `_archive/` firewall
  (`SPEC.md` §2.1) enforces.
- **Delete:** *human-authored-only.* Authorship is not the boundary. An agent may author
  a binding rule, provided it enters through the structured channel (schema-valid YAML →
  resolved ruleset).

The 2026-04 flip was not "an agent authored a rule." It was **prose crossing into the
binding set**. The fix is to make that crossing impossible, not to ban agents from
authoring.

## 5. The hard problem: self-legalization

If an agent both authors the rules and is bound by them with zero friction, it can
author a rule that blesses its own error — quietly legalizing the very mistake the
system exists to prevent. This is the one genuinely hard problem the model introduces,
and it must carry a control.

The control is a **cheap, independent check** — not a human picking words:

- Schema constraints reject malformed or out-of-range rules at authoring time.
- A second agent reviews the rule *diff* (not the translation), so no single agent both
  writes and ratifies.
- A human spot-approves **only register-level changes** — formal↔informal, the rare,
  high-blast-radius decisions — and never individual word choices.

This keeps humans out of word-level work while closing the self-legalization gap.

## 6. Delta from what exists today

Two changes and one deletion separate the current repo from the model above.

1. **Flip authoring.** Agents emit the structured rule. The existing schema layer is
   reused unchanged — as the *validator*, not the bottleneck.
2. **Wire the binding loop.** Load each locale's resolved ruleset into its translation
   task (input binding) and make the deterministic gate the task's definition of done
   (output binding).
3. **Delete the human-authored-only premise — not the firewall.** Keep
   prose-never-binds; drop who-may-author.

**Status today (honest inventory).** The binding loop is not built. No
`.resolved/<locale>.json` is consumed by the app repo, and there is no task-close gate.
The only live enforcement is a **PR-level** forbidden-token lint
(`validate-register.yml` on the app repo's `develop` branch, running `bin/lint-register`
from a read-only pinned checkout of this repo) — the backstop described in §2, not the
task gate. One locale (`de_AT`) is governed.

---

*Provenance: merged and de-conversationalized from two agent design notes
(`agent-authored-rules.md` and `enforcement-model.md`) authored on parallel branches.
Non-binding agent analysis; not human input.*
