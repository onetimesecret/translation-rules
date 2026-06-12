#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6,<7",
# ]
# ///
"""Retro lifecycle gate tests. SPEC.md §3 (orphan timeout, applied transition).

The two core checks are pure functions over frontmatter dicts, so cases are
inline data rather than file fixtures — there is no load/merge behavior to
exercise here (that is tests/schema/ and tests/resolver/ territory). The git
plumbing in retro_lifecycle.main() is exercised end-to-end by CI itself, which
runs the gate against the real retrospectives/ directory on every PR.

Exit codes: 0 all passed · 1 a case failed · 2 harness setup error.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from resolver.retro_lifecycle import (
        check_applied_transitions,
        check_pending_orphans,
    )
except ImportError as exc:
    print(f"setup: {exc}", file=sys.stderr)
    sys.exit(2)

TODAY = date(2026, 6, 12)


def _retro(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "2026-06-10-example",
        "date": "2026-06-10",
        "status": "pending",
        "affected_rules": [],
    }
    base.update(overrides)
    return base


def run_cases() -> list[tuple[str, bool, str]]:
    """Each case returns (name, passed, detail)."""
    results: list[tuple[str, bool, str]] = []

    def case(name: str, passed: bool, detail: str = "") -> None:
        results.append((name, passed, detail))

    # --- pending-orphan timeout ---

    f = check_pending_orphans([_retro()], TODAY, grace=set())
    case("fresh pending passes", f == [], f"findings={f}")

    f = check_pending_orphans([_retro(date="2026-06-01")], TODAY, grace=set())
    case(
        "overdue pending errors",
        len(f) == 1 and f[0].severity == "error" and f[0].check == "pending_orphan",
        f"findings={f}",
    )

    f = check_pending_orphans(
        [_retro(date="2026-06-01")], TODAY, grace={"2026-06-10-example"}
    )
    case(
        "graced overdue pending warns (non-fatal)",
        len(f) == 1 and f[0].severity == "warning",
        f"findings={f}",
    )

    # Boundary: exactly max_pending_days old is not yet an orphan.
    f = check_pending_orphans([_retro(date="2026-06-05")], TODAY, grace=set())
    case("pending exactly 7 days passes", f == [], f"findings={f}")

    f = check_pending_orphans(
        [_retro(status="applied", date="2026-01-01")], TODAY, grace=set()
    )
    case("old applied retro is not an orphan", f == [], f"findings={f}")

    f = check_pending_orphans([_retro(date="not-a-date")], TODAY, grace=set())
    case(
        "unparseable date errors",
        len(f) == 1 and f[0].severity == "error",
        f"findings={f}",
    )

    # --- applied-transition diff check ---

    applied = _retro(status="applied", affected_rules=["register.de_AT.formality"])

    f = check_applied_transitions(
        [applied],
        base_statuses={"2026-06-10-example": "pending"},
        changed_yaml_contents={
            "locales/de_AT/register.yaml": "rule_ref: register.de_AT.formality\n"
        },
    )
    case("applied transition touching its rule passes", f == [], f"findings={f}")

    f = check_applied_transitions(
        [applied],
        base_statuses={"2026-06-10-example": "pending"},
        changed_yaml_contents={"base.yaml": "id: base\n"},
    )
    case(
        "applied transition missing its rule errors",
        len(f) == 1 and f[0].severity == "error" and f[0].check == "applied_transition",
        f"findings={f}",
    )

    f = check_applied_transitions(
        [applied],
        base_statuses={"2026-06-10-example": "pending"},
        changed_yaml_contents={},
    )
    case(
        "applied transition with no YAML changes errors",
        len(f) == 1 and f[0].severity == "error",
        f"findings={f}",
    )

    f = check_applied_transitions(
        [applied],
        base_statuses={"2026-06-10-example": "applied"},
        changed_yaml_contents={},
    )
    case("already-applied at base is not a transition", f == [], f"findings={f}")

    # New retro filed directly as applied (the 2026-04-12 bootstrap pattern):
    # absent from base, so it IS a transition and must touch its rules.
    f = check_applied_transitions([applied], base_statuses={}, changed_yaml_contents={})
    case(
        "new retro filed as applied must touch rules",
        len(f) == 1 and f[0].severity == "error",
        f"findings={f}",
    )

    structural = _retro(status="applied", affected_rules=[])
    f = check_applied_transitions(
        [structural],
        base_statuses={"2026-06-10-example": "pending"},
        changed_yaml_contents={},
    )
    case(
        "structural retro (empty affected_rules) passes",
        f == [],
        f"findings={f}",
    )

    multi = _retro(
        status="applied",
        affected_rules=["register.de_AT.formality", "rule.de-sie"],
    )
    f = check_applied_transitions(
        [multi],
        base_statuses={"2026-06-10-example": "pending"},
        changed_yaml_contents={
            "locales/de_AT/register.yaml": "rule_ref: register.de_AT.formality\n"
        },
    )
    case(
        "every affected rule must be touched, not just one",
        len(f) == 1 and "rule.de-sie" in f[0].message,
        f"findings={f}",
    )

    return results


def main() -> int:
    results = run_cases()
    failed = [(name, detail) for name, ok, detail in results if not ok]
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"  {detail}"))
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
