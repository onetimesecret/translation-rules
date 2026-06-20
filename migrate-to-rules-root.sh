#!/usr/bin/env bash
# migrate-to-rules-root.sh
#
# Consolidate the scattered authored governance source under a single `rules/`
# root. Root keeps only: contract (schema/), tooling (lib bin tests .github
# pyproject uv.lock), meta (README, SPEC*, BACKLOG), _references/, generated/.
#
# MOVES (git mv, history-preserving):
#   base.yaml          -> rules/base.yaml
#   baselines.yaml     -> rules/baselines.yaml      (auto-resolved via base_path.parent)
#   locales/           -> rules/locales/
#   retrospectives/    -> rules/retrospectives/
#   _archive/          -> rules/_archive/            (firewall lives with what it guards)
#
# STAYS AT ROOT:
#   schema/   — $id URLs bake in .../translation-rules/schema/<name>.schema.json; moving breaks canonical refs
#   docs/     — resolver-embedded rationale; kept at root (project_root/docs anchor unchanged)
#   lib/ bin/ tests/ .github/ pyproject.toml uv.lock — tooling
#   README.md SPEC.md SPEC-cross-property.md BACKLOG.md — meta
#   _references/ generated/ — non-governing / output
#
# macOS/BSD sed (-i '') — this repo runs on darwin.
set -euo pipefail
cd "$(dirname "$0")"

if [ -n "$(git status --porcelain)" ]; then
  echo "error: working tree not clean; commit or stash first" >&2
  exit 1
fi

echo "== Phase 1: move source trees under rules/ =="
mkdir -p rules
git mv base.yaml        rules/base.yaml
git mv baselines.yaml   rules/baselines.yaml
git mv locales          rules/locales
git mv retrospectives   rules/retrospectives
git mv _archive         rules/_archive

echo "== Phase 2: repoint resolver path defaults (resolve.py) =="
# CWD-relative defaults used by `resolve.py --all` in CI.
sed -i '' 's|default="locales",|default="rules/locales",|'                 lib/resolver/resolve.py
sed -i '' 's|default="base.yaml",|default="rules/base.yaml",|'             lib/resolver/resolve.py
sed -i '' 's|default="retrospectives",|default="rules/retrospectives",|'   lib/resolver/resolve.py

echo "== Phase 3: repoint REPO_ROOT-anchored gate defaults =="
sed -i '' 's|REPO_ROOT / "retrospectives"|REPO_ROOT / "rules" / "retrospectives"|' lib/resolver/retro_lifecycle.py
sed -i '' 's|REPO_ROOT / "retrospectives"|REPO_ROOT / "rules" / "retrospectives"|' lib/resolver/review_manifest.py

echo "== Phase 4: repoint archive-firewall trees =="
sed -i '' 's|("_archive/", "retrospectives/_archive/")|("rules/_archive/", "rules/retrospectives/_archive/")|' lib/resolver/archive_firewall.py

echo "== Phase 5: repoint bin/lint-register (consumed by app-repo CI via pinned checkout) =="
sed -i '' 's|/locales/${LOCALE}/register.yaml|/rules/locales/${LOCALE}/register.yaml|' bin/lint-register

echo "== Phase 6: rewrite repo-root-relative paths in the UUID index =="
sed -i '' \
  -e 's|"file": "retrospectives/|"file": "rules/retrospectives/|' \
  -e 's|"file": "base.yaml"|"file": "rules/base.yaml"|' \
  -e 's|"file": "baselines.yaml"|"file": "rules/baselines.yaml"|' \
  -e 's|"file": "locales/|"file": "rules/locales/|' \
  lib/resolver/index.json

echo "== Phase 7: repoint archive paths in firewall test fixtures =="
# Promotion-check cases (lines 45-139) only. The -z parser cases below them feed
# arbitrary path strings and assert round-trip equality, so their expected-output
# tuples must stay on the pre-move paths. Quote-anchoring (leading ") additionally
# skips the tests/_archive/ and _archived/ lookalikes, which must remain ungated.
sed -i '' \
  -e '45,139 s|"_archive/|"rules/_archive/|g' \
  -e '45,139 s|"retrospectives/_archive/|"rules/retrospectives/_archive/|g' \
  tests/archive_firewall/run.py

echo
echo "== Move + edits complete. NOT YET DONE (separate, lower-risk): =="
echo "  - SPEC.md §2.1 layout block + path mentions (prose; hand-edit)"
echo "  - README.md path mentions; schema/*.json title/description prose"
echo
echo "== Verify (run after review; all must pass) =="
cat <<'VERIFY'
  grep -rn 'default="locales"\|default="base.yaml"\|REPO_ROOT / "retrospectives"' lib/ bin/   # expect: no hits
  python tests/schema/run.py
  python tests/inheritance/run.py
  python tests/resolver/run.py
  python tests/retro_lifecycle/run.py
  python tests/archive_firewall/run.py
  python tests/review_manifest/run.py
  python lib/resolver/resolve.py --all --lint --validate-only
  git --no-pager diff --stat lib/resolver/index.json   # confirm regen matches the sed
VERIFY
