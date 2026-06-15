# Archived locale scripts

Locale-tooling scripts retired from `onetimesecret/locales/scripts/` as the i18n
pipeline consolidated on the SQLite task DB (`store.py`, `tasks/*`) plus
`build/compile.py` and `add_hashes.py`. Kept for reference, not for re-running.

## Spent one-shot migration / remediation (job finished)

- `bootstrap.py` — seeded `content/<locale>/` from the old `src/locales/<locale>/` tree; that input dir no longer exists.
- `interpolate_product_name.py` — replaced hardcoded "Onetime Secret" / "One-Time Secret" with `{product_name}` interpolation across locale sources.
- `fix_hashes.py` — repaired empty / "placeholder" / fake-sequential `content_hash` / `source_hash` values from the English source.
- `remove_content_hash_from_translations.py` — stripped `content_hash` that leaked into non-source locales (translations keep only `source_hash`).

## Superseded by current tooling (replaced, not spent)

- `harmonize.py` — repaired locale files to the English key structure; replaced by `migrate/export.py` (which creates missing files) and incompatible with the `source_hash` watermark, which it would strip.
- `json_validate.py` — standalone JSON-syntax check; `validate/pr.py` now does this as its first step.
- `_apply_translations.py` — piped a JSON array of translations into locale files; replaced by `tasks/update.py` writing to the task DB.
- `_extract_english.py` — listed untranslated (text == English) strings; replaced by `tasks/next.py` serving pending tasks from the DB.
