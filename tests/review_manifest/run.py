#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6,<7",
# ]
# ///
"""Review findings-manifest gate tests. SPEC.md §3 (manifest contract,
grandfather clause).

The manifest check is a pure function over (doc_text, known_retro_ids) and
the exemption rule is a pure function over a reviews-dir-relative path, so
cases are inline data rather than file fixtures. The directory walk and
retro-id loading in review_manifest.main() are exercised end-to-end by CI
itself, which runs the gate against the real reviews/ tree on every PR.

Exit codes: 0 all passed · 1 a case failed · 2 harness setup error.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from resolver.review_manifest import (
        GRANDFATHERED,
        check_manifest,
        is_exempt,
    )
except ImportError as exc:
    print(f"setup: {exc}", file=sys.stderr)
    sys.exit(2)

KNOWN_IDS = {"2026-06-01-example-retro"}


def _doc(manifest: str) -> str:
    """A plausible review document body with `manifest` appended."""
    return (
        "# QA review\n"
        "\n"
        "Prose about what was found.\n"
        "\n"
        "## Analysis\n"
        "\n"
        "More prose.\n"
        "\n" + manifest
    )


def run_cases() -> list[tuple[str, bool, str]]:
    """Each case returns (name, passed, detail)."""
    results: list[tuple[str, bool, str]] = []

    def case(name: str, passed: bool, detail: str = "") -> None:
        results.append((name, passed, detail))

    # --- exemptions: grandfather clause and README indexes ---

    case(
        "grandfathered doc is exempt (no manifest required)",
        is_exempt(Path("2025-11-14/polish-translation-review.md")),
    )
    case(
        "every frozen-inventory path is exempt",
        all(is_exempt(Path(p)) for p in GRANDFATHERED),
    )
    # The inventory is frozen at the 30 docs present when the gate landed.
    case(
        "frozen inventory holds exactly 30 paths",
        len(GRANDFATHERED) == 30,
        f"len={len(GRANDFATHERED)}",
    )
    case("top-level README.md is exempt", is_exempt(Path("README.md")))
    case(
        "nested README.md is exempt",
        is_exempt(Path("2026-04-12/README.md")),
    )
    case(
        "new doc in an OLD dated directory is not exempt",
        not is_exempt(Path("2025-11-16/locale-quality-analysis-xx.md")),
    )
    case(
        "new doc in a new directory is not exempt",
        not is_exempt(Path("2026-06-12/some-review.md")),
    )

    # --- manifest presence and placement ---

    f = check_manifest(_doc(""), KNOWN_IDS)
    case(
        "new doc without manifest errors",
        len(f) == 1 and f[0].severity == "error" and f[0].check == "missing_manifest",
        f"findings={f}",
    )

    f = check_manifest(
        _doc("## Findings manifest\n\n- none\n\n## Appendix\n\nExtra prose.\n"),
        KNOWN_IDS,
    )
    case(
        "manifest heading present but not last errors",
        len(f) == 1 and f[0].check == "manifest_not_last",
        f"findings={f}",
    )

    # The heading match is exact — a near-miss does not count as a manifest.
    f = check_manifest(_doc("## Findings Manifest\n\n- none\n"), KNOWN_IDS)
    case(
        "wrong-case heading is a missing manifest",
        len(f) == 1 and f[0].check == "missing_manifest",
        f"findings={f}",
    )

    f = check_manifest(_doc("## Findings manifest\n"), KNOWN_IDS)
    case(
        "manifest with zero bullets errors",
        len(f) == 1 and f[0].check == "empty_manifest",
        f"findings={f}",
    )

    # --- valid manifests ---

    f = check_manifest(
        _doc(
            "## Findings manifest\n"
            "\n"
            "- Formality drift in checkout strings. "
            "retro: 2026-06-01-example-retro\n"
            "- Inconsistent emoji usage. wont_fix: cosmetic, no harm.\n"
        ),
        KNOWN_IDS,
    )
    case("valid manifest (retro tag + wont_fix) passes", f == [], f"findings={f}")

    f = check_manifest(_doc("## Findings manifest\n\n- none\n"), KNOWN_IDS)
    case("`- none` sentinel passes", f == [], f"findings={f}")

    f = check_manifest(
        _doc(
            "## Findings manifest\n"
            "\n"
            "- A long finding description that wraps onto a second line\n"
            "  before naming its tag. retro: 2026-06-01-example-retro\n"
            "- Minor tone mismatch. wont_fix:\n"
            "  source string is being rewritten next sprint.\n"
        ),
        KNOWN_IDS,
    )
    case(
        "multi-line bullet continuation allowed (tag on continuation)",
        f == [],
        f"findings={f}",
    )

    # --- per-bullet tag validation ---

    f = check_manifest(
        _doc("## Findings manifest\n\n- retro: 2026-01-01-typo-id\n"),
        KNOWN_IDS,
    )
    case(
        "unknown retro id errors",
        len(f) == 1 and f[0].check == "unknown_retro_id",
        f"findings={f}",
    )

    f = check_manifest(
        _doc("## Findings manifest\n\n- Stale glossary entry. wont_fix:\n"),
        KNOWN_IDS,
    )
    case(
        "wont_fix with empty reasoning errors",
        len(f) == 1 and f[0].check == "empty_wont_fix_reason",
        f"findings={f}",
    )

    f = check_manifest(
        _doc("## Findings manifest\n\n- Found a thing, should fix sometime.\n"),
        KNOWN_IDS,
    )
    case(
        "bullet with neither tag errors",
        len(f) == 1 and f[0].check == "untagged_finding",
        f"findings={f}",
    )

    # `- none` is a sentinel only as the single bullet; alongside real
    # findings it is just an untagged bullet.
    f = check_manifest(
        _doc(
            "## Findings manifest\n"
            "\n"
            "- none\n"
            "- Real finding. retro: 2026-06-01-example-retro\n"
        ),
        KNOWN_IDS,
    )
    case(
        "`- none` next to other bullets is untagged",
        len(f) == 1 and f[0].check == "untagged_finding",
        f"findings={f}",
    )

    # --- stray content after the heading ---

    f = check_manifest(
        _doc("## Findings manifest\n\nSome closing prose before the list.\n\n- none\n"),
        KNOWN_IDS,
    )
    case(
        "stray prose after the heading errors",
        len(f) == 1 and f[0].check == "stray_content",
        f"findings={f}",
    )

    f = check_manifest(
        _doc("## Findings manifest\n\n### Grouped findings\n\n- none\n"),
        KNOWN_IDS,
    )
    case(
        "subheading inside the manifest is stray content",
        len(f) == 1 and f[0].check == "stray_content",
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
