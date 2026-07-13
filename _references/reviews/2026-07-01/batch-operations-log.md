# _references/reviews/2026-07-01/batch-operations-log.md

---

```bash
~/Projects/dev/onetimesecret/onetimesecret main
venv3.13 ❯ pairs=(
  "3574 i18n/update-ar"   "3575 i18n/update-bg"   "3576 i18n/update-ca_ES"
  "3577 i18n/update-cs"   "3578 i18n/update-da_DK" "3579 i18n/update-de"
  "3580 i18n/update-de_AT" "3581 i18n/update-el_GR" "3582 i18n/update-eo"
  "3583 i18n/update-es"   "3584 i18n/update-fr_CA" "3585 i18n/update-fr_FR"
  "3586 i18n/update-he"   "3587 i18n/update-hu"   "3588 i18n/update-it_IT"
  "3589 i18n/update-ja"   "3590 i18n/update-ko"   "3591 i18n/update-mi_NZ"
  "3592 i18n/update-nl"   "3593 i18n/update-pl"   "3594 i18n/update-pt_BR"
  "3595 i18n/update-pt_PT" "3596 i18n/update-ru"  "3597 i18n/update-sl_SI"
  "3598 i18n/update-sv_SE" "3599 i18n/update-tr"  "3600 i18n/update-uk"
  "3601 i18n/update-vi"   "3602 i18n/update-zh"
)
for pair in "${pairs[@]}"; do
  pr="${pair%% *}"; b="${pair#* }"
  echo "=== PR #$pr ($b) ==="
  git switch "$b" || { echo "skip $b"; continue; }
  claude -p --model claude-sonnet-5 --permission-mode acceptEdits "\
You are on branch $b, which is the head of PR #$pr in onetimesecret/onetimesecret. \
Read that PR's review feedback: gh pr view $pr --comments; gh api repos/onetimesecret/onetimesecret/pulls/$pr/comments. \
For each actionable comment, update this locale's files under locales/content/. Validate JSON. \
Commit each logical change (commit-msg hook adds the prefix; don't hand-add it) and push with git push. \
Do not force-push, rebase, amend, or switch branches. If a comment is ambiguous or you disagree, leave it and note why."
done
git switch main
=== PR #3574 (i18n/update-ar) ===
Switched to branch 'i18n/update-ar'
Your branch is up to date with 'origin/i18n/update-ar'.
Record commit hash.......................................................Passed
Pushed. Both actionable review findings from the automated PR review (Claude bot) are fixed:

1. **`workspace-organizations.json`** — "السر السري" ("secret secret") redundancy in SSO client secret labels → now "سر العميل (Client Secret)" / "سر عميل OAuth الخاص بك"
2. **`workspace-domains.json`** — "تبديل نطاق النطاق" ("switch domain domain") → now "تبديل النطاق", matching the existing sibling key `switcher_locked`'s phrasing

No inline review comments existed (`pulls/3574/comments` was empty); the only substantive feedback was in the bot's review summary, and both flagged items are now resolved. The other items in that review (duplicate error keys across files, brand terms, interpolation tokens) were marked as informational/non-blocking, not actionable requests — left as-is. JSON validated via `i18n validate variables` (0 mismatches), commits pushed to `i18n/update-ar`.
=== PR #3575 (i18n/update-bg) ===
Switched to branch 'i18n/update-bg'
Your branch is up to date with 'origin/i18n/update-bg'.
Record commit hash.......................................................Passed
Done. Reviewed PR #3575's feedback — only one actionable item existed: the Claude review flagged `web.homepage.log_in_to_onetime_secret` in `secret-homepage.json` using a noun form ("Влизане в...") while other imperative CTAs in the bg locale use "Влезте" (e.g. `00-common.json`'s "Влезте в акаунта си"). Fixed to `"Влезте в {product_name}"`, validated JSON, committed (`8815e501e6`), and pushed.

Nothing else was flagged — no inline review comments, and the review verdict was "Approved for merge, no blockers."
=== PR #3576 (i18n/update-ca_ES) ===
Switched to branch 'i18n/update-ca_ES'
Your branch is up to date with 'origin/i18n/update-ca_ES'.
Record commit hash.......................................................Passed
Pushed as `cfc93d116a`. Summary of the review triage:

- **Fixed**: elision inconsistency in `secret-homepage.json` — `visit_onetime_secret_home` and `onetime_secret_homepage` changed from `d'{product_name}` to `de {product_name}`, matching the pattern already used in the three other strings this PR changed.
- **Left as-is, missing `source_hash` on new `00-common.json` strings**: the English source itself has no `content_hash` on these same new keys — hashes are populated later by the `locales:hashes` script, not hand-authored per PR. Not a bug.
- **Left as-is, `web.COMMON.need_help` missing `?`**: matches the English source (`"Need help"`, no `?`) exactly — faithful translation, not a defect.
- **Left as-is, other `d'{product_name}` occurrences** in `feature-translations.json`/`feature-regions.json`: not named in the review; one wasn't even touched by this PR. Out of scope for this pass.
=== PR #3577 (i18n/update-cs) ===
Switched to branch 'i18n/update-cs'
Your branch is up to date with 'origin/i18n/update-cs'.
Record commit hash.......................................................Passed
There are no actionable review comments on PR #3577 — only bot noise (Greptile's "required label not found" and the CI performance metrics summary from github-actions). No reviewer feedback exists to act on.

No changes needed. If a human reviewer leaves comments later, re-run this check.
=== PR #3578 (i18n/update-da_DK) ===
Switched to branch 'i18n/update-da_DK'
Your branch is up to date with 'origin/i18n/update-da_DK'.
Record commit hash.......................................................Passed
All da_DK JSON is valid and the working tree is already clean.

I reviewed PR #3578's feedback — the only review is the automated `claude` bot comment (no human inline comments, no formal GitHub reviews). Its points, checked one by one:

- **`email.feedback_email.signature` = "Secret Support"** — the bot flagged this as possibly missed, but the English *source* itself uses two distinct strings (`"Secret Support"` for feedback emails vs `"Support Team"`/`"Supportteamet"` elsewhere) with different `content_hash` values, so it's a deliberate brand-name variant, not an untranslated leftover. Checking all 30 locales, roughly half (including de, nl, ru, sv_SE, it_IT, he, cs) keep it as literal `"Secret Support"` too — it's an inconsistent project-wide convention, not a da_DK-specific bug. **Leaving as-is**, consistent with the majority sibling-locale pattern.
- **Template literal leak in `admin-colonel.json`**, **`_guidance.context` in English**, **duplicated guidance blocks** — bot itself confirms these are pre-existing/intentional/not introduced by this PR. No action needed.
- **Placeholder integrity / JSON structure** — bot confirmed both are correct.

No code changes were needed; nothing to commit or push.
=== PR #3579 (i18n/update-de) ===
Switched to branch 'i18n/update-de'
Your branch is up to date with 'origin/i18n/update-de'.
Record commit hash.......................................................Passed
The PR review comment from `claude` (a bot) cites `locales/content/de/email.json` line 413 with key `email.email_changed.body` containing a spurious `%{date}`. That key doesn't exist in this file — the actual `email.email_changed.*` keys (subject, title, security_notice, change_notice, new_email_label, changed_at_label, etc.) are correct and match the English source's variables exactly, with no `%{date}` anywhere in that group. All other `%{date}` usages in de/email.json line up 1:1 with en. JSON is valid. No code change matches what the comment describes, so I'm leaving it — the finding appears stale or based on a different file structure than what's in this branch/repo.

No other actionable review comments exist (the `greptile-apps` comment is just a label notice, and the CI metrics comment isn't feedback). Nothing to commit or push.
=== PR #3580 (i18n/update-de_AT) ===
Switched to branch 'i18n/update-de_AT'
Your branch is up to date with 'origin/i18n/update-de_AT'.
Record commit hash.......................................................Passed
Pushed. Summary of changes to `i18n/update-de_AT` (PR #3580), addressing the `claude` bot review:

1. **Critical fix** (`00-common.json`): `phishing_warning` — "überprüfen Sie den Regionen-Bereich" → "überprüfen Sie die Domain der Region" (was semantically garbled).
2. **Warning fix** (`secret-homepage.json`): `onetime_secret_homepage` — reverted "Homepage" loanword regression back to established "Startseite".
3. **Warning fixes** (`workspace-domains.json`): standardized the `web.domains.email.*` group from "Domäne" to "Bereich" (matching the rest of the file's convention), and fixed the missing genitive -s in `domain_overrides_label` ("Bereich-" → "Bereichs-Überschreibungen").

Left untouched: the DMARC hint's "Organisationsdomäne"/"Subdomäne" (real DNS terminology, not the app's "Bereich" feature naming — changing those would invent new terms not requested by the review) and "Domäne"/"Domänen" occurrences outside the email group in `workspace-domains.json`, since the review comment scoped its complaint to that group specifically.

All JSON validated, variable-consistency check clean, 3 commits pushed.
=== PR #3581 (i18n/update-el_GR) ===
Switched to branch 'i18n/update-el_GR'
Your branch is up to date with 'origin/i18n/update-el_GR'.
Record commit hash.......................................................Passed
Done. PR #3581 review had two items in the Claude bot's summary, no other reviewers and no inline comments:

1. **Fixed**: `web.INSTRUCTION.phishing_warning` in `00-common.json` — "τομέα της περιοχής" was redundant (both words mean domain/area); simplified to "τομέα", matching the term used consistently elsewhere in el_GR files. Committed and pushed (888fdf092b).
2. **Left as-is, noted why**: `expires_in_days`/`expires_in_hours` compact suffix format (`"Απομένουν {days}η"`). Checked the source strings (`"{days}d left"`) and the German translation (`"{days}T verbleibend"`) — the no-space single-letter suffix is the established cross-locale convention, not a bug. Not changing it.

The third item flagged by the bot (`%{status}` placeholder in `accept_already_acted`) was explicitly called out as pre-existing/not introduced by this PR, so no action needed there either.
=== PR #3582 (i18n/update-eo) ===
Switched to branch 'i18n/update-eo'
Your branch is up to date with 'origin/i18n/update-eo'.
Record commit hash.......................................................Passed
Confirmed pre-existing, mirrors the English source structure exactly — not something to fix in this locale-only PR.

Summary of PR #3582 review pass:

- **Fixed & pushed**: `Organioznomo` → `Organiznomo` typo in `workspace-organizations.json` (2 occurrences).
- **Stale, no action**: the "critical" `%{date}` mismatch in `email.email_changed.body` — that key was already removed by commit `5049cd5a1` before this review ran; the bot reviewed an outdated version of the file.
- **No action, not eo-specific**: the `admin-colonel.json` JS-code-artifact string and the duplicate `api.organizations.errors.*` keys across two files both mirror the English source exactly — pre-existing structural issues, not something to fix in a single-locale PR.
- **No action, translation is correct**: `phishing_warning` reword (`Friponoj`, `antaŭ ol krei`) — the bot flagged it for native-speaker review, but `antaŭ ol` + infinitive is the grammatically correct Esperanto construction (plain `antaŭ` before a verb is actually wrong), so this is an improvement, not a regression.

Variable validation (`i18n validate variables --locale eo`) is clean. Commit pushed to `i18n/update-eo`.
=== PR #3583 (i18n/update-es) ===
Switched to branch 'i18n/update-es'
Your branch is up to date with 'origin/i18n/update-es'.
Record commit hash.......................................................Passed
Pushed. Summary of PR #3583 review handling:

**Fixed and pushed:**
1. SSO terminology inconsistency — `method_sso` and `sso_enabled_label` changed from untranslated "Single Sign-On" to "Inicio de sesión único (SSO)", matching the convention already used in `sso.title`/`sso_description`.
2. Two untranslated strings in `workspace-domains.json` — `dns_optional_label` ("Recommended" → "Recomendado") and `dns_optional_hint` (full English paragraph translated to Spanish).

**Not actioned (with reason):**
- The "critical" `email.email_changed.body` / `%{date}` bug — this key/string doesn't exist anywhere in the current `email.json` (en or es), and this PR's diff only touches `signature` fields (Delano → Equipo de soporte), never `email_changed`. The review comment doesn't match the actual file content, so there's nothing to fix.
- `email.feedback_email.signature` using "Soporte Secreto" instead of "Equipo de soporte" — review flagged this as a note, not an action item, pending confirmation from you on whether it's intentional.

JSON validated (`python3` load + `i18n validate variables`), 0 mismatches.
=== PR #3584 (i18n/update-fr_CA) ===
Switched to branch 'i18n/update-fr_CA'
Your branch is up to date with 'origin/i18n/update-fr_CA'.
Record commit hash.......................................................Passed
Done. Reviewed all feedback on PR #3584:

- **Critical `%{date}` blocker** — already fixed earlier (commit `5049cd5a1` removed the orphaned `email.email_changed.body` key before this session).
- **`state.viewed` translation drift** ("Lien ouvert" → "Vu") — fixed to match the New/Received/Viewed pattern (Nouveau/Reçu/Vu). Committed and pushed as `83004691d0`.
- **SSO terminology "inconsistency"** — not a bug: the English source itself uses "SSO" for the feature bullet and "Single Sign-On (SSO)" for the entitlement detail view; fr_CA correctly mirrors that. Left unchanged.
- **Non-breaking space before `?!:;`** — not applied anywhere in fr, fr_FR, or fr_CA locale content currently; this is a project-wide typography policy question, not something to unilaterally introduce in one locale's PR. Left unchanged, noting the reason here per your instructions.
=== PR #3585 (i18n/update-fr_FR) ===
Switched to branch 'i18n/update-fr_FR'
Your branch is up to date with 'origin/i18n/update-fr_FR'.
Record commit hash.......................................................Passed
Pushed.

Summary of PR #3585 review triage:

- **The `%{date}` extra-variable bug in `email.email_changed.body`** flagged by the Claude bot review — already resolved by an earlier commit (`5049cd5a1 "Remove orphaned email.email_changed.body locale key"`), before this PR was opened. No action needed; verified with `i18n validate variables --locale fr_FR` (clean, no output).
- **Missing `renderer`/`source_hash` fields** on 11 newly-added `email.json` keys, also flagged by the bot — this was real and part of this PR's diff. Fixed: added `renderer: "erb"` + `source_hash` (matching the EN source's `content_hash`) to 10 keys, and `renderer: "erb"` alone to `email.expiration_warning.signature` (EN source itself lacks a `content_hash` for that key, so no `source_hash` to copy). Left `email.common.support_label` untouched — it already matches the EN source's minimal shape (no renderer/hash there either).
- **`trust_zero_retained` wording** ("Zero retained" → "Aucune donnée conservée") — bot called this a minor liberty, not a bug. Left as-is; it's a legitimate translation choice, not incorrect.
- No inline review comments existed on the PR (`pulls/3585/comments` returned `[]`) — only the bot's summary review.

Committed as `ac1c19e079` and pushed to `i18n/update-fr_FR`.
=== PR #3586 (i18n/update-he) ===
Switched to branch 'i18n/update-he'
Your branch is up to date with 'origin/i18n/update-he'.
Record commit hash.......................................................Passed





Pushed successfully. Summary:

**Actioned (2 commits):**
1. `email.feedback_email.signature` — was left as English `"Secret Support"`, the only outlier among 20 signature keys in `he/email.json` (all others use `צוות התמיכה`). Fixed to match.
2. `web.COMMON.click_to_continue` — arrow `→` trailed the text (LTR convention), inconsistent with the `ar` (also RTL) sibling locale which flips to `←` at the start. Fixed to match RTL convention.

**Not actioned (per reviewer's own notes, not clear defects):**
- Empty `broadcast` string — explicitly `"skip": true`, intentional.
- Missing `source_hash` on new entries — reviewer flagged this as "consistent with codebase... expected behavior," not a defect.
- Masculine imperative forms — reviewer framed as a future accessibility consideration, not an actionable fix for this PR.

No inline PR review comments existed on the diff (`pulls/3586/comments` returned 0) — the only substantive feedback was in the bot's PR-level comment, addressed above. JSON validated and `i18n validate variables --locale he` passes (0 mismatches).
=== PR #3587 (i18n/update-hu) ===
Switched to branch 'i18n/update-hu'
Your branch is up to date with 'origin/i18n/update-hu'.
Record commit hash.......................................................Passed
No changes needed on PR #3587.

**Review findings:** Only one substantive review comment exists (from the `claude` bot), verdict "✅ Approved for merge." No inline comments, no formal GitHub reviews, no greptile findings (greptile just posted a label-gate notice).

The bot's 4 observations, checked against `git diff origin/main...HEAD -- locales/content/hu/`:

1. **Template literal artifact** (`admin-colonel.json`, `customer_verified_verified_not_verified_0`) — pre-existing key on `origin/main`, not touched by this PR. Source-side issue, not this locale's to fix.
2. **`content_hash` vs `source_hash` field naming** — explicitly noted as established repo convention, no action.
3. **New keys missing `source_hash`** — explicitly expected/transitional until `locales:hashes` runs.
4. **`"domainek"` vs `"domén"` inconsistency** (`00-common.json`, `custom_domains_title`) — not in this PR's diff either; pre-existing, out of scope.

All 27 changed files validate as JSON. Nothing to commit or push — branch is unchanged.
=== PR #3588 (i18n/update-it_IT) ===
Switched to branch 'i18n/update-it_IT'
Your branch is up to date with 'origin/i18n/update-it_IT'.
Record commit hash.......................................................Passed
Pushed. Summary: the only actionable feedback on PR #3588 was from the Claude review bot — 3 spurious `web.*._guidance.context` dotted-literal keys (export-tool artifacts, not present in the English source) in `session-auth.json` and `session-auth-extended.json`. Removed them, fixed a resulting trailing comma, validated JSON and ran `i18n validate pr`, committed (`a7ddb489b0`), and pushed. The other two review threads (greptile's label gate, CI metrics bot) weren't actionable content feedback.
=== PR #3589 (i18n/update-ja) ===
Switched to branch 'i18n/update-ja'
Your branch is up to date with 'origin/i18n/update-ja'.
Record commit hash.......................................................Passed
No further action needed. Summary:

- Fetched PR #3589's review feedback: one bot-authored review (Claude) flagged a blocker — a spurious `%{date}` variable in `email.email_changed.body` (ja/email.json) not matching the English source. No human/line-level review comments exist (`pulls/3589/comments` and `/reviews` are both empty).
- That exact key/bug was already removed by commit `5049cd5a1` ("Remove orphaned email.email_changed.body locale key"), which is already an ancestor of `i18n/update-ja` — confirmed via `git merge-base --is-ancestor`. So the blocker is resolved on this branch already.
- The bot's other notes (minor punctuation-style inconsistency, some new keys lacking `source_hash`) were explicitly called non-blocking observations, not action items.
- Working tree is clean, all `ja` JSON files validate. Nothing to commit or push.
=== PR #3590 (i18n/update-ko) ===
Switched to branch 'i18n/update-ko'
Your branch is up to date with 'origin/i18n/update-ko'.
Record commit hash.......................................................Passed
The one actionable comment (bot flagging an invented `%{date}` placeholder in `email.email_changed.body`) was already resolved — a prior commit (`5049cd5a1`, "Remove orphaned email.email_changed.body locale key") removed the dead key across all 11 affected locales including `ko`, and that commit is already an ancestor of the current branch HEAD. No further changes needed.

The only other PR comments are automated noise (greptile label-gate message, CI performance metrics) — not actionable. Nothing to commit or push; PR #3590 has no outstanding review feedback to address.
=== PR #3591 (i18n/update-mi_NZ) ===
Switched to branch 'i18n/update-mi_NZ'
Your branch is up to date with 'origin/i18n/update-mi_NZ'.
Record commit hash.......................................................Passed
Reviewed PR #3591 feedback — only one actionable item from the `claude` bot review: `email.expiration_warning.signature` used "Tīma Tautoko" instead of the "Te Kapa Tautoko" used by 20+ other `.signature` keys. Fixed, validated JSON, committed (`d5929b5511`), and pushed.

The other two notes in that review were explicitly called out by the reviewer as benign/intentional (not actionable):
- `web.auth.verify._guidance.context` flat-key duplication — reviewer confirmed it's non-user-facing doc metadata, consistent with other locales.
- `email.feedback_email.signature` → "Tautoko Huna" — reviewer confirmed this is correct/intentional.

No other reviewers (greptile, github-actions) left actionable comments; `gh api .../comments` returned no inline review comments either.
=== PR #3592 (i18n/update-nl) ===
Switched to branch 'i18n/update-nl'
Your branch is up to date with 'origin/i18n/update-nl'.
Record commit hash.......................................................Passed
Pushed as `716e6fdc63`.

Summary of PR #3592 review handling:
- **Critical `%{date}` in `email.email_changed.body`**: not applicable — that key was already removed by commit `5049cd5a1` before this PR's diff; no `.body` key or stray `%{date}` exists in the current file.
- **Workspace terminology inconsistency**: fixed. `web.footer.workspace` was left as literal "Workspace"; two new strings mixed in English "workspace". Changed all three to "Werkruimte"/"werkruimtes" to match the established term (`web.layout.workspace`).
- **"Homepage" capitalization**: left as-is — bot noted it's an upstream English-source issue, not something to fix in the nl translation.

JSON validated, `i18n validate variables --locale nl` clean, committed and pushed.
=== PR #3593 (i18n/update-pl) ===
Switched to branch 'i18n/update-pl'
Your branch is up to date with 'origin/i18n/update-pl'.
Record commit hash.......................................................Passed
Pushed. Summary:

Fixed 2 of the 3 actionable review comments from the `claude` bot on PR #3593:

1. **`api-invite-errors.json`** — `invitation_already_processed` changed from raw `"Zaproszenie zostało już %{status}"` to the grammatically correct `"Zaproszenie zostało już obsłużone: %{status}"`, matching the established pattern in `accept_already_acted`.
2. **`workspace-domains.json` (×2) + `workspace-organizations.json`** — `"Nieskonfigurowano"` → `"Nie skonfigurowano"` (standard two-word Polish form), matching the sibling tooltip strings.

**Left unfixed (item 3, SSO label inconsistency):** Checked `locales/content/en/workspace-billing.json` — the English source itself has `features.manage_sso` = `"SSO"` (bare) while `features.sso` and `entitlements.manage_sso` = `"Single Sign-On (SSO)"`. The Polish translation is a faithful match to the English source, not a translation error. This is a source-content inconsistency in `en`, out of scope for a locale-update PR — flagging rather than guessing at intent.

Both fixes validated with `json.load` and `i18n validate variables --detailed --locale pl` (no discrepancies), committed separately, and pushed.
=== PR #3594 (i18n/update-pt_BR) ===
Switched to branch 'i18n/update-pt_BR'
Your branch is up to date with 'origin/i18n/update-pt_BR'.
Record commit hash.......................................................Passed
Reviewed PR #3594 feedback:

**Critical bug (fabricated `%{date}` in `email.email_changed.body`)** — already fixed. Commit `5049cd5a1` ("Remove orphaned email.email_changed.body locale key") removed that key entirely from `pt_BR/email.json`, which is already in this branch's history. No action needed.

**Two other items are flagged as "maintainer decision," not bugs — leaving as-is:**
- "Workspace" left untranslated in new keys vs. existing `web.layout.workspace_context` → "Contexto da área de trabalho". Ambiguous whether "Workspace" is being treated as a brand term; not something I should decide unilaterally.
- Title Case in billing feature labels (`Gerenciamento de Organizações`, etc.) — reviewer notes this likely mirrors English source styling for plan-feature badges intentionally; also a style call, not a defect.

The only inline review comments API call returned empty (`[]`) — no line-level comments exist, only the bot summary. Greptile's comment was just a label-gating notice, no content.

Working tree is clean, nothing to commit or push — the actionable fix was already present on the branch.
=== PR #3595 (i18n/update-pt_PT) ===
Switched to branch 'i18n/update-pt_PT'
Your branch is up to date with 'origin/i18n/update-pt_PT'.
Record commit hash.......................................................Passed







Pushed. Summary of the PR #3595 review pass:

**Fixed and pushed** (commit `1791dfc99f`):
- `workspace-domains.json`: `web.domains.incoming.tooltip_configured` used parenthetical plural `destinatário(s)` — inconsistent with the codebase's pipe-plural convention (`{count} X | {count} Xs`, as used in `web.domains.incoming.recipient_count` and billing files). Converted to pipe-plural form.

**Left unchanged, with reasoning:**
- **`example.com` vs `exemplo.com` mix**: The reviewer's own recommendation ("validation messages should stay `example.com`, example/placeholder UI fields can be left localized as `exemplo.com`") already matches the current file state — `signup.domain_placeholder`/`invalid_domain` use `example.com`, while placeholder fields like `secrets_example_dot_com` and `from_address_placeholder` use `exemplo.com`. Nothing to change.
- **T/V register inconsistency in `email.json`** (informal `tu` vs formal `você` across templates): reviewer explicitly called this pre-existing and non-blocking. Checked the PR diff — this PR only touched the `signature` fields (`Delano` → `Equipa de Suporte`) plus a few new keys; it never modified the body text of `email_changed`/`email_change_requested`/`email_change_confirmation` where the formal register lives. Fixing register consistency requires a project-wide tu/você decision and retranslating body copy — out of scope for this locale-update PR. Leaving it for a dedicated follow-up.

Validated with `python3 locales/scripts/i18n validate variables --locale pt_PT` (0 mismatches) and JSON parse check before committing.
=== PR #3596 (i18n/update-ru) ===
Switched to branch 'i18n/update-ru'
Your branch is up to date with 'origin/i18n/update-ru'.
Record commit hash.......................................................Passed
The only actionable feedback on PR #3596 — the stray `%{date}` variable in `email.email_changed.body` — was already resolved in commit `5049cd5a1`, which removed the orphaned key entirely across `ru` and 10 other affected locales (a broader fix than a per-locale text edit, since the key isn't rendered by any template). No inline review comments exist on this PR; the only other bot posts are a Greptile label notice and CI metrics, neither actionable.

Working tree is clean, JSON is valid, and the branch is already up to date with `origin/i18n/update-ru` — nothing to commit or push.
=== PR #3597 (i18n/update-sl_SI) ===
Switched to branch 'i18n/update-sl_SI'
Your branch is up to date with 'origin/i18n/update-sl_SI'.
Record commit hash.......................................................Passed
Fixed and pushed (commit `29315d1013`).

Reviewed all comments on PR #3597: only the `claude` bot review had actionable content — the untranslated `email.feedback_email.signature` ("Secret Support" instead of "Ekipa za podporo") in `email.json`. All other observations in that review were noted as expected/acceptable behavior (mixed hash field names, missing `source_hash` on newer keys, English technical terms), not requests for changes. Fixed the signature to match the pattern used by every other signature key in the sl_SI `email.json`, validated JSON and i18n variable checks (0 mismatches), committed, and pushed.
=== PR #3598 (i18n/update-sv_SE) ===
Switched to branch 'i18n/update-sv_SE'
Your branch is up to date with 'origin/i18n/update-sv_SE'.
Record commit hash.......................................................Passed
Pushed. Summary of the PR review comment (from the `claude` bot) and what I did:

**Fixed (2 commits):**
1. `web.auth.verify._guidance.context` in `session-auth.json` — spurious metadata key leaked in as a translatable string (same bug pattern already fixed in it_IT/ko for other locales). Removed.
2. `email.feedback_email.signature` — left as English "Secret Support" while most other locales (es, fr_FR, ja, pt_PT) translated it. Translated to "Hemlig Support".

**Left as-is, with reasoning:**
- `web.COMMON.switch` ("byt") — bot flagged as inconsistent capitalization, but the English source itself uses lowercase `"switch"`. Matches source; not a bug.
- `web.auth.account.session_count` parenthetical plural ("aktiv(a) session(er)") — bot suggested pipe-pluralization, but the English source uses `"{count} active session(s)"` and every other locale (de, es, fr_FR) mirrors that same parenthetical format for this key. Consistent cross-locale pattern, not an error.
- `web.COMMON.caution_zone` verbosity — explicitly flagged by the bot as a style preference, not a correctness issue.
- Missing `source_hash` on new entries — expected behavior per the content-hash pipeline (populated by running `locales:hashes`, not hand-authored); not a per-locale fix.

Both changed files validated as JSON and passed `i18n validate variables`.
=== PR #3599 (i18n/update-tr) ===
Switched to branch 'i18n/update-tr'
Your branch is up to date with 'origin/i18n/update-tr'.
Record commit hash.......................................................Passed
Done. PR #3599 had two review sources: a `greptile-apps` label-gate comment (no content) and a Claude automated review with one actionable finding.

Fixed and pushed: `email.feedback_email.signature` in `locales/content/tr/email.json` was `"Secret Destek"`, inconsistent with all 20+ other Turkish email signatures using `"Destek Ekibi"`. Committed as `670d8456d7` and pushed.

The other five findings (identical singular/plural forms for session/member/resent/domain counts) were noted by the reviewer itself as linguistically correct Turkish — count-based nouns don't inflect — so no change needed there.
=== PR #3600 (i18n/update-uk) ===
Switched to branch 'i18n/update-uk'
Your branch is up to date with 'origin/i18n/update-uk'.
Record commit hash.......................................................Passed
Done. PR #3600's review (from the `claude` bot) had three observations, only one actionable for this locale:

1. **Fixed** — pronoun capitalization inconsistency in `workspace-billing.json` (3 instances: lines 7, 99, 895), aligning `вашої`/`вашу` → `Вашої`/`Вашу` to match the formal register used elsewhere in the file and in `email.json`/`session-auth.json`. Committed as `42365d800d` and pushed.
2. **Skipped** — the `_guidance.context` spurious key and the JS-template-literal string in `admin-colonel.json`: reviewer explicitly confirmed both are pre-existing pipeline issues affecting 23+ other locales, not introduced by this PR — out of scope for a single-locale fix.

Note: I initially also capitalized a 4th instance (line 751, "з вашого домену") but reverted it — a grep across the whole `uk` locale showed lowercase `ваш-` forms are actually the dominant convention locale-wide (including the identical phrase in `secret-homepage.json`), so that would have been scope creep beyond what the reviewer flagged, not a genuine fix.
=== PR #3601 (i18n/update-vi) ===
Switched to branch 'i18n/update-vi'
Your branch is up to date with 'origin/i18n/update-vi'.
Record commit hash.......................................................Passed
Confirmed — this is a pre-existing English source defect (broken template literal), not a vi translation issue. Nothing to fix here.

All three review observations are non-actionable for this locale's files:

1. **Missing hashes on new files** — expected pipeline behavior; per established convention new keys stay hash-less until `locales:hashes` runs separately (confirmed in memory: don't hand-author hash values, and don't bundle tree-wide hash rewrites into a feature PR).
2. **SSO heading inconsistency** — traced to source: `en/workspace-billing.json` itself has `entitlements.sso` = "Single Sign-On" (content_hash `cf7cd744`) vs `entitlements.manage_sso`/`features.sso` = "Single Sign-On (SSO)" (content_hash `5db5c812`). The vi translations correctly mirror each distinct source string/hash. Fixing only vi would desync it from source and get overwritten on the next hash sync — this needs a source-side (English) fix first, out of scope for this locale PR.
3. **Colonel template-literal string** — confirmed pre-existing broken English source (`en/admin-colonel.json:7`, raw JS ternary as literal text). The vi translation faithfully mirrors the broken source, which is correct behavior. Not a vi defect.

No inline review comments exist on the PR (API returned `[]`), and all CI checks pass. There's nothing to change in `locales/content/vi/` — I'm leaving the branch as is, no commits needed.
=== PR #3602 (i18n/update-zh) ===
Switched to branch 'i18n/update-zh'
Your branch is up to date with 'origin/i18n/update-zh'.
Record commit hash.......................................................Passed
I reviewed PR #3602's feedback (the automated `claude` review, since there are no human inline comments or `greptile` findings beyond the "required label not found" notice):

1. **Critical: spurious `%{date}` in `email.email_changed.body`** — Already fixed. Commit `5049cd5a1` ("Remove orphaned email.email_changed.body locale key") removed the dead key from zh and 10 other locales; it's already an ancestor of `HEAD` and pushed to `origin/i18n/update-zh`. Nothing to do.

2. **`%{status}` enum interpolation warning** — Left as-is. The reviewer flagged this as a cross-locale, app-layer question ("consider whether `%{status}` values are translatable at the app layer"), not a zh-specific fix, and offered no definitive resolution. Deciding unilaterally for one locale would diverge from the other affected locales.

3. **Spacing cosmetic note** — Reviewer explicitly called this "not a blocker... cosmetic concern for a future pass." Skipped.

All zh JSON files validate. Working tree is clean and branch is up to date with origin — no new commits or push needed.
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
Record commit hash.......................................................Passed
```


---

/Users/d/Projects/dev/onetimesecret/onetimesecret/locales/BATCH_OPERATIONS.md


❯ gh pr list | awk '{print $1}'
3613
3603
3602
3601
3600
3599
3598
3597
3596
3595
3594
3593
3592
3591
3590
3589
3588
3587
3586
3585
3584
3583
3582
3581
3580
3579
3578
3577
3576
3575

python3 locales/scripts/i18n content hashes --apply
==============================  CONTENT WARNING   ==============================
  `content hashes` rewrites hash values across the WHOLE locale tree in 1 pass,
  harmonizing both source content_hash and source_hash values. It is a DRY RUN
  by default -- preview the counts below, then re-run with --apply to write.

  A content_hash = sha256(text), so it only changes when source text changes.

          new: a key that had no content_hash at all (a brand-new source
               string); expected.
    unchanged: the recomputed hash matched what was stored; no-op.
      changed: the source text changed; hmm.

  An individual change signals:
    - Punctuation, spelling or grammar
    - Replacing individual words
    - A complete rewrite

  Many changes together can signal something you did NOT intend:
    - Wrong base: branched off an integration/develop-merge that already
      carries the ~2000-hash tree-wide rewrite.
    - The normalization or hashing rule changed, re-stamping every key.
    - A bulk find/replace swept the source tree.

  If the number of changed hashes is wildly larger than the keys you added,
  STOP -- don't stop-drop-and-roll -- run `git diff --stat` and decide whether
  it's expected.

  Valid ameliorations:
    - Raise --max-rewrites for this run (or its default), "nothing to see here".
    - Carve the changed keys out from the new keys into separate PRs.
    - Restore the changed keys so you can merge just the new keys.
================================================================================

Source locale: en
Content dir: /Users/d/Projects/dev/onetimesecret/onetimesecret/locales/content

=== Adding content_hash to source ===
00-common.json: set +10 new, 0 changed (378 keys)
10-layout.json: set +1 new, 0 changed (88 keys)
admin-colonel.json: 208 hashes (no changes)
api-account-errors.json: 2 hashes (no changes)
api-domains-errors.json: 9 hashes (no changes)
api-entitlements-errors.json: set +1 new, 0 changed (23 keys)
api-feedback-errors.json: 1 hashes (no changes)
api-incoming-errors.json: 1 hashes (no changes)
api-invite-errors.json: 7 hashes (no changes)
api-organizations-errors.json: 35 hashes (no changes)
api-secrets-errors.json: 3 hashes (no changes)
email.json: set +2 new, 19 changed (183 keys)
error-pages.json: 19 hashes (no changes)
feature-feedback.json: 18 hashes (no changes)
feature-homepage-secrets.json: 16 hashes (no changes)
feature-incoming.json: 40 hashes (no changes)
feature-regions.json: 48 hashes (no changes)
feature-testimonials.json: 12 hashes (no changes)
feature-translations.json: 23 hashes (no changes)
secret-homepage.json: 46 hashes (no changes)
secret-manage.json: set +2 new, 0 changed (102 keys)
session-auth-extended.json: set +2 new, 0 changed (163 keys)
session-auth.json: set +2 new, 0 changed (111 keys)
workspace-account.json: 174 hashes (no changes)
workspace-billing.json: 258 hashes (no changes)
workspace-branding.json: set +0 new, 4 changed (47 keys)
workspace-dashboard.json: set +3 new, 0 changed (9 keys)
workspace-domains.json: set +63 new, 0 changed (341 keys)
workspace-organizations.json: set +2 new, 0 changed (258 keys)

=== Initializing missing source_hash in locales ===
ar: added 597 missing hashes
bg: added 597 missing hashes
ca_ES: added 597 missing hashes
cs: added 597 missing hashes
da_DK: added 597 missing hashes
de: added 437 missing hashes
de_AT: added 597 missing hashes
el_GR: added 597 missing hashes
eo: added 437 missing hashes
es: added 437 missing hashes
fr_CA: added 437 missing hashes
fr_FR: added 427 missing hashes
he: added 597 missing hashes
hu: added 597 missing hashes
it_IT: added 597 missing hashes
ja: added 437 missing hashes
ko: added 437 missing hashes
mi_NZ: added 597 missing hashes
nl: added 437 missing hashes
pl: added 597 missing hashes
pt_BR: added 437 missing hashes
pt_PT: added 597 missing hashes
ru: added 437 missing hashes
sl_SI: added 597 missing hashes
sv_SE: added 597 missing hashes
tr: added 597 missing hashes
uk: added 597 missing hashes
vi: added 597 missing hashes
zh: added 437 missing hashes

Summary: 88 new key(s), 23 existing hash(es) rewritten, 2512 unchanged.

Changed keys (existing content_hash rewritten -- source moved):
  email.json: email.welcome.signature
  email.json: email.password_request.signature
  email.json: email.magic_link.signature
  email.json: email.secret_revealed.signature
  email.json: email.organization_invitation.signature
  email.json: email.password_changed.signature
  email.json: email.email_changed.signature
  email.json: email.email_change_requested.signature
  email.json: email.email_change_confirmation.signature
  email.json: email.mfa_enabled.signature
  email.json: email.mfa_disabled.signature
  email.json: email.new_login_alert.signature
  email.json: email.member_removed.signature
  email.json: email.role_changed.signature
  email.json: email.organization_deleted.signature
  email.json: email.payment_receipt.signature
  email.json: email.payment_failed.signature
  email.json: email.trial_expiring.signature
  email.json: email.subscription_changed.signature
  workspace-branding.json: web.branding.powered_by_onetime_secret
  workspace-branding.json: web.branding.low_contrast_warning
  workspace-branding.json: web.branding.contrast_ratio_label
  workspace-branding.json: web.branding.keyhole_logo_icon

---

gemini's thought process and actions while deciding on the corrected translation for sl_SI (Slovenian) locale:

Commit: 01a2ea3eac81

### 1. Analyzing the Validation Error
* **The Clue**: The GitHub Actions failure reported a forbidden token `'tvoj'` in the Slovenian (`sl_SI`) locale under two keys in `feature-regions.json`.
* **The Reason**: In Slovenian grammar, **"tvoj"** is the informal/singular possessive pronoun ("your"). The project's linter restricts this register in favor of the formal/plural register **"vaš"** to ensure a professional tone across user-facing copy.

---

### 2. Formulating the Translation Corrections

#### **Key 1: `web.regions.changing_regions_billing_note`**
* **Original Text**: 
  > *"Če se **tvoj** e-poštni naslov za obračunavanje razlikuje od e-poštnega naslova računa {product_name}, **uporabi** e-poštni naslov za obračunavanje za novi regijski račun, da **ohranite** ugodnosti naročnine."*
* **The Register Mismatch**: 
  * *"tvoj"* is informal singular ("your").
  * *"uporabi"* is the informal singular imperative ("use").
  * *"ohranite"* is the formal or plural verb form ("keep/retain").
  * This text mixed informal/singular and formal/plural structures within the same sentence.
* **The Correction**:
  * Change the possessive pronoun from the informal **"tvoj"** to the formal **"vaš"**.
  * Change the imperative verb from the informal **"uporabi"** to the formal **"uporabite"** so that it grammatically aligns with **"ohranite"**.
* **Corrected Sentence**: 
  > *"Če se **vaš** e-poštni naslov za obračunavanje razlikuje od e-poštnega naslova računa {product_name}, **uporabite** e-poštni naslov za obračunavanje za novi regijski račun, da **ohranite** ugodnosti naročnine."*

#### **Key 2: `web.regions.no_region_configured`**
* **Original Text**: 
  > *"Za **tvoj** račun trenutno ni na voljo nobenih informacij o regiji."*
* **The Correction**:
  * Replace **"tvoj"** directly with the formal possessive pronoun **"vaš"**.
* **Corrected Sentence**: 
  > *"Za **vaš** račun trenutno ni na voljo nobenih informacij o regiji."*

---

### 3. Verification & Execution
* **Code Modification**: Surgically modified `locales/content/sl_SI/feature-regions.json` using the `replace` tool.
* **Validation Check**: Ran the local test runner (`pnpm test`) to ensure JSON integrity and TypeScript compilation, resulting in all **6,482 tests successfully passing**.
* **Git Operations**: Staged, committed, and successfully pushed the changes to the remote `i18n/integration-batch` branch.

---

for pr in $(seq 3574 3602); do gh pr view "$pr" --json number,state --jq '"\(.number) \(.state)"'; done
3574 MERGED
3575 MERGED
3576 MERGED
3577 MERGED
3578 MERGED
3579 MERGED
3580 MERGED
3581 MERGED
3582 MERGED
3583 MERGED
3584 MERGED
3585 MERGED
3586 MERGED
3587 MERGED
3588 MERGED
3589 MERGED
3590 MERGED
3591 MERGED
3592 MERGED
3593 MERGED
3594 MERGED
3595 MERGED
3596 MERGED
3597 MERGED
3598 MERGED
3599 MERGED
3600 MERGED
3601 MERGED
3602 MERGED

## Findings manifest

- Glossary decisions for "Secret Support" / "Workspace" surfaced by the wave.
  retro: 2026-07-02-signature-brand-vs-translatable
- Source-side en/ defects and pipeline issues captured here as raw evidence,
  formalized in upstream-source-issue.md. wont_fix: source-repo defects fixed
  upstream, not rules-repo actions.
- rule.meta-keys-untranslated gap (flattened `_`-segment leak). wont_fix:
  resolved in this PR via base.yaml (meta-keys covers underscore segments).
