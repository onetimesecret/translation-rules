#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6,<7",
# ]
# ///
"""Review findings-manifest gate. SPEC.md §3.

Every new review document must end with a findings manifest — a bulleted
list where each item maps to a retrospective id or `wont_fix` tag with
reasoning (SPEC §3: "CI checks: for each review doc, every finding has a
tracking tag"). CI cannot extract findings from prose; the manifest is the
machine-checkable proxy: it must exist, be well-formed, and its tags must
resolve. This prevents the "insights die in prose" failure that produced
the pre-2026 unactioned review backlog.

Manifest contract (strict, so it stays machine-checkable):

  1. The document's LAST `##`-level heading is exactly `## Findings manifest`.
  2. After it: only top-level `- ` bullets, indented continuation lines of a
     bullet, and blank lines. Anything else is stray content.
  3. Every bullet carries `retro: <id>` where <id> is an existing
     retrospective id (frontmatter of `retrospectives/*.md`, including
     `_archive/` — superseded retros are still valid tags), or `wont_fix:`
     followed by non-empty reasoning text.
  4. A review with zero findings uses the single literal bullet `- none`.

Documents predating the gate are grandfathered (SPEC §3: "Existing `reviews/`
directories remain as-is ... no backfill into retrospective format") — see
GRANDFATHERED below. `README.md` files are directory indexes, not review
documents, and are exempt at any depth.

Usage:
    resolver/review_manifest.py [--reviews-dir reviews]
                                [--retros-dir retrospectives]

Exit codes:
    0  all checks passed (warnings allowed)
    1  manifest violation
    2  harness/setup error (missing directory, unreadable retro, etc.)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from resolver.loader import (  # noqa: E402
    LoaderError,
    load_retro_frontmatter,
)

FATAL = {"error"}

MANIFEST_HEADING = "## Findings manifest"

# SPEC §3 grandfather clause: "Existing `reviews/` directories remain as-is.
# Historical QA reviews are preserved as raw input; no backfill into
# retrospective format." This is the exact reviews/ inventory at the time the
# gate landed (2026-06-12), frozen by path rather than by a date cutoff: a
# document added later into an old dated directory is still a NEW review
# document. Do NOT add paths to this set — new review docs carry manifests.
GRANDFATHERED = frozenset(
    {
        "2025-11-14/polish-translation-review.md",
        "2025-11-14/pt-br-locale-analysis.md",
        "2025-11-14/turkish-locale-analysis.md",
        "2025-11-14/ukrainian-translation-review.md",
        "2025-11-14/zh-cn-translation-review.md",
        "2025-11-16/locale-quality-analysis-bg.md",
        "2025-11-16/locale-quality-analysis-da.md",
        "2025-11-16/locale-quality-analysis-de.md",
        "2025-11-16/locale-quality-analysis-es.md",
        "2025-11-16/locale-quality-analysis-fr.md",
        "2025-11-16/locale-quality-analysis-it.md",
        "2025-11-16/locale-quality-analysis-ja.md",
        "2025-11-16/locale-quality-analysis-ko.md",
        "2025-11-16/locale-quality-analysis-mi.md",
        "2025-11-16/locale-quality-analysis-nl.md",
        "2025-11-16/locale-quality-analysis-pl.md",
        "2025-11-16/locale-quality-analysis-pt-br.md",
        "2025-11-16/locale-quality-analysis-sv.md",
        "2025-11-16/locale-quality-analysis-tr.md",
        "2025-11-16/locale-quality-analysis-uk.md",
        "2025-11-16/locale-quality-analysis-zh-cn.md",
        "2026-04-12/README.md",
        "2026-04-12/advice-for-saas-translator-skill.md",
        "2026-04-12/criteria.md",
        "2026-04-12/cross-locale-audit.md",
        "2026-04-12/guide-repair-report.md",
        "2026-04-12/locale-quality-analysis-de_AT.md",
        "2026-04-12/proposed-new-structure-addendum.md",
        "2026-04-12/proposed-new-structure.md",
        "2026-04-12/qa-validation.md",
    }
)

# Retro ids are `YYYY-MM-DD-<slug>` (word chars + hyphens), so the capture
# stops cleanly before trailing prose punctuation.
RETRO_TAG_RE = re.compile(r"retro:\s*([\w-]+)")
WONT_FIX_TAG_RE = re.compile(r"wont_fix:\s*(.*)", re.DOTALL)


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    doc: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {"check": self.check, "severity": self.severity, "message": self.message}
        if self.doc is not None:
            out["doc"] = self.doc
        return out


def is_exempt(rel_path: Path) -> bool:
    """True if this reviews-dir-relative path is not held to the manifest
    contract: README.md files are directory indexes, not review documents;
    grandfathered paths predate the gate (SPEC §3 "remain as-is")."""
    if rel_path.name == "README.md":
        return True
    return rel_path.as_posix() in GRANDFATHERED


def check_manifest(
    doc_text: str,
    known_retro_ids: set[str],
    doc: str | None = None,
) -> list[Finding]:
    """SPEC §3 manifest contract over a single review document's text.

    Parsing is line-based and deliberately naive: a `## ` line is a heading
    wherever it appears. Keeping the manifest the literal tail of the file
    (no trailing sections, no fenced blocks after it) is part of the
    contract, not a parser limitation to engineer around.
    """
    lines = doc_text.splitlines()
    h2s = [(i, ln.rstrip()) for i, ln in enumerate(lines) if ln.startswith("## ")]
    if not any(text == MANIFEST_HEADING for _, text in h2s):
        return [
            Finding(
                check="missing_manifest",
                severity="error",
                message=(
                    f"no `{MANIFEST_HEADING}` section; every new review "
                    f"document must end with one (SPEC §3)"
                ),
                doc=doc,
            )
        ]
    last_idx, last_text = h2s[-1]
    if last_text != MANIFEST_HEADING:
        return [
            Finding(
                check="manifest_not_last",
                severity="error",
                message=(
                    f"`{MANIFEST_HEADING}` must be the document's last "
                    f"`##` heading; found {last_text!r} after it"
                ),
                doc=doc,
            )
        ]

    findings: list[Finding] = []
    bullets: list[str] = []  # one entry per `- ` bullet, continuations joined
    for lineno, raw in enumerate(lines[last_idx + 1 :], start=last_idx + 2):
        if not raw.strip():
            continue
        if raw.startswith("- "):
            bullets.append(raw[2:].strip())
            continue
        if raw[0] in (" ", "\t") and bullets:
            bullets[-1] += "\n" + raw.strip()
            continue
        findings.append(
            Finding(
                check="stray_content",
                severity="error",
                message=(
                    f"line {lineno}: only `- ` bullets, indented "
                    f"continuations, and blank lines are allowed after the "
                    f"manifest heading: {raw.strip()!r}"
                ),
                doc=doc,
            )
        )

    if not bullets:
        findings.append(
            Finding(
                check="empty_manifest",
                severity="error",
                message=(
                    "manifest has no bullets; a review with zero findings "
                    "uses the single bullet `- none`"
                ),
                doc=doc,
            )
        )
        return findings
    if bullets == ["none"]:
        return findings  # zero-findings sentinel
    for n, text in enumerate(bullets, start=1):
        findings.extend(_check_bullet(n, text, known_retro_ids, doc))
    return findings


def _check_bullet(
    n: int, text: str, known_retro_ids: set[str], doc: str | None
) -> list[Finding]:
    findings: list[Finding] = []
    retro = RETRO_TAG_RE.search(text)
    wont_fix = WONT_FIX_TAG_RE.search(text)
    if not retro and not wont_fix:
        # `- ` with no text yields an empty bullet; splitlines() would be [].
        head = text.splitlines()[0] if text else ""
        if len(head) > 60:
            head = head[:57] + "..."
        findings.append(
            Finding(
                check="untagged_finding",
                severity="error",
                message=(
                    f"bullet {n} has neither `retro: <id>` nor "
                    f"`wont_fix: <reasoning>`: {head!r}"
                ),
                doc=doc,
            )
        )
    if retro and retro.group(1) not in known_retro_ids:
        findings.append(
            Finding(
                check="unknown_retro_id",
                severity="error",
                message=(
                    f"bullet {n} tags unknown retrospective id "
                    f"{retro.group(1)!r}: no such file in retrospectives/"
                ),
                doc=doc,
            )
        )
    if wont_fix and not wont_fix.group(1).strip():
        findings.append(
            Finding(
                check="empty_wont_fix_reason",
                severity="error",
                message=f"bullet {n}: `wont_fix:` requires reasoning text",
                doc=doc,
            )
        )
    return findings


def load_known_retro_ids(retros_dir: Path) -> set[str]:
    """Retro ids from frontmatter, including `_archive/` if present —
    superseded retros are still valid tracking tags."""
    dirs = [retros_dir]
    archive = retros_dir / "_archive"
    if archive.is_dir():
        dirs.append(archive)
    ids: set[str] = set()
    for d in dirs:
        for path in sorted(d.iterdir()):
            if path.suffix != ".md" or path.name == "README.md":
                continue
            data = load_retro_frontmatter(path)
            if "id" in data:
                ids.add(str(data["id"]))
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviews-dir", default=str(REPO_ROOT / "reviews"))
    parser.add_argument("--retros-dir", default=str(REPO_ROOT / "retrospectives"))
    args = parser.parse_args(argv)

    reviews_dir = Path(args.reviews_dir).resolve()
    if not reviews_dir.is_dir():
        print(f"setup: reviews dir not found: {reviews_dir}", file=sys.stderr)
        return 2
    retros_dir = Path(args.retros_dir).resolve()
    if not retros_dir.is_dir():
        print(f"setup: retros dir not found: {retros_dir}", file=sys.stderr)
        return 2
    try:
        known_ids = load_known_retro_ids(retros_dir)
    except LoaderError as exc:
        print(f"setup: {exc}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    checked = exempt = 0
    for path in sorted(reviews_dir.rglob("*.md")):
        rel = path.relative_to(reviews_dir)
        if is_exempt(rel):
            exempt += 1
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        findings.extend(check_manifest(text, known_ids, doc=rel.as_posix()))

    for f in findings:
        stream = sys.stderr if f.severity in FATAL else sys.stdout
        print(f"{f.severity}: [{f.check}] {f.doc}: {f.message}", file=stream)
    if any(f.severity in FATAL for f in findings):
        return 1
    print(f"review manifests: ok ({checked} checked, {exempt} exempt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
