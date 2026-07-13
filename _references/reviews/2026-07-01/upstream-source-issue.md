[i18n] Source-side (en/) locale defects surfaced by the 2026-07-01 review wave

## Context

During reconciliation of the 29-locale update wave (merged main, HEAD includes batch merge `833b43aae` and content-hash commit `37ebfb6f5`), several defects were traced back to the **English source** (`locales/content/en/…`) and the hash/export pipeline — not to any translator. Every locale faithfully mirrored the source, so these were correctly left untouched in the per-locale PRs. Fixing each once in `en/` (or in the pipeline) benefits all 29 locales at the same time; patching them per-locale would only desync the affected files from source.

All items below are **confirmed** or **partial** and scoped to the source side. Retrospective/bookkeeping, glossary, process, base-rule, and one refuted claim are listed under *Out of scope / already handled*.

| # | Defect | Source location | Blast radius |
|---|--------|-----------------|--------------|
| 1 | Broken JS ternary shipped as translatable text | `en/admin-colonel.json:6-7` | all 29 locales |
| 2 | SSO term rendered 3 ways | `en/workspace-billing.json` (4 keys) | all 29 locales |
| 3 | `_guidance.*` metadata leaked as `{text}` units (export-tool bug) | export/flatten tool; `en` clean | 28 of 29 locales (~82 keys) |
| 4 | Phantom `source_hash` + "region domain" jargon | `en/00-common.json:1373-1376` | all 29 locales |
| 5 | Hand-typed placeholder `content_hash`es | `en/workspace-branding.json:150-165` | all 29 locales |
| 6 | Raw un-localized model enum in `%{status}` | `en/api-invite-errors.json:17-20` + app layer | all locales |
| 7 | Inconsistent casing of "homepage" | `en/secret-homepage.json:58-60` vs `:150-152` | source-side (seeds downstream) |
| 8 | Founder's name "Delano" shipped as the support signature | `vi/email.json` (20 keys) | `vi` (user-facing) |

---

## 1. Broken JS ternary shipped as translatable text (`admin-colonel.json`)

**File:** `locales/content/en/admin-colonel.json:6-7` (key `web.colonel.customer_verified_verified_not_verified_0`, `content_hash 52e93cc0`)

**Offending value:**

```
`+customer.verified ? `verified` : `not verified
```

**Why it's wrong:** This is a mangled template-literal + ternary fragment (leading backtick, `+customer.verified`, ` ? … : … `), not user copy. It is a byproduct of a stale auto-extraction: the whole file is 208 flat machine-generated `web.colonel.*_0` keys (e.g. line 3 `customer_secrets_created_customer_secrets_shared_0 = "{0}/{1}/{2} [{3}]"`).

**Blast radius:** All 29 locales carry the same broken key and mirror the ternary shape (spot-checked eo/da_DK/hu/uk/vi/de/ja/ar and more). Several translators localized the inner labels (e.g. hu `` `+customer.verified ? `ellenőrizve` : `nem ellenőrizve ``), so the garbage is now also **inconsistent** across locales, and a couple mangled it further (`de_AT` lost the leading backtick and broke quoting; `it_IT` dropped a space `` `+cliente.verificato?` ``).

**Fix in `en/`:** Prune the stale `admin-colonel.json` legacy-extraction file rather than "correcting" the string. The 208 flat keys are orphaned (see *Out of scope* — no `src/` consumer). After confirming no legacy Ruby colonel view reads these flat keys, delete the file at source; the hash-sync then removes it from every locale. Do **not** patch per-locale.

---

## 2. SSO term rendered three ways in one file (`workspace-billing.json`)

**File / keys (all in `locales/content/en/workspace-billing.json`):**

- `:230-232` `web.billing.overview.entitlements.manage_sso` = `"Single Sign-On (SSO)"` (`5db5c812`)
- `:246-248` `web.billing.overview.entitlements.sso` = `"Single Sign-On"` (`cf7cd744`)
- `:318-320` `web.billing.features.sso` = `"Single Sign-On (SSO)"` (`5db5c812`)
- `:346-348` `web.billing.features.manage_sso` = `"SSO"` (`5ba3ac9f`)

**Why it's wrong:** One concept, **4 keys / 3 renderings / 3 hashes** ("SSO", "Single Sign-On (SSO)", "Single Sign-On"). The `features.sso` and `entitlements.manage_sso` keys collide on `5db5c812` because their text is identical — `content_hash` is content-addressed, which is exactly why a per-locale fix desyncs from source. The naming is also semantically inverted between sections: the `manage_sso` suffix is terser than `sso` under `features.*` but more verbose than `sso` under `entitlements.*`, so the same suffix resolves to different text depending on section. This is authoring inconsistency, not intentional variance.

**Blast radius:** All 29 locales faithfully mirror the three renderings. `pl` (#3593), `vi` (#3601), and `fr_CA` (#3584) explicitly declined to normalize per-locale, citing source desync.

**Fix in `en/`:** Pick one canonical rule — recommend `"Single Sign-On (SSO)"` on first use / detail views, `"SSO"` for terse feature bullets — and apply it consistently across both `features.*` and `entitlements.*`. Regenerate `content_hash`es via the `locales:hashes` script and re-propagate `source_hash` to all locales; the ~30 locale files then re-sync automatically.

---

## 3. `_guidance.*` metadata leaks as translatable strings (export-tool artifact)

**Root cause:** The export/flattening tool converts nested underscore-prefixed metadata objects into flat `{text: …}` translatable units.

**Source is clean:** `en/session-auth.json:165` holds only the nested structural form:

```json
"web.auth.verify._guidance": { "context": "Email verification flow after signup" }
```

(no `text`; `en/session-auth-extended.json:2/64/354` use `{ "skip": true, … }`). `en` has **zero** flat `_guidance.context` keys.

**What leaked:** Every non-en locale carries the flattened dotted key in translatable shape, e.g. `pl/session-auth.json:403`:

```json
"web.auth.verify._guidance.context": { "text": "Email verification flow after signup" }
```

Three such keys per locale: `web.auth.verify._guidance.context`, `web.auth.security._guidance.context`, `web.auth.sessions._guidance.context`. These are pipeline metadata — the `security` one is literally an internal note referencing `src/locales/SECURITY-TRANSLATION-GUIDE.md` — emitted as user-translatable units. Harm is materialized: `ru`/`de`/`ja`/`ko` actually **translated** the metadata.

**Blast radius:** 28 of 29 locales (`it_IT`=0 fully stripped, `sv_SE`=2 partial, 27 others=3), roughly **82 leaked keys**; `fr/` has no session-auth files.

**Fix (pipeline + one-time cleanup):** Fix the export/flatten tool so nested underscore-prefixed metadata objects (`._guidance` and their `.context`/`._meta` children) inherit the `skip:true` / non-translatable treatment the nested form already carries, instead of being emitted as flat `{text}` units. Then run a one-time cleanup deleting the ~82 leaked flat keys across all locales so state matches `en`.

---

## 4. Phantom `source_hash` + "region domain" jargon (`00-common.json`)

**File:** `locales/content/en/00-common.json:1373-1376`, `web.INSTRUCTION.phishing_warning`, text ending `"…check the region domain before creating new links."`, `content_hash 68ec20f8`.

**Why it's wrong (two issues):**
1. **Hash desync:** Every locale stores `source_hash "b588f5b2"` for this key (e.g. `de/00-common.json:1301-1304`, `ar` same), but `b588f5b2` was **never** an en `content_hash` for this key (`git log -S` confirms it is a phantom). Control keys match exactly (`web.pricing.title` en=`97e283c7`=de.source=ar.source), so this is an en source edit merged **without** re-propagating `source_hash`. Result: the staleness tracker permanently flags every `phishing_warning` translation as out-of-date, even though the translations are already fine (de_AT `:1301-1304` "…überprüfen Sie die Domain der Region", el_GR "…ελέγχετε τον τομέα").
2. **Jargon:** "region domain" is unusual phrasing that invited garbled/redundant translations (de_AT "Regionen-Bereich", el_GR redundant "τομέα της περιοχής").

**Blast radius:** All 29 locales carry the phantom `source_hash`.

**Fix in `en/`:** Re-run content-hash propagation so every locale's `source_hash` for `phishing_warning` == en `68ec20f8`. Reword the en source to drop the ambiguity, e.g. "verify the region's domain in your address bar."

---

## 5. Hand-typed placeholder `content_hash`es (`workspace-branding.json`)

**File:** `locales/content/en/workspace-branding.json:150-165` — keys `powered_by_onetime_secret`, `low_contrast_warning`, `contrast_ratio_label`, `keyhole_logo_icon`.

**Why it's wrong:** These keys were seeded (commit `680f2afd04`) with obviously fake sequential-hex placeholders — `d8e9f0a1`, `a1b2c3d4`, `e5f6a7b8`, `f2a3b4c5` — with text identical to today. en is now corrected to real hashes (`1f393117`/`2d6e7516`/`d521a5be`/`c868ac60`), but the source text never changed, so the "content hashes --apply" tail that reported these as "source moved / content_hash rewritten" misattributed the cause (bogus seed hashes, not an edit).

**Blast radius:** All 29 locales still store a placeholder as `source_hash` for 3 of the 4 branding keys (e.g. `de/workspace-branding.json:147-156` shows `d8e9f0a1`/`a1b2c3d4`/`e5f6a7b8`), so those entries reference a source version that never existed and are mis-tracked.

**Fix:** Re-run `source_hash` propagation to overwrite the placeholder hashes in all 29 locales for the 4 branding keys. Add a PR-time guard rejecting non-sha256 placeholder hashes so hand-typed dummies (`a1b2c3d4`-style) can't enter the tree again.

---

## 6. Raw, un-localized model enum interpolated into copy (`%{status}`)

**Source:** `locales/content/en/api-invite-errors.json:17-20`, `api.invite.errors.invitation_already_processed` = `"Invitation has already been %{status}"` (context "accepted/declined/revoked").

**App layer passes the raw enum:**
- `apps/api/invite/logic/invites/accept_invite.rb:53-55` — `raise_form_error("Invitation has already been #{@invitation.status}", … args: { status: @invitation.status })`
- `apps/api/invite/logic/invites/decline_invite.rb:47-49` — same pattern

`@invitation.status` is the raw model string (`accepted`/`declined`/`expired`).

**Why it's wrong:** Every non-en locale ends up splicing an **English** enum word mid-sentence, where grammar/agreement break: `el_GR:14-16` "Η πρόσκληση είναι ήδη %{status}", `zh:14-16` "邀请已被%{status}", `pl:14-16` reworded to "…obsłużone: %{status}" (detached, but still surfaces the raw English value). This is an app + source design defect; it **cannot** be fixed in locale files.

**Blast radius:** All locales.

**Fix:** Localize the status at the app layer (pass a translated label, e.g. `t('web.invite.status.accepted')`) or drop `%{status}` from the copy entirely. Until then, do not ask locale PRs to "fix" `%{status}`.

---

## 7. Inconsistent casing of "homepage" in the source (`secret-homepage.json`)

**File:** `locales/content/en/secret-homepage.json`
- `:58-60` `web.homepage.visit_onetime_secret_home` = `"Visit {product_name} homepage"` (lowercase)
- `:150-152` `web.homepage.onetime_secret_homepage` = `"{product_name} Homepage"` (capital)

**Why it's wrong:** Two adjacent keys case the same word differently, seeding downstream locales with mixed casing. (The "Homepage" loanword pattern is otherwise resolved: `de`/`de_AT` reverted to "Startseite"; `nl:150-151` keeps "Homepage" as a legitimate Dutch loanword — acceptable.)

**Blast radius:** Source-side; the residual real defect is the mixed en casing, not the locales.

**Fix in `en/`:** Normalize to one casing ("homepage" or "Homepage") across both keys. Leave `nl` "Homepage" as an accepted loanword.

---

## 8. Founder's name "Delano" shipped as the support signature (`vi/email.json`)

**File:** `locales/content/vi/email.json` — **all 20** generic "Support Team" signature keys (`email.welcome.signature`, `email.password_request.signature`, `email.magic_link.signature`, `email.secret_revealed.signature`, `email.expiration_warning.signature`, `email.organization_invitation.signature`, … through `email.subscription_changed.signature`).

**Offending value:** every one of those 20 keys is `"text": "Delano"` — the founder's personal name — instead of a Vietnamese rendering of "Support Team". (`vi`'s `email.feedback_email.signature` is separately fine: `"Hỗ trợ bí mật"`.)

**Why it's wrong:** the en source for these keys is `"Support Team"` (`content_hash dc75bf9f`) — the intended sign-off after commit `1664dd6a4` retired the hardcoded "Delano" signature project-wide. `vi` alone never got the update, so Vietnamese users receive transactional emails (welcome, password reset, secret revealed, MFA, billing, …) signed **"Delano"**. This is **user-facing** and shipped on merged main — the highest-severity item in this list.

**Blast radius:** `vi` only (surfaced while enumerating `*.signature` across all locales; no other locale leaves the founder name or verbatim English "Support Team").

**Fix in `vi/`:** replace the 20 `"Delano"` signature values with a proper Vietnamese "Support Team" rendering (e.g. `"Đội ngũ hỗ trợ"`), matching how every other locale translated `dc75bf9f`. This one *is* a per-locale fix (it is a `vi` translation gap, not an en source defect), but it belongs here as the wave's most consequential residual defect.

---

## Out of scope / already handled

- **Refuted — `admin-colonel.json` is user-facing (defect #1):** No `src/` consumer references these flat `web.colonel.*_0` keys; `grep` for `customer_verified_verified_not_verified`, `web.colonel.customer_`, and `admin-colonel` in `src/` returns nothing. The live colonel UI uses a different, hand-authored nested namespace (`ColonelUsers.vue:93` `v-if="user.verified"`; keys like `web.colonel.titles.index`). The artifact is an **orphaned/dead** key — low severity (bundle/hash noise, not visible breakage) — which is why the fix is *prune*, not *translate*. Confirm no legacy Ruby colonel view reads the flat keys before deletion.
- **Retrospective bookkeeping (not a source fix):**
  - The "five agents refused the SSO keys" roster (#2) is only partly right — the genuine refusers for these four keys are `pl`, `vi`, `fr_CA`. `es` (#3583) edited unrelated SSO keys in `workspace-domains.json`; `pt_BR` left no recorded position.
  - The batch-log `_guidance.*` tabulation (#3) misclassifies `ko` and `mi_NZ` as "deleted" — both retain all 3 keys (`ko` translated the value). Only `it_IT` fully stripped; `sv_SE` partial. Superseded once the pipeline cleanup converges all 28 to 0.
  - The 19 `email.json *.signature` hash rewrites were the **intended** Delano→"Support Team" change (`dc75bf9f`), reconciled late; en deliberately keeps a second sign-off, `feedback_email.signature` = "Secret Support" (`f6a6c90f`). No source fix needed. Recommend a CI check that `content_hash == sha256(text)` so hash lag can't recur (also closes the gap behind #4 and #5).
- **Tracked under other rulebooks (not source):**
  - `base.yaml` `rule.meta-keys-untranslated:32-35` only enumerates three top-level keys and misses mid-path `_guidance` segments in flattened dotted keys — a **base-rule** broadening, companion to defect #3.
  - `de_AT` translating "domain" as "Bereich" (72×) vs `de` "Domain" (111×) is a **glossary-term** decision, not a source defect.
  - Inconsistent formal/informal register enforcement (`pt_PT` email informal "tu/teu/tua" unflagged while `sl_SI` "tvoj" was gated) is a **process/validation-gate** item.

---

## Suggested labels

`i18n`, `source-locale`, `en`, `build-pipeline`, `tech-debt`, `bug`