#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.21,<5",
#   "referencing>=0.32,<1",
#   "pyyaml>=6,<7",
# ]
# ///
"""Resolver emit + lint fixture runner. SPEC.md §2.3 steps 5-7.

Each fixture under tests/resolver/fixtures/<name>/ is a self-contained project
root with base.yaml, locales/<locale>/*.yaml, optional retrospectives/, and an
expect.json describing what the assembled model / emitted artifacts / lint must
produce. Source commit and generated_at are pinned from expect.json so the JSON
and MD goldens compare byte-for-byte.

expect.json shape:
    {
      "locale": "de_AT",
      "source_commit": "TESTSHA0",          # pinned into artifacts + goldens
      "generated_at": "2026-05-29T00:00:00+00:00",
      "json_golden": "expected/de_AT.resolved.json",     # optional, byte-for-byte
      "md_golden":   "expected/de_AT.for-translators.md", # optional, byte-for-byte
      "lint_ok": true,                       # optional
      "lint_checks": ["forbidden_token"],    # optional: checks that MUST appear
      "declined_includes": ["..."],          # optional: ids in declined_index
      "declined_excludes": ["..."],          # optional: ids NOT in declined_index
      "fold": {"rule.x": ["retro-id"]}       # optional: rule.retro_refs
    }

Lint runs with the fixture's embedded docs loaded via
resolver.resolve.load_lint_docs — docs-lint fixtures just place .md files under
base/docs/ or locales/<locale>/docs/ in the fixture root (or reference them
from a rule's `docs:` list) and assert via lint_ok / lint_checks.

Exit codes: 0 all passed · 1 a fixture failed · 2 harness setup error.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from resolver.emit_json import emit_json
    from resolver.emit_markdown import emit_markdown
    from resolver.lint import lint_model
    from resolver.model import ModelError, build_model
    from resolver.resolve import (
        ResolutionError,
        ResolverInputs,
        load_lint_docs,
        resolve_locale,
    )
except ImportError as exc:
    print(f"setup: {exc}", file=sys.stderr)
    sys.exit(2)

ERROR_TYPES = {"ModelError": ModelError, "ResolutionError": ResolutionError}

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SCHEMA_DIR = REPO_ROOT / "schema"


def _build_inputs(fixture_root: Path) -> ResolverInputs:
    retros = fixture_root / "retrospectives"
    return ResolverInputs(
        base_path=fixture_root / "base.yaml",
        locales_dir=fixture_root / "locales",
        retros_dir=retros if retros.exists() else None,
        schema_dir=SCHEMA_DIR,
        index_path=fixture_root / "resolver" / "index.json",
        project_root=fixture_root,
    )


def _run_fixture(fixture_root: Path) -> tuple[bool, str]:
    expect_path = fixture_root / "expect.json"
    if not expect_path.exists():
        return False, "missing expect.json"
    expect = json.loads(expect_path.read_text())
    locale = expect["locale"]

    # Negative fixture: resolve+assemble must raise the expected error.
    if "error_type" in expect:
        expected_cls = ERROR_TYPES.get(expect["error_type"])
        if expected_cls is None:
            return False, f"unknown error_type {expect['error_type']!r}"
        try:
            r = resolve_locale(locale, _build_inputs(fixture_root), validate_only=True)
            build_model(
                locale=locale,
                merged_rules=r["merged_rules"],
                register=r.get("register"),
                glossary=r.get("glossary"),
                retros=r.get("retros") or [],
                source_commit="TESTSHA0",
                generated_at="2026-01-01T00:00:00+00:00",
            )
        except Exception as exc:  # noqa: BLE001
            if not isinstance(exc, expected_cls):
                return (
                    False,
                    f"wrong error: got {type(exc).__name__}, expected {expect['error_type']}",
                )
            sub = expect.get("error_substring")
            if sub and sub not in str(exc):
                return (
                    False,
                    f"error substring not found: expected {sub!r}, got {str(exc)!r}",
                )
            return True, "ok (raised as expected)"
        return False, f"expected {expect['error_type']} but pipeline completed"

    result = resolve_locale(locale, _build_inputs(fixture_root), validate_only=True)
    model = build_model(
        locale=locale,
        merged_rules=result["merged_rules"],
        register=result.get("register"),
        glossary=result.get("glossary"),
        retros=result.get("retros") or [],
        source_commit=expect.get("source_commit", "TESTSHA0"),
        generated_at=expect.get("generated_at", "2026-01-01T00:00:00+00:00"),
    )

    errs: list[str] = []

    if "json_golden" in expect:
        got = emit_json(model)
        want = (fixture_root / expect["json_golden"]).read_text(encoding="utf-8")
        if got != want:
            errs.append(_first_diff("json", got, want))

    if "md_golden" in expect:
        got = emit_markdown(model, expect.get("source_commit", "TESTSHA0"))
        want = (fixture_root / expect["md_golden"]).read_text(encoding="utf-8")
        if got != want:
            errs.append(_first_diff("md", got, want))

    if "lint_ok" in expect or "lint_checks" in expect:
        docs = load_lint_docs(_build_inputs(fixture_root), locale, model)
        lr = lint_model(model, docs=docs)
        if "lint_ok" in expect and lr.ok != expect["lint_ok"]:
            errs.append(f"lint ok mismatch: got {lr.ok}, expected {expect['lint_ok']}")
        if "lint_checks" in expect:
            got_checks = {f.check for f in lr.findings}
            missing = set(expect["lint_checks"]) - got_checks
            if missing:
                errs.append(
                    f"lint missing expected checks {sorted(missing)} (got {sorted(got_checks)})"
                )

    declined_ids = {d["id"] for d in model["declined_index"]}
    for want_id in expect.get("declined_includes", []):
        if want_id not in declined_ids:
            errs.append(
                f"declined_index missing {want_id!r} (got {sorted(declined_ids)})"
            )
    for bad_id in expect.get("declined_excludes", []):
        if bad_id in declined_ids:
            errs.append(f"declined_index must exclude {bad_id!r} but it is present")

    for rule_id, want_refs in expect.get("fold", {}).items():
        rule = next((r for r in model["rules"] if r["id"] == rule_id), None)
        if rule is None:
            errs.append(f"fold: rule {rule_id!r} not in rules partition")
        elif rule.get("retro_refs") != want_refs:
            errs.append(
                f"fold: {rule_id} retro_refs got {rule.get('retro_refs')}, expected {want_refs}"
            )

    if errs:
        return False, "; ".join(errs)
    return True, "ok"


def _first_diff(label: str, got: str, want: str) -> str:
    g, w = got.splitlines(), want.splitlines()
    for i, (gl, wl) in enumerate(zip(g, w), 1):
        if gl != wl:
            return f"{label} golden mismatch at line {i}: got {gl!r}, want {wl!r}"
    if len(g) != len(w):
        return (
            f"{label} golden length mismatch: got {len(g)} lines, want {len(w)} lines"
        )
    return f"{label} golden mismatch (no line diff found)"


def main(argv: list[str]) -> int:
    targets = argv[1:] if len(argv) > 1 else None
    if not FIXTURES_DIR.exists():
        print(f"setup: fixtures dir missing: {FIXTURES_DIR}", file=sys.stderr)
        return 2
    passed = failed = 0
    for fixture_dir in sorted(FIXTURES_DIR.iterdir()):
        if not fixture_dir.is_dir() or fixture_dir.name.startswith("."):
            continue
        if targets and fixture_dir.name not in targets:
            continue
        try:
            ok, msg = _run_fixture(fixture_dir)
        except Exception as exc:  # noqa: BLE001
            ok, msg = False, f"unexpected error: {type(exc).__name__}: {exc}"
        print(f"  {'pass' if ok else 'FAIL'} {fixture_dir.name}: {msg}")
        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
    print()
    print(f"summary: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
