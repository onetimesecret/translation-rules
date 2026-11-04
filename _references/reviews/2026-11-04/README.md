# 2026-11-04: onetimesecret.com website translation

Two runs of the `translate-website-i18n` workflow over the website's routed locales (fr, de, es), plus a second opinion between them. The resulting content changes are in onetimesecret/onetimesecret.com#275. The stale resolver index found during the runs is fixed in onetimesecret/translation-rules#58.

| File | What it is |
|---|---|
| `website-translation-fr.md` | Run 1 (`registerPolicy: "strict"`): fr translated, de and es skipped for a register conflict. Assembled after the run because its report step could not write. |
| `second-opinion-register-and-security-pages.md` | Independent review of the follow-up actions, with outcomes. |
| `website-translation-de-es.md` | Run 2 (`registerPolicy: "file"`): de and es in formal register. The run's own report, with post-run changes appended. |
| `artifacts/apply-{fr,de,es}.json` | UI key values each run approved and wrote, before later hand edits (de/es `navigation.docs` was set back to `Docs`). |
| `artifacts/run-1-fr-strict-summary.json`, `artifacts/run-2-de-es-file-summary.json` | Workflow result summaries: scout notes, per-locale approvals, keepEnglish and glossary candidates, translator questions, gate results. Local paths removed. |

Not copied: the resolved governance artifacts (regenerated from this repo by `lib/resolver/resolve.py --all --emit=json`; run 1 used source commit 45773c7 and run 2 used 70c4f45) and the per-agent run journals (local session files).

Key decision: the website keeps formal register for de (Sie) and es (usted), and governance keeps informal (c930872). Website runs use `registerPolicy: "file"`.
