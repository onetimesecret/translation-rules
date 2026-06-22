#!/usr/bin/env python3
"""Central baselines pass for backfilled locales.

For each locale in LOCALES it:
  1. appends a `baselines.<locale>` backfill-pin entry to baselines.yaml
     (form/pronoun + a couple glossary invariants, justification_doc, the
     AGENT-AUTHORED/pending-sign-off note, pinned to the current branch tip);
  2. restores `baseline_ref: baselines.<locale>` in the locale's register.yaml
     and rules.yaml, removing the "deferred" comment the authoring agent left.

Agents could not do this themselves: baselines.yaml is a single shared file, and
a `baseline_ref` to a missing entry dangles and fails the resolver — so it had to
be a serialized central pass. Idempotent: skips a locale already in baselines.yaml.

Usage (from the translation-rules repo root):
  uv run locales/scripts/backfill-baselines.py nl es pl
  uv run locales/scripts/backfill-baselines.py --rest   # every governed locale missing an entry

Verify after:  uv run resolver/resolve.py <L> --lint --validate-only
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]  # repo root (…/translation-rules)
BASELINES = ROOT / "baselines.yaml"
PINNED_ON = "2026-06-22"

# Locales whose register/glossary are NOT their own backfill source (family
# parents already pinned, or variants that inherit). Still get an entry, but the
# note is generic. Everything else points at the app translator guide.
GUIDE = "onetimesecret/locales/guides/for-translators/{L}.md"


def head_sha() -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()


def first_target(loc_block):
    """Pull a representative target string from a glossary term's locale block."""
    if not isinstance(loc_block, dict):
        return None
    for _sense, v in loc_block.items():
        if isinstance(v, dict) and v.get("target"):
            return v["target"]
        if isinstance(v, str):
            return v
    return None


def invariants_for(locale: str) -> list[str]:
    reg = yaml.safe_load((ROOT / "locales" / locale / "register.yaml").read_text())
    inv = [f"register.form={reg.get('form')} ({reg.get('pronoun')})"]
    glo_path = ROOT / "locales" / locale / "glossary.yaml"
    glo = yaml.safe_load(glo_path.read_text()) if glo_path.exists() else {}
    for term in (glo.get("terms") or [])[:2]:
        key = term.get("key")
        tgt = first_target(term.get(locale))
        if key and tgt:
            inv.append(f"glossary.{key}={tgt}")
    return inv


def baselines_block(locale: str, sha: str) -> str:
    inv = invariants_for(locale)
    inv_yaml = "\n".join(f"      - {line}" for line in inv)
    return (
        f"  {locale}:\n"
        f"    commit: {sha}\n"
        f"    pinned_on: {PINNED_ON}\n"
        f"    invariants:\n"
        f"{inv_yaml}\n"
        f"    justification_doc: {GUIDE.format(L=locale)}\n"
        f'    note: "Backfill pin for the {locale} structured-rules layer. No retro '
        f"exists; source of truth is the app-repo translator guide. AGENT-AUTHORED "
        f"content pending native-speaker sign-off. Commit is the branch tip at "
        f'authoring time, not a curated content commit."\n'
    )


def existing_keys() -> set[str]:
    doc = yaml.safe_load(BASELINES.read_text())
    return set((doc.get("baselines") or {}).keys())


def restore_baseline_ref(locale: str) -> None:
    """Drop the agent's 'baseline_ref deferred' comment lines and add the key."""
    for fn in ("register.yaml", "rules.yaml"):
        p = ROOT / "locales" / locale / fn
        lines = p.read_text().splitlines()
        kept = [
            ln
            for ln in lines
            if not (ln.lstrip().startswith("#") and "baseline" in ln.lower())
        ]
        if not any(ln.startswith("baseline_ref:") for ln in kept):
            while kept and kept[-1].strip() == "":
                kept.pop()
            kept.append(f"baseline_ref: baselines.{locale}")
        p.write_text("\n".join(kept) + "\n")


def main(argv: list[str]) -> int:
    have = existing_keys()
    if argv == ["--rest"]:
        governed = sorted(
            d.name
            for d in (ROOT / "locales").iterdir()
            if (d / "register.yaml").exists()
        )
        locales = [L for L in governed if L not in have]
    else:
        locales = argv
    if not locales:
        print("nothing to do")
        return 0

    sha = head_sha()
    blocks = []
    for L in locales:
        if L in have:
            print(f"skip {L}: already in baselines.yaml")
            continue
        if not (ROOT / "locales" / L / "register.yaml").exists():
            print(f"skip {L}: not governed")
            continue
        blocks.append(baselines_block(L, sha))
        restore_baseline_ref(L)
        print(f"added baselines.{L} + restored baseline_ref")

    if blocks:
        text = BASELINES.read_text()
        if not text.endswith("\n"):
            text += "\n"
        BASELINES.write_text(text + "".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
