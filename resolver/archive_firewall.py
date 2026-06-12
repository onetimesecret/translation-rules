#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Archive firewall gate. SPEC.md §2.1.

Top-level `_archive/` is the prescriptive-vs-descriptive firewall — anything
inside is never compiled into resolver output — and `retrospectives/_archive/`
holds superseded retros. SPEC §2.1: "Moving a file out of `_archive/` is a
reviewable diff requiring explicit label approval."

One CI-enforced check:

  archive promotion — a rename or copy whose source is inside an archive tree
  and whose destination is outside any archive tree, or a deletion inside an
  archive tree, requires the `prescriptive-promotion` label on the PR. A
  deletion is gated because it is indistinguishable from the first half of a
  move that rename detection missed — the label is the escape hatch either
  way. When the label is present, gated changes report as non-fatal warnings
  so the promotion stays visible in CI output (the same pattern as graced
  orphans in retro_lifecycle.py). Adds into an archive, edits in place, and
  renames within or between the two archive trees pass silently.

Changes are read from `git diff --name-status -z -M -C <merge-base> HEAD`.
The NUL-separated `-z` form is parsed so filenames containing tabs or
newlines cannot break record boundaries.

Labels arrive via repeatable `--label` (local runs) or via `--labels-env`,
naming an environment variable that holds a JSON array of label names — the
CI path, which avoids shell-interpolating attacker-controlled label text
into a command line.

Usage:
    resolver/archive_firewall.py --diff-base <ref>
                                 [--label NAME]...
                                 [--labels-env VARNAME]

Exit codes:
    0  no unapproved promotions (warnings allowed)
    1  firewall violation
    2  harness/setup error (bad git ref, malformed diff or labels, etc.)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

PROMOTION_LABEL = "prescriptive-promotion"

# Exactly the two trees SPEC §2.1 names: the top-level firewall and the
# superseded-retros archive. Prefix lookalikes (`_archived/x`, `foo/_archive/x`)
# are NOT gated.
ARCHIVE_TREES = ("_archive/", "retrospectives/_archive/")

FATAL = {"error"}

# (status, src, dst) as parsed from `--name-status -z`; dst is None except
# for rename/copy records.
Record = tuple[str, str, str | None]


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {"check": self.check, "severity": self.severity, "message": self.message}
        if self.path is not None:
            out["path"] = self.path
        return out


@dataclass
class FirewallResult:
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(f.severity in FATAL for f in self.findings)


def in_archive(path: str) -> bool:
    return path.startswith(ARCHIVE_TREES)


def check_archive_moves(records: list[Record], labels: set[str]) -> list[Finding]:
    """SPEC §2.1 promotion check over parsed diff records.

    With the promotion label present, findings downgrade to warnings: the
    promotion stays visible in CI output instead of passing silently.
    """
    approved = PROMOTION_LABEL in labels
    severity = "warning" if approved else "error"
    suffix = (
        f"approved by the {PROMOTION_LABEL!r} label"
        if approved
        else f"requires the {PROMOTION_LABEL!r} label on the PR (SPEC §2.1)"
    )
    findings: list[Finding] = []
    for status, src, dst in records:
        kind = status[:1]
        if kind in {"R", "C"} and dst is not None:
            if in_archive(src) and not in_archive(dst):
                verb = "renamed" if kind == "R" else "copied"
                findings.append(
                    Finding(
                        check="archive_promotion",
                        severity=severity,
                        message=f"{verb} out of the archive to {dst!r}; {suffix}",
                        path=src,
                    )
                )
        elif kind == "D" and in_archive(src):
            findings.append(
                Finding(
                    check="archive_promotion",
                    severity=severity,
                    message=f"deleted from the archive; {suffix}",
                    path=src,
                )
            )
    return findings


def parse_name_status(raw: str) -> list[Record]:
    """Parse `git diff --name-status -z` output into (status, src, dst).

    The -z stream is NUL-separated fields: STATUS, PATH for most records;
    STATUS, SRC, DST for renames and copies (the status carries a similarity
    score, e.g. R100). NUL cannot appear in a filename, so names containing
    tabs or newlines cannot break record boundaries the way the default
    tab/newline-separated form can.
    """
    fields = raw.split("\0")
    # A non-empty stream is NUL-terminated, leaving one trailing empty field.
    if fields and fields[-1] == "":
        fields.pop()
    records: list[Record] = []
    i = 0
    while i < len(fields):
        status = fields[i]
        width = 3 if status[:1] in {"R", "C"} else 2
        if i + width > len(fields):
            raise ValueError(f"truncated diff record at field {i}: status {status!r}")
        if width == 3:
            records.append((status, fields[i + 1], fields[i + 2]))
        else:
            records.append((status, fields[i + 1], None))
        i += width
    return records


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, cwd=REPO_ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def _merge_base(diff_base: str) -> str:
    """Same comparison point as retro_lifecycle.py: the merge base keeps the
    diff stable when the base branch has moved since this branch diverged."""
    return _git(["merge-base", diff_base, "HEAD"]).strip()


def _diff_records(base_commit: str) -> list[Record]:
    """Changed-vs-base records with rename (-M) and copy (-C) detection on,
    so promotions surface as R/C records instead of delete+add pairs."""
    raw = _git(["diff", "--name-status", "-z", "-M", "-C", base_commit, "HEAD"])
    return parse_name_status(raw)


def _load_labels(label_args: list[str], labels_env: str | None) -> set[str]:
    labels = set(label_args)
    if labels_env is not None:
        raw = os.environ.get(labels_env)
        if raw is None:
            raise RuntimeError(
                f"--labels-env: environment variable {labels_env!r} is not set"
            )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"--labels-env: {labels_env} is not valid JSON: {exc}"
            ) from exc
        if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
            raise RuntimeError(
                f"--labels-env: {labels_env} must be a JSON array of strings"
            )
        labels.update(parsed)
    return labels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--diff-base",
        required=True,
        metavar="REF",
        help="git ref to diff against (the merge base with HEAD is used)",
    )
    parser.add_argument(
        "--label",
        action="append",
        default=[],
        metavar="NAME",
        help="treat this PR label as present (repeatable; for local runs)",
    )
    parser.add_argument(
        "--labels-env",
        default=None,
        metavar="VARNAME",
        help="environment variable holding a JSON array of PR label names",
    )
    args = parser.parse_args(argv)

    try:
        labels = _load_labels(args.label, args.labels_env)
        base_commit = _merge_base(args.diff_base)
        records = _diff_records(base_commit)
    except (RuntimeError, ValueError) as exc:
        print(f"setup: {exc}", file=sys.stderr)
        return 2

    result = FirewallResult(findings=check_archive_moves(records, labels))
    for f in result.findings:
        stream = sys.stderr if f.severity in FATAL else sys.stdout
        print(f"{f.severity}: [{f.check}] {f.path}: {f.message}", file=stream)
    if result.ok:
        n = len(records)
        print(f"archive firewall: ok ({n} record{'s' if n != 1 else ''} checked)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
