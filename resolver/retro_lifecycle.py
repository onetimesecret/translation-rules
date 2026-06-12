#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6,<7",
# ]
# ///
"""Retrospective lifecycle gate. SPEC.md §3.

Two CI-enforced checks the schema cannot express:

  1. pending-orphan timeout — a retro that stays `status: pending` more than
     7 days without transition blocks the next main PR (SPEC §3: "pending with
     no transition after 7 days blocks next main PR"). A retro id passed via
     `--grace` is downgraded to a warning: the waiver is visible in the
     workflow file as a reviewable diff, and applies to that id only.
  2. applied-transition diff check — the PR that flips a retro to
     `status: applied` must also touch every id in `affected_rules`
     (SPEC §3: "requires PR to also touch every ID in affected_rules").
     Enforced when `--diff-base <ref>` is given: a retro that is `applied` at
     HEAD but not at the base ref must have, for each affected rule id, at
     least one changed YAML file whose HEAD content contains that id.
     Retros with empty `affected_rules` are structural (see the 2026-04-26
     conventions-drift retro) and have nothing to touch — they pass.

Field-shape requirements per status (applied needs `resolved_in_commit`,
declined needs `declined_reason` + `would_change_decision_if`) are enforced by
schema/retrospective.schema.json; supersede pairing is enforced cross-file by
resolver/model.py. Neither is duplicated here.

Usage:
    resolver/retro_lifecycle.py [--retros-dir retrospectives]
                                [--today YYYY-MM-DD]
                                [--max-pending-days 7]
                                [--grace <retro-id>]...
                                [--diff-base <ref>]

Exit codes:
    0  all checks passed (warnings allowed)
    1  lifecycle violation
    2  harness/setup error (unreadable file, bad git ref, etc.)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from resolver.loader import (  # noqa: E402
    FRONTMATTER_RE,
    LoaderError,
    StringDateLoader,
    load_retro_frontmatter,
)

FATAL = {"error"}


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    retro_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {"check": self.check, "severity": self.severity, "message": self.message}
        if self.retro_id is not None:
            out["retro_id"] = self.retro_id
        return out


@dataclass
class LifecycleResult:
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(f.severity in FATAL for f in self.findings)


def check_pending_orphans(
    retros: list[dict[str, Any]],
    today: date,
    grace: set[str],
    max_pending_days: int = 7,
) -> list[Finding]:
    """SPEC §3 orphan timeout. Graced ids report as warnings so the waiver
    stays visible in CI output instead of silently swallowing the overdue."""
    findings: list[Finding] = []
    for r in retros:
        if r.get("status") != "pending":
            continue
        rid = str(r.get("id", "?"))
        raw_date = str(r.get("date", ""))
        try:
            filed = date.fromisoformat(raw_date)
        except ValueError:
            findings.append(
                Finding(
                    check="pending_orphan",
                    severity="error",
                    message=f"unparseable date {raw_date!r}",
                    retro_id=rid,
                )
            )
            continue
        age = (today - filed).days
        if age <= max_pending_days:
            continue
        if rid in grace:
            findings.append(
                Finding(
                    check="pending_orphan",
                    severity="warning",
                    message=(
                        f"pending {age} days (limit {max_pending_days}); "
                        f"graced by explicit waiver in workflow"
                    ),
                    retro_id=rid,
                )
            )
        else:
            findings.append(
                Finding(
                    check="pending_orphan",
                    severity="error",
                    message=(
                        f"pending {age} days without transition "
                        f"(limit {max_pending_days}); SPEC §3 blocks this PR"
                    ),
                    retro_id=rid,
                )
            )
    return findings


def check_applied_transitions(
    head_retros: list[dict[str, Any]],
    base_statuses: dict[str, str],
    changed_yaml_contents: dict[str, str],
) -> list[Finding]:
    """SPEC §3 applied-transition check.

    `base_statuses` maps retro id -> status at the diff base (absent means the
    retro is new in this PR). `changed_yaml_contents` maps changed YAML paths
    -> their HEAD content. A retro newly `applied` in this diff must have each
    affected rule id present in at least one changed YAML file.
    """
    findings: list[Finding] = []
    for r in head_retros:
        if r.get("status") != "applied":
            continue
        rid = str(r.get("id", "?"))
        if base_statuses.get(rid) == "applied":
            continue  # not a transition in this diff
        for rule_id in r.get("affected_rules") or []:
            if not any(rule_id in text for text in changed_yaml_contents.values()):
                findings.append(
                    Finding(
                        check="applied_transition",
                        severity="error",
                        message=(
                            f"transition to applied does not touch "
                            f"affected rule {rule_id!r}: no changed YAML file "
                            f"in this diff contains it"
                        ),
                        retro_id=rid,
                    )
                )
    return findings


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, cwd=REPO_ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def _base_statuses(diff_base: str, retros_dir: Path) -> dict[str, str]:
    """Retro id -> status at the base ref, parsed from `git show`."""
    rel = retros_dir.relative_to(REPO_ROOT)
    listing = _git(["ls-tree", "--name-only", diff_base, f"{rel}/"])
    statuses: dict[str, str] = {}
    for line in listing.splitlines():
        if not line.endswith(".md") or line.endswith("README.md"):
            continue
        text = _git(["show", f"{diff_base}:{line}"])
        match = FRONTMATTER_RE.match(text)
        if not match:
            continue
        data = yaml.load(match.group(1), Loader=StringDateLoader)
        if isinstance(data, dict) and "id" in data:
            statuses[str(data["id"])] = str(data.get("status", ""))
    return statuses


def _changed_yaml_contents(diff_base: str) -> dict[str, str]:
    """Changed-vs-base YAML paths -> HEAD content (deleted files excluded)."""
    names = _git(["diff", "--name-only", "--diff-filter=d", f"{diff_base}...HEAD"])
    out: dict[str, str] = {}
    for name in names.splitlines():
        if not (name.endswith(".yaml") or name.endswith(".yml")):
            continue
        path = REPO_ROOT / name
        if path.exists():
            out[name] = path.read_text(encoding="utf-8")
    return out


def load_retros(retros_dir: Path) -> list[dict[str, Any]]:
    retros: list[dict[str, Any]] = []
    for path in sorted(retros_dir.iterdir()):
        if path.suffix != ".md" or path.name == "README.md":
            continue
        retros.append(load_retro_frontmatter(path))
    return retros


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retros-dir", default=str(REPO_ROOT / "retrospectives"))
    parser.add_argument("--today", default=None, help="ISO date; defaults to today")
    parser.add_argument("--max-pending-days", type=int, default=7)
    parser.add_argument(
        "--grace",
        action="append",
        default=[],
        metavar="RETRO_ID",
        help="downgrade this retro's orphan timeout to a warning (repeatable)",
    )
    parser.add_argument(
        "--diff-base",
        default=None,
        metavar="REF",
        help="git ref to diff against for the applied-transition check",
    )
    args = parser.parse_args(argv)

    retros_dir = Path(args.retros_dir).resolve()
    if not retros_dir.is_dir():
        print(f"setup: retros dir not found: {retros_dir}", file=sys.stderr)
        return 2
    try:
        retros = load_retros(retros_dir)
    except LoaderError as exc:
        print(f"setup: {exc}", file=sys.stderr)
        return 2

    today = date.fromisoformat(args.today) if args.today else date.today()
    result = LifecycleResult()
    result.findings.extend(
        check_pending_orphans(retros, today, set(args.grace), args.max_pending_days)
    )

    if args.diff_base:
        try:
            base_statuses = _base_statuses(args.diff_base, retros_dir)
            changed = _changed_yaml_contents(args.diff_base)
        except RuntimeError as exc:
            print(f"setup: {exc}", file=sys.stderr)
            return 2
        result.findings.extend(
            check_applied_transitions(retros, base_statuses, changed)
        )

    for f in result.findings:
        stream = sys.stderr if f.severity in FATAL else sys.stdout
        print(f"{f.severity}: [{f.check}] {f.retro_id}: {f.message}", file=stream)
    if result.ok:
        n = len(retros)
        print(f"retro lifecycle: ok ({n} retro{'s' if n != 1 else ''} checked)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
