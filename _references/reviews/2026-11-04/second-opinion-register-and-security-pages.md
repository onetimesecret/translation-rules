# Second opinion: register policy and fr security page (2026-11-04)

Independent review by a separate model agent (read-only) of four proposed actions after the first website translation run (`website-translation-fr.md`). The agent tested each proposal against the workflow script, this repo's history, and the website files. Lightly edited from the delivered text: script line numbers and local timestamps removed. The "Outcome" section was added afterwards.

**A. Register: half agree.** Agree on rerunning de/es with `registerPolicy: "file"`: the script sets `enforceRegister=false` and injects a REGISTER OVERRIDE line, so the es `usted` forbidden tokens won't produce false errors. **Disagree on "correcting" the governance declaration.** It is deliberate: translation-rules commit c930872 (2026-06-22) "Flip de register to informal du ... Per maintainer decision", and both `rules/locales/de/register.yaml` and `es/register.yaml` headers ground the informal lock in the *app* content (`onetimesecret/locales/content/<lang>/*.json`, du ~270x; zero usted). The real finding is that the website (Sie/usted) and the app (du/tú) diverge in register for de and es. That is a product decision for the maintainer, not a governance typo. Use "file" for this run; leave governance alone; log the divergence. Note es is 19% informal (12/62), so "file" will write usted and leave 12 tú strings mixed.

**B. Agree.** Both items were the two remaining `warn` findings in the final fr/security verification round. "jours ouvrés" is the precise term for business days. The mailto prefills the English subject (identical URL in approved text and en source), so the visible text should show the English subject.

**C. Agree, write directly.** Content approved, `filesWritten` for fr lists only fr.json; report `wrote:false`. No rerun needed. `i18n:markdown` is not in the build chain and `generateSecurityContent` requires `web.security` keys, which fr.json has 0 of, so it skips fr. en/security.md and fr/about.md are already markdown through the same `createContentPage` path; the pages schema needs only `title`. Build not run (read-only).

**D. Split.** fr.json: revert. The ` ` escape to a literal NBSP is a JSON no-op; the file previously had 0 literal NBSPs, so the escape was the convention. index.json: not WIP. HEAD has 0/483 entries with `rules/` prefix; working copy 483/483; its mtime falls inside the workflow window; `resolve.py --all` writes it. HEAD is stale since bd9d655 moved files without regenerating, and CI uses `--validate-only` so never catches it. Commit it in translation-rules as a one-line regen rather than revert, otherwise every resolver run recreates the diff.

**French text defects**

- "Pris en charge" should be "Prise en charge" (Version is feminine; also the correct noun form).
- "votre vie privée" for a reporter's privacy reads literal; "confidentialité" fits, but the heading already says it. Optional.
- Infinitive list items (Envoyer/Inclure) are standard French procedural style; not a defect. Version numbers and the mailto URL match the English exactly.
- "de Onetime Secret" matches fr/about.md and most of fr.json; leave.

**Missed**

- de/es security.md stay HTML until their rerun; the scout's drift check should pick them up, confirm it does.
- The website-vs-app register split above is the one decision that needs the maintainer.

**Not verified:** `pnpm build`/`astro check` with the new fr page; native-speaker quality beyond the items listed.

## Outcome

- A: rerun with `"file"` done; governance left unchanged by maintainer decision (`website-translation-de-es.md`). The de/es drift check did pick up `security.md`.
- B: applied, plus "Prise en charge" (eb07836b in onetimesecret.com).
- C: page written by hand; `pnpm check` and `pnpm build` passed afterwards.
- D: fr.json reverted; index.json regenerated in onetimesecret/translation-rules#58.
- The infinitive point was resolved the other way: rule.fr-infinitive-buttons was followed and the steps use "Envoyez" / "Incluez".

## Findings manifest

- Website register diverges from the app and governance register for de and es.
  wont_fix: maintainer decision 2026-11-04 keeps the website formal and governance unchanged; see website-translation-de-es.md.
- fr security.md defects (business days, table header, subject line).
  wont_fix: no rule change needed; fixed directly in content (eb07836b in onetimesecret.com).
- Stale lib/resolver/index.json, not caught by CI's `--validate-only` run.
  wont_fix: index regenerated in onetimesecret/translation-rules#58; a CI regen-and-diff check is noted there as a follow-up.
