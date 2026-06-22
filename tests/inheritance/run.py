#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.21,<5",
#   "referencing>=0.32,<1",
#   "pyyaml>=6,<7",
# ]
# ///
"""Inheritance / merge / resolution fixture runner.

Each fixture under tests/inheritance/fixtures/<name>/ is a self-contained
project root containing base.yaml, locales/<locale>/*.yaml, and an expect.json
sidecar describing the expected outcome.

Positive expect.json shape:
    {
      "kind": "positive",
      "locale": "<code>",
      "chain": ["...", "...", "base"],            # optional
      "rule_ids": ["...", "..."],                  # optional
      "merge_strategy": "append",                  # optional sanity hint
      "context_count": <n>, "context_first": "..." # optional
    }

Negative expect.json shape:
    {
      "kind": "negative",
      "locale": "<code>",
      "error_type": "InheritanceError" | "MergeError" | "ResolutionError" | ...,
      "error_substring": "<must appear in the rendered error message>"
    }

Exit codes:
    0 — every fixture behaved as expected
    1 — one or more fixtures behaved incorrectly
    2 — harness setup error
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "lib"))

try:
    from resolver.ids import IdError
    from resolver.inheritance import InheritanceError
    from resolver.loader import LoaderError
    from resolver.merge import MergeError
    from resolver.resolve import ResolutionError, ResolverInputs, resolve_locale
    from resolver.validate import ValidationFailed
except ImportError as exc:
    print(f"setup: {exc}", file=sys.stderr)
    sys.exit(2)

ERROR_TYPES = {
    "InheritanceError": InheritanceError,
    "MergeError": MergeError,
    "ResolutionError": ResolutionError,
    "LoaderError": LoaderError,
    "ValidationFailed": ValidationFailed,
    "IdError": IdError,
}

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


def _check_positive(
    name: str, result: dict[str, Any], expect: dict[str, Any]
) -> list[str]:
    errs: list[str] = []
    if "chain" in expect and result["chain"] != expect["chain"]:
        errs.append(
            f"chain mismatch: got {result['chain']}, expected {expect['chain']}"
        )
    merged = result["merged_rules"]
    if "expect_top_id" in expect and merged.get("id") != expect["expect_top_id"]:
        errs.append(
            f"top id mismatch: got {merged.get('id')!r}, expected {expect['expect_top_id']!r}"
        )
    if "rule_ids" in expect:
        actual_ids = [r.get("id") for r in (merged.get("rules") or [])]
        if actual_ids != expect["rule_ids"]:
            errs.append(
                f"rule_ids mismatch: got {actual_ids}, expected {expect['rule_ids']}"
            )
    if "context_count" in expect:
        ctx = merged.get("context") or []
        if len(ctx) != expect["context_count"]:
            errs.append(
                f"context count mismatch: got {len(ctx)}, expected {expect['context_count']}"
            )
    if "context_first" in expect:
        ctx = merged.get("context") or []
        if not ctx or ctx[0] != expect["context_first"]:
            errs.append(
                f"context first mismatch: got {ctx[:1]!r}, expected {expect['context_first']!r}"
            )
    if "provenance_for" in expect:
        prov = result.get("provenance") or {}
        for cursor, expected_source in expect["provenance_for"].items():
            actual = prov.get(cursor)
            if actual is None:
                errs.append(f"provenance missing for {cursor!r}")
                continue
            # Source paths are absolute in provenance; compare by suffix.
            if not actual.endswith(expected_source):
                errs.append(
                    f"provenance mismatch at {cursor!r}: got {actual!r}, "
                    f"expected suffix {expected_source!r}"
                )
    return errs


def _run_fixture(name: str, fixture_root: Path) -> tuple[bool, str]:
    expect_path = fixture_root / "expect.json"
    if not expect_path.exists():
        return False, "missing expect.json"
    expect = json.loads(expect_path.read_text())
    locale = expect["locale"]
    kind = expect["kind"]
    inputs = _build_inputs(fixture_root)

    try:
        result = resolve_locale(locale, inputs, validate_only=True)
    except Exception as exc:  # noqa: BLE001
        if kind == "positive":
            return False, f"unexpected error: {type(exc).__name__}: {exc}"
        # Negative case.
        expected_type = expect.get("error_type")
        if expected_type:
            expected_cls = ERROR_TYPES.get(expected_type)
            if expected_cls is None:
                return False, f"unknown error_type {expected_type!r} in expect.json"
            if not isinstance(exc, expected_cls):
                return False, (
                    f"wrong error type: got {type(exc).__name__}, expected {expected_type}"
                )
        substring = expect.get("error_substring")
        if substring and substring not in str(exc):
            return False, (
                f"error substring not found: expected {substring!r}, got {str(exc)!r}"
            )
        return True, "ok (raised as expected)"

    if kind == "negative":
        return False, "expected error but pipeline completed successfully"
    errs = _check_positive(name, result, expect)
    if errs:
        return False, "; ".join(errs)
    return True, "ok"


def main(argv: list[str]) -> int:
    targets = argv[1:] if len(argv) > 1 else None
    if not FIXTURES_DIR.exists():
        print(f"setup: fixtures dir missing: {FIXTURES_DIR}", file=sys.stderr)
        return 2

    failed = 0
    passed = 0
    for fixture_dir in sorted(FIXTURES_DIR.iterdir()):
        if not fixture_dir.is_dir() or fixture_dir.name.startswith("."):
            continue
        if targets and fixture_dir.name not in targets:
            continue
        ok, msg = _run_fixture(fixture_dir.name, fixture_dir)
        marker = "pass" if ok else "FAIL"
        print(f"  {marker} {fixture_dir.name}: {msg}")
        if ok:
            passed += 1
        else:
            failed += 1

    print()
    print(f"summary: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
