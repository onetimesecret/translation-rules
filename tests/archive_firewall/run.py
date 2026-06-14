#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Archive firewall gate tests. SPEC.md §2.1 (label-gated archive promotion).

The promotion check and the `-z` record parser are pure functions, so cases
are inline data rather than git fixtures. The git plumbing in
archive_firewall.main() is exercised end-to-end by CI itself, which runs the
gate against the real PR diff on every PR.

Exit codes: 0 all passed · 1 a case failed · 2 harness setup error.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "lib"))

try:
    from resolver.archive_firewall import (
        PROMOTION_LABEL,
        check_archive_moves,
        parse_name_status,
    )
except ImportError as exc:
    print(f"setup: {exc}", file=sys.stderr)
    sys.exit(2)

LABEL = {PROMOTION_LABEL}
NO_LABEL: set[str] = set()


def run_cases() -> list[tuple[str, bool, str]]:
    """Each case returns (name, passed, detail)."""
    results: list[tuple[str, bool, str]] = []

    def case(name: str, passed: bool, detail: str = "") -> None:
        results.append((name, passed, detail))

    # --- promotion check: gated changes ---

    f = check_archive_moves(
        [("R100", "rules/_archive/notes.md", "docs/notes.md")], NO_LABEL
    )
    case(
        "move out of _archive/ without label errors",
        len(f) == 1 and f[0].severity == "error" and f[0].check == "archive_promotion",
        f"findings={f}",
    )

    f = check_archive_moves(
        [("R100", "rules/_archive/notes.md", "docs/notes.md")], LABEL
    )
    case(
        "move out with label warns (exactly one, non-fatal)",
        len(f) == 1 and f[0].severity == "warning",
        f"findings={f}",
    )

    f = check_archive_moves(
        [
            (
                "R087",
                "rules/retrospectives/_archive/old.md",
                "rules/retrospectives/old.md",
            )
        ],
        NO_LABEL,
    )
    case(
        "move out of retrospectives/_archive/ is gated",
        len(f) == 1 and f[0].severity == "error",
        f"findings={f}",
    )

    f = check_archive_moves([("D", "rules/_archive/notes.md", None)], NO_LABEL)
    case(
        "delete from archive without label errors",
        len(f) == 1 and f[0].severity == "error",
        f"findings={f}",
    )

    f = check_archive_moves([("D", "rules/_archive/notes.md", None)], LABEL)
    case(
        "delete from archive with label warns",
        len(f) == 1 and f[0].severity == "warning",
        f"findings={f}",
    )

    f = check_archive_moves(
        [("C075", "rules/_archive/notes.md", "rules/locales/de/notes.md")], NO_LABEL
    )
    case(
        "copy out of the archive is gated",
        len(f) == 1 and f[0].severity == "error",
        f"findings={f}",
    )

    f = check_archive_moves(
        [
            ("R100", "rules/_archive/a.md", "docs/a.md"),
            ("D", "rules/_archive/b.md", None),
        ],
        NO_LABEL,
    )
    case(
        "rename out + delete in one diff yields both findings",
        len(f) == 2 and all(x.severity == "error" for x in f),
        f"findings={f}",
    )

    # --- promotion check: ungated changes ---

    f = check_archive_moves([("A", "rules/_archive/new.md", None)], NO_LABEL)
    case("add into archive passes", f == [], f"findings={f}")

    f = check_archive_moves([("M", "rules/_archive/notes.md", None)], NO_LABEL)
    case("modify inside archive passes", f == [], f"findings={f}")

    f = check_archive_moves(
        [("R100", "rules/_archive/a.md", "rules/_archive/sub/a.md")], NO_LABEL
    )
    case("rename within an archive tree passes", f == [], f"findings={f}")

    f = check_archive_moves(
        [
            (
                "R100",
                "rules/_archive/old-retro.md",
                "rules/retrospectives/_archive/old-retro.md",
            )
        ],
        NO_LABEL,
    )
    case("rename between the two archive trees passes", f == [], f"findings={f}")

    # Moving INTO the archive is demotion, not promotion — unrestricted.
    f = check_archive_moves(
        [("R100", "docs/notes.md", "rules/_archive/notes.md")], NO_LABEL
    )
    case("move into the archive passes", f == [], f"findings={f}")

    # Exactly the two SPEC §2.1 trees are gated; prefix lookalikes are not.
    f = check_archive_moves(
        [
            ("R100", "rules/_archived/foo.md", "docs/foo.md"),
            ("D", "tests/_archive/foo.md", None),
        ],
        NO_LABEL,
    )
    case(
        "_archived/ and tests/_archive/ lookalikes are not gated",
        f == [],
        f"findings={f}",
    )

    f = check_archive_moves([("M", "lib/resolver/resolve.py", None)], NO_LABEL)
    case("record for an unrelated path passes", f == [], f"findings={f}")

    # --- -z record parser ---

    p = parse_name_status("M\0SPEC.md\0")
    case(
        "parser: single modify record",
        p == [("M", "SPEC.md", None)],
        f"records={p}",
    )

    p = parse_name_status("R100\0_archive/a.md\0docs/a.md\0")
    case(
        "parser: rename record carries src and dst",
        p == [("R100", "_archive/a.md", "docs/a.md")],
        f"records={p}",
    )

    p = parse_name_status("A\0_archive/new.md\0D\0_archive/b.md\0C075\0a.md\0b.md\0")
    case(
        "parser: mixed record stream",
        p
        == [
            ("A", "_archive/new.md", None),
            ("D", "_archive/b.md", None),
            ("C075", "a.md", "b.md"),
        ],
        f"records={p}",
    )

    # The reason the gate reads -z output at all.
    p = parse_name_status("M\0_archive/with\ttab\nand newline.md\0")
    case(
        "parser: tabs and newlines inside a filename do not split records",
        p == [("M", "_archive/with\ttab\nand newline.md", None)],
        f"records={p}",
    )

    p = parse_name_status("")
    case("parser: empty diff yields no records", p == [], f"records={p}")

    try:
        parse_name_status("R100\0_archive/a.md\0")
        case("parser: truncated rename record raises ValueError", False, "no exception")
    except ValueError:
        case("parser: truncated rename record raises ValueError", True)

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
