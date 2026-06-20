# The translation task ⇄ rules binding loop

You're right, and I had the author backwards. Let me redraw what I now understand you're describing — the human is *out* of the word-level loop; agents codify constraints, and the system makes those constraints bind the translation tasks so they can't be broken.

### 1. The correction (what it's NOT → what it IS)

```
   WHAT I WRONGLY DESCRIBED              WHAT YOU ACTUALLY WANT
   ──────────────────────────           ──────────────────────────────
   human picks the words                agent learns a constraint
            │                                     │
            ▼                                     ▼
   human hand-writes YAML               agent writes a STRUCTURED RULE
            │                                     │
            ▼                                     ▼
   machine lints a PR afterward         rule is woven INTO every translation
   (detached, post-hoc)                 task as a binding constraint + a gate
            │                                     │
            ▼                                     ▼
   human is the bottleneck  ✗           human never touches a word  ✓
```

### 2. The loop you're describing (the core)

```
        agent codifies a finding
        as a STRUCTURED RULE
                  │
                  ▼
   ╔═══════════════════════════════════════════════════════╗
   ║                  RULES AUTHORITY                        ║
   ║   rules/locales/de_AT/*.yaml     (schema-validated)     ║
   ║          │  resolve                                     ║
   ║          ▼                                              ║
   ║   .resolved/de_AT.json     →   pinned as ruleset@<hash> ║
   ╚════════════╤══════════════════════════════╤════════════╝
                │ (A) binds the INPUT           │ (C) binds the OUTPUT
                ▼                               ▼
 ┌────────┐  ┌──────────────────────┐   ┌────────────────────┐
 │TASK DB │─▶│   TRANSLATOR AGENT    │─▶ │ DETERMINISTIC GATE │─▶ ✓ task closes
 │de_AT #n│  │ (B) rules in-context: │   │ tokens / glossary  │
 └────────┘  │  Sie · no du/dein ·   │   └─────────┬──────────┘
      ▲       │  secret = Geheimnis  │             │ violation
      │       └──────────────────────┘             ▼
      └───────────────  task cannot close  ◀─────── ✗
```

The rule isn't a downstream lint — it's **pinned into the task** (`ruleset@hash`) and bites at two points: **(A/B)** the translator agent gets the rules *as constraints in its context* before it writes a word, and **(C)** a deterministic gate is the task's definition-of-done. A task literally cannot close while it violates its pinned ruleset. (This is your SPEC §5/§6 — `saas-translator`, `start-translation-session`, `work-tasks-db` — consuming `.resolved/<locale>.json`.)

### 3. Why *two* points = "cannot be violated"

```
   ONLY rules in prompt        ONLY a gate                BOTH  (this design)
   ────────────────────        ───────────────            ───────────────────
   agent usually complies      agent may emit "du"        agent rarely emits "du"
   but CAN still emit "du"     gate blocks it             AND if it does, gate blocks
   → a violation can land      → many wasted reruns       → a violation CANNOT land
       probabilistic               deterministic               guarantee
```

Prompt-adherence alone is probabilistic; the deterministic gate is what upgrades "usually fine" into a guarantee.

### 4. The firewall, reframed (this is the part I had inverted)

```
  WHO may author a rule?  →  an AGENT.  The line is NOT human-vs-agent.
  WHAT may bind a task?   →  only the STRUCTURED CHANNEL.  The line is here:

  ┌─ BINDS ────────────────────────┐   ┌─ NEVER BINDS (explanatory only) ─────┐
  │ rules/locales/<locale>/*.yaml  │   │ retrospectives/*.md                  │
  │ → resolved → ruleset@<hash>    │   │ _archive/*   chat   changelog  PRdesc│
  └────────────────────────────────┘   └──────────────────────────────────────┘
           ▲                                          │
   the de_AT flip is impossible here                  └─ 2026-04-12: a changelog
   because prose can't cross the line                    crossed THIS line → flip
```

The 2026-04-12 incident wasn't "an agent wrote a rule" — it was **prose crossing into the binding set**. The fix isn't to ban agents from authoring; it's that *only structured, resolved YAML crosses the line*. Agents author freely; conversational text never binds.

---

**In one line:** agents turn findings into structured rules → the resolver pins a ruleset per task → the translator agent is bound by it in-context (prevention) and a deterministic gate enforces it at task-close (guarantee) → prose never binds. The human never picks a word.

Where I most want to confirm I've got it: is the gate's *home* the **task's definition-of-done inside the translation pipeline** (with app-repo PR CI as a mere backstop), rather than the PR lint I over-indexed on last time? If yes, that's the loop — and the real build is the **task ⇄ rules binding** (A/B/C above), not more rule-authoring machinery.
