# Recovery Plan — locale content restoration and i18n unfreeze

**Purpose.** Define the process for (a) extracting the known-good historical
translations for the locales contaminated by the 2026-04-12 harmonization
incident, (b) landing them in the app repo behind the new mechanical gates, and
(c) unfreezing regular i18n work, which has been stopped since the incident
(coverage has fallen from ~95% to ~81% as untranslated en keys accumulate).

**Status.** Draft for review, 2026-06-12. Companion to `SPEC.md` (the system
design) — this document covers the one-time content recovery the system was
built to make safe, and the order in which the freeze lifts.

**Authority chain.** Every factual claim about the contamination traces to
`reviews/2026-04-12/cross-locale-audit.md` (per-locale commits and severity)
and `reviews/2026-04-12/locale-quality-analysis-de_AT.md` (baseline
determination). The de_AT baseline is pinned in `baselines.yaml`. The
coverage figures (~95% → ~81%) and the freeze itself are operational facts
supplied by the maintainers — they are not derivable from this repo and
should be re-confirmed against the app repo's i18n tooling before §4
decision point 2 is acted on.

---

## 1. Ground rules

1. **Gate before content.** No recovery PR lands until the app-repo CI gate
   (P1-4b) is live for the locale being recovered. The recovery PRs must be
   the first consumers of the gate — if the gate would not have caught the
   original incident in the recovery PR's own diff, the gate is wrong, and we
   want to learn that on a revert, not on new translation work.
2. **Revert + replay, not `git revert`.** The 2026-04-10 harmonize commits
   mixed legitimate key restructuring with illegitimate text rewrites (the
   anti-pattern now codified in `local-guides/UX-TRANSLATION-GUIDE.md`:
   harmonize = keys only). A plain revert would undo the legitimate key work.
   The unit of recovery is the **string value**, mapped onto the **current key
   structure**.
3. **Restore the split, not one side.** Per
   `locale-quality-analysis-de_AT.md`, the mature de_AT content used a
   semantic split: *Geheimnis* = the secret as object/container (burn, share,
   create, destroy, expire); *Nachricht* = the revealed payload content.
   Demanding *Geheimnis* everywhere would be as wrong as the incident's
   *Nachricht*-everywhere. The recovered content must reproduce the split —
   this is exactly what `locales/de_AT/glossary.yaml` now encodes.
4. **Native-speaker gate at merge.** Mechanical checks bound the damage; they
   do not certify quality. Each recovery PR carries a `Needs-native-review`
   label and a stratified sample review (§4 step 6) before merge.

---

## 2. What to recover from (per locale)

All commits below are in `onetimesecret/onetimesecret`. Layout eras:

- **Single-file era** (until 2025-11-15): `src/locales/<locale>.json`, deleted
  in the reorg commit `be5bdb5ca`.
- **Per-file era** (current): `locales/content/<locale>/*.json`
  (email.json, session-auth.json, …).

| Locale | Contaminating commit | Severity | Recovery source | Source layout |
|---|---|---|---|---|
| de_AT | `b08e59838` | High | `f95b03f44:src/locales/de_AT.json` | single-file |
| uk | `5c7d5c362` | High | `be5bdb5ca^:src/locales/uk.json` | single-file |
| pt_PT | `3f9d8d3d2` | High | `d8834a021` (or earlier post-March pass) | per-file |
| hu | `bea7e1b7e` | High | `d8834a021` (16 formal / 0 informal in email.json) | per-file |
| da_DK | `6c1b55c16` | Medium | fix in place (brand-term swap only) | — |
| zh | `311537d04` | Medium | fix in place (您 erosion, 消息 inflation) | — |

Why de_AT's source is `f95b03f44` and **not** a state nearer the incident:
the incident was the endpoint of a five-month assistant→assistant drift loop,
and `locale-quality-analysis-de_AT.md` settles the question — `f95b03f44` "is
the last known-good human-curated de_AT content … the only defensible
baseline," while the nearer candidate it evaluated (`e5fe5566f^`) "is
downstream of the corrupting loop and carries partial du-form drift."
(`baselines.yaml` pins the same commit while characterizing it as the last
*acceptable* state rather than a curation event; the two sources agree on the
pin, not on the wording.) For uk, the audit names `be5bdb5ca^` a usable
revert source — clean formal Ви throughout.

pt_PT and hu were essentially empty at the reorg; their usable baselines are
the March 2026 translation pass at `d8834a021`, already in the per-file
layout — no key mapping needed, only value restore. Note the asymmetry the
audit records: hu's March state was clean formal *Ön*, but pt_PT's was
"mixed você+tu leaning formal." Recovered pt_PT content therefore needs a
**register-repair pass** (informal 2sg residue removed against its future
`register.yaml`) on top of the restore — budget for it.

**Verify before use.** Each candidate snapshot is confirmed before any values
are taken from it: for de_AT, `Sie/Ihr*` present throughout, zero du-paradigm
tokens, and **both** Geheimnis and Nachricht present (the split intact —
a one-sided count means the wrong snapshot). Measure the snapshot's own
Geheimnis/Nachricht counts at extraction time and carry them forward as the
expected shape for step 4d; the audit's 108/65 figure was measured at
`b08e59838^` (per-file era) and is a shape reference, not the baseline's
expected value. If a snapshot fails its smoke test, stop and re-derive the
baseline; do not improvise forward.

---

## 3. The de_AT extraction pipeline (template for the others)

Run inside a clone of `onetimesecret/onetimesecret`. Steps 1–4 are mechanical
and agent-executable; steps 5–7 carry the human gates.

**Step 1 — extract the snapshots.**

```bash
git show f95b03f44:src/locales/de_AT.json   > /tmp/deAT-baseline.json   # values
git show be5bdb5ca^:src/locales/de_AT.json  > /tmp/deAT-reorg-flat.json # keymap aid
# pre-incident per-file tree (keymap aid only — carries drift, do not take values):
mkdir -p /tmp/deAT-preincident && git archive b08e59838^ locales/content/de_AT | tar -x -C /tmp/deAT-preincident
```

**Step 2 — build the key map (flat → per-file).**
The reorg commit `be5bdb5ca` is the Rosetta stone: it deleted the flat file
and (with its surrounding commits) introduced the per-file layout while
preserving values. Match flat keys to per-file keys by identical value at the
reorg boundary; match the remainder by key-leaf name. Output:
`keymap.de_AT.json` mapping `<flat key> → <file>:<nested key>`. Keys that
exist today but have no flat-era ancestor go to the **retranslate queue**;
flat-era keys with no current counterpart are dropped (retired strings).

**Step 3 — generate the candidate tree.**
For every key in the *current* `locales/content/de_AT/*.json` structure:

- mapped + baseline has a value → take the `f95b03f44` value;
- mapped but baseline value empty → take the `be5bdb5ca^` value if non-empty,
  else retranslate queue;
- unmapped (new since the freeze or since the reorg) → retranslate queue,
  value left as-is for now (current value may be contaminated; queue entries
  are re-done under the new rules, not trusted).

**Step 4 — mechanical validation (all must pass).** Paths assume the P1-4b
layout: this repo as a submodule at `locales/translation-rules/` (per
`.github/ISSUE_DRAFTS/p1-4b-app-repo-integration.md`; the minimal-slice
workflow draft checks out at `.translation-rules` — adjust to whichever
landed).

```bash
# 4a. Register lint — the Phase 0 gate, zero tolerance, runs on the
#     candidate content itself:
locales/translation-rules/bin/lint-register de_AT 'locales/content/de_AT/*.json'

# 4b. Resolver green — regenerate the artifacts the retranslate queue and
#     reviewers consume. Runs INSIDE the submodule (the resolver lints the
#     rules model and embedded examples, NOT app content — content checks
#     are 4a/4c/4d plus the P1-4b CI grep):
(cd locales/translation-rules && python resolver/resolve.py de_AT --lint --emit=md,json)

# 4c. Object/content split spot-grep (locale-quality-analysis item 3):
#     no Nachricht as object of verbrennen/teilen/erstellen/löschen;
#     no Geheimnis in post_reveal / encrypted_message / message_ready keys.

# 4d. Marker-count smoke test: du-paradigm = 0; Sie/Ihr* high; Geheimnis and
#     Nachricht both present in roughly the ratio measured on the baseline
#     snapshot in §2 — a one-sided count is a red flag that the split
#     collapsed again.
```

**Step 5 — retranslate queue.** New keys are translated fresh by the
translator agent consuming `locales/.resolved/de_AT.json` (the SPEC §6.1
contract — not the legacy conventions table), in the same PR or a fast-follow,
each pass re-running step 4.

**Step 6 — native-speaker sample.** Stratified sample across files (suggest
10% per file, minimum 10 strings, weighted toward email/session-auth where the
damage was worst) reviewed by an AT German speaker. Findings either fix
in-place or file a retrospective if they reveal a rule gap.

**Step 7 — land it.** One PR per locale: candidate tree + keymap artifact +
PR description linking `retrospectives/2026-04-12-de_AT-register-flip.md` and
`baselines.de_AT`. The PR must show the P1-4b gate passing. Merge updates the
coverage number; the locale's freeze lifts at merge (§5).

---

## 4. Sequencing and dependencies

```
P1-4a (this repo CI)              [core gates + retro lifecycle live as of
        │                          2026-06-12; _archive/ firewall and
        │                          embedded-docs grep still open — SPEC §2.4]
        │
P1-4b: submodule + CI gate in app repo        [HUMAN-GATED, drafts ready:
        │                                      .github/ISSUE_DRAFTS/p1-4b-*]
P1-5b: de_AT resolver artifacts land in app repo
        │
de_AT recovery PR (§3)            [first real exercise of the gate]
        │
unfreeze de_AT  ──────────────►  regular translation tasks resume for de_AT
        │
pt_PT / uk / hu:                  [each needs register.yaml FIRST —
  register.yaml + recovery PR      knowledge-base work, BACKLOG 2026-04-23:
        │                          audit-backed tokens + source: field +
        │                          native-speaker confirmation]
da_DK / zh fix-in-place PRs       [no full replay; brand-term/您 repairs]
        │
remaining ~28 clean locales       [unfreeze as soon as the gate is live;
                                   they were never contaminated — the freeze
                                   was precautionary. register.yaml authoring
                                   proceeds in parallel waves (Phase 2)]
```

Two explicit decision points for maintainers:

1. **Clean-locale unfreeze timing.** The conservative reading keeps every
   locale frozen until its `register.yaml` exists. The pragmatic reading —
   recommended — unfreezes clean locales once the P1-4b gate is live, because
   (a) the audit found no damage in them, and (b) the gate plus the
   `.resolved/<locale>.json` agent contract already removes the original
   failure vector (prose guidance). Forbidden-token enforcement then arrives
   per-locale as Phase 2 authoring lands.
2. **Coverage backfill.** The 95%→81% drop is mostly *new en keys accumulated
   during the freeze*, not destroyed translations. Backfill is therefore
   ordinary translation work: per-locale tasks through the existing task-DB
   workflow, agents consuming `.resolved/<locale>.json` where it exists, every
   PR passing the gate. de_AT first as the proof, then highest-traffic locales
   first by user impact, not alphabetically.

---

## 5. Per-locale unfreeze checklist

A locale exits the freeze when all of:

- [ ] P1-4b CI gate live in the app repo (repo-wide, once)
- [ ] For contaminated locales: recovery PR merged (§3), with native-speaker
      sample sign-off
- [ ] For pt_PT/uk/hu: `locales/<locale>/register.yaml` authored in this repo
      with audit-backed `forbidden_tokens` and a populated `source:` field
      (BACKLOG 2026-04-23/2026-04-26 — the de_AT paradigm-gap note applies)
- [ ] `.resolved/<locale>.json` present in the app repo **or** the locale is
      clean and maintainers accepted decision point 1 above
- [ ] The translator-agent entry point for the locale no longer reads the
      legacy conventions table (closes the 2026-04-26 conventions-drift retro
      for that locale's slice)

---

## 6. What this plan deliberately does not do

- **No bulk re-translation of contaminated locales from scratch.** The
  historical content is better than fresh machine output — it embodies years
  of curation. Extraction is cheaper and safer than regeneration.
- **No backfill of old reviews into retrospectives** (SPEC §3 stands).
- **No Phase 2 fan-out scheduling.** That is templated after de_AT proves the
  pattern end-to-end (clearinghouse, Phase 2 section).
- **No new tooling in this repo for the extraction.** The keymap/candidate
  scripts in §3 live with the app repo's locale scripts
  (`locales/scripts/`), where they can run against real content in CI;
  this repo stays the rules authority.
