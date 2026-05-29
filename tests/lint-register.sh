#!/usr/bin/env bash
# tests/lint-register.sh — fixture-driven harness for bin/lint-register.
#
# Phase 0 minimum-viable: pure bash, same yq/grep the linter uses, no test
# framework. Asserts exit code and (optionally) a substring on stdout.
#
# Fixtures under tests/fixtures/de_AT/ reproduce verbatim strings from the
# 2026-04-12 incident (commit b08e59838) — see fixture _provenance fields
# and reviews/2026-04-12/cross-locale-audit.md lines 41–48.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LINTER="${REPO_ROOT}/bin/lint-register"
FIX="${REPO_ROOT}/tests/fixtures"

PASS=0
FAIL=0

# run_case <name> <expected_exit> <expected_stdout_grep|""> <locale> <glob>
run_case() {
  local name="$1" expected_exit="$2" expected_grep="$3" locale="$4" glob="$5"
  local out rc=0
  out="$("$LINTER" "$locale" "$glob" 2>&1)" || rc=$?
  if [ "$rc" -ne "$expected_exit" ]; then
    printf 'FAIL  %-22s exit=%s expected=%s\n' "$name" "$rc" "$expected_exit"
    printf '      output: %s\n' "${out//$'\n'/ | }"
    FAIL=$((FAIL + 1))
    return
  fi
  if [ -n "$expected_grep" ] && ! grep -qE "$expected_grep" <<<"$out"; then
    printf 'FAIL  %-22s exit ok (%s) but stdout missing /%s/\n' "$name" "$rc" "$expected_grep"
    printf '      output: %s\n' "${out//$'\n'/ | }"
    FAIL=$((FAIL + 1))
    return
  fi
  printf 'PASS  %-22s exit=%s\n' "$name" "$rc"
  PASS=$((PASS + 1))
}

# Cases below: name, expected exit, stdout substring (regex; "" to skip), locale, glob.
run_case violations-lowercase   1 "forbidden token 'deine'"   de_AT "${FIX}/de_AT/violations-lowercase.json"
run_case lowercase-has-dir      1 "forbidden token 'dir'"     de_AT "${FIX}/de_AT/violations-lowercase.json"
# Capitalized fixture: linter prints the canonical lowercase token in its
# diagnostic regardless of input casing. Asserting 'du' confirms the -i flag
# is doing its job — the matched-line tail still shows the original "Du".
run_case violations-capitalized 1 "forbidden token 'du'"      de_AT "${FIX}/de_AT/violations-capitalized"
run_case clean-formal           0 ""                          de_AT "${FIX}/de_AT/clean-formal.json"
run_case umlauts                0 ""                          de_AT "${FIX}/de_AT/umlauts.json"
# Binary-only: grep -I skips, VIOLATIONS=0, glob has 1 file so the exit-3
# guard is not tripped. Expected behavior is exit 0, not 3.
run_case binary-only            0 ""                          de_AT "${FIX}/de_AT/binary.bin"
run_case mixed-with-binary      0 ""                          de_AT "${FIX}/de_AT/mixed/*"
run_case empty-glob             3 "no files matched"          de_AT "/no/such/path/*.json"
run_case missing-register       2 "register file not found"   zz_ZZ "${FIX}/de_AT/clean-formal.json"

echo
echo "summary: ${PASS} passed, ${FAIL} failed"
[ "$FAIL" -eq 0 ]
