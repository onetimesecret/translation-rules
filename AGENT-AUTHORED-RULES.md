You're describing a system whose **authoring direction is the opposite of the one that got built** — and the distinction you're drawing is exactly the right one. Let me reflect it back visually so you can see if I've got it.

Here's what I hear you saying, in one line: *you* shouldn't be the author of word choices; **agents should write the rules as a byproduct of doing the translation work** — and the rules then become structured, machine-checked objects that the translation pipeline can't violate.

## 1. The current repo inverted who does the work

```
  ✗  WHAT WAS BUILT                         ✓  WHAT YOU ACTUALLY WANT
     "only humans may author rules"            "agents author rules, safely"

     YOU (human)                               AGENT (me / saas-translator)
       │                                         │
       │  sit down, decide every                 │  hits a word-choice decision
       │  term / register / forbidden            │  *while translating a task*
       │  word, hand-write YAML  ◄── the         │
       ▼      part you refuse to do              ▼
     rules/*.yaml                              emits a STRUCTURED rule
       │                                         │   (schema-shaped, not prose)
       ▼  resolver + CI gate                     ▼  validate → store → enforce
     blocks bad translations                   blocks bad translations
                                                 │
                                                 └──► and the rule feeds the
                                                      next task automatically
```

The enforcement half (left-bottom = right-bottom) the repo **already does well**. The defect is that it put *you* at the top of the pipeline.

## 2. The failure it was built to stop was never "an agent did it"

The 2026-04 `de_AT` flip is usually blamed on *"an agent wrote the rule."* That's the wrong axis. The axis that actually matters is **structured + enforced vs. loose prose**:

```
                  UNSTRUCTURED prose              STRUCTURED + schema + CI-enforced
                  (changelog, retro, notes)       (validated rule + forbidden-token gate)
                ┌────────────────────────────┬────────────────────────────────┐
  HUMAN writes  │  "du feels friendlier"     │  register: formal; forbid: du   │
                │  → still drifts if cited   │  → SAFE                         │
                ├────────────────────────────┼────────────────────────────────┤
  AGENT writes  │  ✗  THE 2026-04 INCIDENT   │  ✓  WHAT YOU WANT               │
                │  agent read prose as rule  │  agent writes a gated rule      │
                │  → silent du-flip          │  → cannot be violated           │
                └────────────────────────────┴────────────────────────────────┘
                     the incident lived             ← this safe quadrant is the
                     in THIS cell only                one the repo banned by
                                                      accident (human-authored-only)
```

The repo killed the **whole bottom row** to kill one **bottom-left cell**. You want the **bottom-right cell** — agent-authored, but structured and enforced so it physically can't be violated. Agent authorship was never the danger; *unstructured* authorship was.

## 3. The shape you're asking for: rules written *inside* the translation loop

```
 ┌───────────────────────── TASK-BASED TRANSLATION (app repo) ─────────────────────────┐
 │                                                                                      │
 │   task: translate key  ──►  agent translates  ──►  proposed string                   │
 │         ▲                          │                      │                          │
 │         │                          │ unknown register /   │                          │
 │         │                          │ term decision        ▼                          │
 │         │                          ▼              ┌────────────────────┐             │
 │         │                 ┌─────────────────┐     │  ENFORCEMENT GATE  │             │
 │         │                 │ agent WRITES a   │    │  string vs. rules  │             │
 │         │                 │ structured rule  │    │  (lint-register++) │             │
 │         │                 └────────┬─────────┘    └─────────┬──────────┘             │
 │         │                          ▼                        │ violates?              │
 │         │              ┌──────────────────────┐     reject ✗ │ ✓ accept              │
 │         │              │ VALIDATE             │             │                        │
 │         │              │ schema + cheap       │             │                        │
 │         │              │ independent check    │             │                        │
 │         │              └──────────┬───────────┘             │                        │
 │         │                         ▼                         │                        │
 │         │              ┌──────────────────────┐             │                        │
 │         └──────────────│   RULE STORE         │◄────────────┘                        │
 │   rules injected into  │  structured,         │   accepted strings become            │
 │   the NEXT task's      │  versioned, machine- │   evidence for future rules          │
 │   context (.resolved)  │  readable            │                                      │
 │                        └──────────────────────┘                                      │
 └──────────────────────────────────────────────────────────────────────────────────────┘
       YOU (human): set direction, spot-approve register-level changes — NOT pick words
```

So, concretely, the delta from what exists today is **two changes, one deletion**:

- **Flip authoring** — the agent emits the structured rule (the repo's schema layer is reusable *as-is* for this; it's the validator, not the bottleneck).
- **Wire the injection** — `rules/.resolved/<locale>.json` actually loaded into each translation task (SPEC §6.1 describes this; I confirmed it's **not built** — there's no `.resolved/` in the app repo yet).
- **Delete the premise** — the "only human-authored YAML may bind" rule and the `_archive` firewall built to enforce it. That's the part fighting you.

**The one thing to get right** (so this isn't me just agreeing): if an agent both *writes* and is *bound by* the rules with zero friction, it can "legalize" its own mistake — author a rule that blesses the wrong word. So the **VALIDATE** box can't be empty. But it doesn't need *you* picking words — it needs a *cheap independent check*: a schema constraint, a second agent reviewing the rule diff, and a human spot-approval **only** on register-level changes (formal↔informal), which are rare and high-blast-radius. That keeps you out of word choices while still closing the bottom-left cell.

Did I get it right? If so, I can render these as a clean PNG/SVG you could drop into a design doc, or turn diagram 3 into a concrete proposal against the actual files (what to add, what to delete).
