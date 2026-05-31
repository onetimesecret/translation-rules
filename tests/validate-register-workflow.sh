#!/usr/bin/env bash
# tests/validate-register-workflow.sh — proves the P1-4b gate's ORCHESTRATION,
# not just bin/lint-register.
#
# bin/lint-register is already covered by tests/lint-register.sh. This harness
# covers the part that has never executed: the workflow's auto-discovery loop
# (locales/*/register.yaml), per-locale content mapping, skip-if-no-content,
# and the empty-scan guard (scanned==0 -> exit 1).
#
# Faithfulness: it does NOT reimplement the loop. It extracts the LITERAL
# `run:` block from the drafted workflow YAML with yq and executes those exact
# bytes — so what passes here is what will run in onetimesecret/onetimesecret.
# The authority (this repo) is materialized as `.translation-rules/` via
# `git archive HEAD`, the analog of actions/checkout at a pinned ref. App
# content is the existing tests/fixtures/de_AT/ incident files.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKFLOW="${REPO_ROOT}/.github/ISSUE_DRAFTS/p1-4b-validate-register.workflow.yml"
FIX="${REPO_ROOT}/tests/fixtures/de_AT"

if ! command -v yq >/dev/null 2>&1; then
  echo "error: yq is required (https://github.com/mikefarah/yq)" >&2
  exit 2
fi

# The exact bytes that will run in the app repo's CI.
RUN_BLOCK="$(yq '.jobs.validate-register.steps[] | select(.name | test("Lint each governed locale")) | .run' "$WORKFLOW")"
if [ -z "$RUN_BLOCK" ]; then
  echo "error: could not extract lint-loop run block from $WORKFLOW" >&2
  exit 2
fi

# Temp app-dirs cleaned up on exit even if a case aborts.
TMP_DIRS=()
cleanup() {
  [ "${#TMP_DIRS[@]}" -gt 0 ] && rm -rf "${TMP_DIRS[@]}"
  return 0
}
trap cleanup EXIT

PASS=0
FAIL=0

# Build a simulated app-repo tree: the authority checked out at .translation-rules
# plus whatever locale content the caller stages. Echoes the new dir path.
# Caller registers the dir for cleanup (this runs in a command-subst subshell,
# so an append here would not reach the parent).
make_appdir() {
  local appdir
  appdir="$(mktemp -d)"
  mkdir -p "$appdir/.translation-rules"
  # Tracked files only, like actions/checkout; preserves the +x bit on bin/.
  git -C "$REPO_ROOT" archive HEAD | tar -x -C "$appdir/.translation-rules"
  printf '%s' "$appdir"
}

# run_case <name> <expected_exit> <stage-fn>
# stage-fn receives the appdir and populates locales/content/<locale>/.
run_case() {
  local name="$1" expected_exit="$2" stage="$3"
  local appdir rc=0 out
  appdir="$(make_appdir)"
  TMP_DIRS+=("$appdir")
  "$stage" "$appdir"
  out="$( cd "$appdir" && bash -c "$RUN_BLOCK" 2>&1 )" || rc=$?
  if [ "$rc" -ne "$expected_exit" ]; then
    printf 'FAIL  %-22s exit=%s expected=%s\n' "$name" "$rc" "$expected_exit"
    printf '      output: %s\n' "${out//$'\n'/ | }"
    FAIL=$((FAIL + 1))
    return
  fi
  printf 'PASS  %-22s exit=%s\n' "$name" "$rc"
  PASS=$((PASS + 1))
}

# RED — the literal 2026-04-12 incident content routed through the gate loop.
# This is the money shot: the orchestrated gate (not just the bare linter)
# blocks the exact "du/dein/dir" strings that caused the regression.
stage_violation() {
  local appdir="$1"
  mkdir -p "$appdir/locales/content/de_AT"
  cp "$FIX/violations-lowercase.json" "$appdir/locales/content/de_AT/web.json"
}

# GREEN — clean formal content (incl. umlauts) passes.
stage_clean() {
  local appdir="$1"
  mkdir -p "$appdir/locales/content/de_AT"
  cp "$FIX/clean-formal.json" "$appdir/locales/content/de_AT/web.json"
  cp "$FIX/umlauts.json"      "$appdir/locales/content/de_AT/email.json"
}

# GUARD — de_AT is governed upstream but the app has no content dir for it.
# The loop skips it, scanned stays 0, the empty-scan guard fails the job.
stage_nothing() { :; }

run_case red-incident-blocked   1 stage_violation
run_case green-clean-passes     0 stage_clean
run_case guard-scanned-nothing  1 stage_nothing

echo
echo "summary: ${PASS} passed, ${FAIL} failed"
[ "$FAIL" -eq 0 ]
