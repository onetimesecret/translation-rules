#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.21,<5",
#   "referencing>=0.32,<1",
#   "pyyaml>=6,<7",
# ]
# ///
"""Schema fixture runner for translation-rules.

Runs JSON Schema validation against per-schema positive and negative fixtures.
Distinguishes "negative didn't fail" (lax schema bug) from "negative failed for the
wrong reason" (silent bug) via an optional `expected_error_path:` sidecar key.

Usage:
    python tests/schema/run.py                       # run all
    python tests/schema/run.py register glossary     # run a subset

Exit codes:
    0  all fixtures behaved as expected
    1  one or more fixtures behaved incorrectly
    2  test harness setup error (missing schema, malformed fixture, etc.)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print(
        "error: PyYAML required (pip install pyyaml or uv run --with pyyaml)",
        file=sys.stderr,
    )
    sys.exit(2)


class StringDateLoader(yaml.SafeLoader):
    """SafeLoader variant that keeps ISO date/datetime values as strings.

    PyYAML's default behavior maps `2026-04-12` to a `datetime.date` object, which
    then fails JSON Schema `type: string` validation. Schemas in this repo want
    raw strings (we run regex-based validation via `isoDate`), so the timestamp
    resolver is disabled here.

    The resolvers dict is deep-copied first so we don't mutate the inherited
    SafeLoader dict (which would silently change yaml.safe_load behavior in any
    other consumer running in the same process).
    """


StringDateLoader.yaml_implicit_resolvers = {
    ch: [
        (tag, regex) for tag, regex in resolvers if tag != "tag:yaml.org,2002:timestamp"
    ]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import ValidationError
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError:
    print(
        "error: jsonschema>=4.18 + referencing required "
        "(pip install jsonschema or uv run --with jsonschema)",
        file=sys.stderr,
    )
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "schema"
FIXTURE_DIR = REPO_ROOT / "tests" / "schema" / "fixtures"

SCHEMA_NAMES = ["base", "rules", "register", "glossary", "baselines", "retrospective"]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def load_schema_registry() -> Registry:
    """Load every schema/*.schema.json into a referencing Registry so $ref resolves."""
    resources: list[tuple[str, Resource]] = []
    for name in SCHEMA_NAMES:
        path = SCHEMA_DIR / f"{name}.schema.json"
        if not path.exists():
            continue
        with path.open() as fh:
            schema = json.load(fh)
        resource = Resource(contents=schema, specification=DRAFT202012)
        # Register both by $id (canonical) and by relative filename (for $ref "base.schema.json#/...").
        if "$id" in schema:
            resources.append((schema["$id"], resource))
        resources.append((f"{name}.schema.json", resource))
    return Registry().with_resources(resources)


def load_fixture(path: Path) -> tuple[Any, dict[str, Any]]:
    """Load a fixture file. Returns (data, sidecar_meta).

    Recognised forms:
      - .yaml / .yml  → parsed as YAML; if a mapping has __meta__, that becomes the sidecar
      - .json         → parsed as JSON; ditto __meta__
      - .md           → frontmatter (YAML between ---/---) is the data; body ignored
    """
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in {".yaml", ".yml"}:
        data = yaml.load(text, Loader=StringDateLoader)
    elif suffix == ".json":
        data = json.loads(text)
    elif suffix == ".md":
        match = FRONTMATTER_RE.match(text)
        if not match:
            raise ValueError(f"{path}: missing YAML frontmatter")
        data = yaml.load(match.group(1), Loader=StringDateLoader)
    else:
        raise ValueError(f"{path}: unsupported fixture suffix {suffix!r}")

    meta: dict[str, Any] = {}
    if isinstance(data, dict) and "__meta__" in data:
        meta = data.pop("__meta__") or {}
    return data, meta


def error_path(err: ValidationError) -> str:
    """Render a ValidationError's path as a slash-joined string for assertion."""
    return (
        "/" + "/".join(str(p) for p in err.absolute_path) if err.absolute_path else "/"
    )


def run_schema(schema_name: str, registry: Registry) -> tuple[int, int]:
    """Run all fixtures under fixtures/<schema_name>/. Returns (passed, failed)."""
    schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"
    if not schema_path.exists():
        print(f"  skip: schema/{schema_name}.schema.json does not exist yet")
        return (0, 0)

    with schema_path.open() as fh:
        schema = json.load(fh)
    validator = Draft202012Validator(schema, registry=registry)

    fixtures_root = FIXTURE_DIR / schema_name
    if not fixtures_root.exists():
        print(f"  skip: tests/schema/fixtures/{schema_name}/ does not exist yet")
        return (0, 0)

    passed = 0
    failed = 0

    for kind in ("positive", "negative"):
        kind_dir = fixtures_root / kind
        if not kind_dir.exists():
            continue
        for fixture_path in sorted(kind_dir.iterdir()):
            if fixture_path.is_dir() or fixture_path.name.startswith("."):
                continue
            try:
                data, meta = load_fixture(fixture_path)
            except Exception as exc:
                print(
                    f"  FAIL {fixture_path.relative_to(REPO_ROOT)}: load error: {exc}"
                )
                failed += 1
                continue

            errors = sorted(
                validator.iter_errors(data), key=lambda e: list(e.absolute_path)
            )
            rel = fixture_path.relative_to(REPO_ROOT)

            if kind == "positive":
                if errors:
                    print(
                        f"  FAIL {rel}: positive fixture should validate, got {len(errors)} errors"
                    )
                    for err in errors[:5]:
                        print(f"        {error_path(err)}: {err.message}")
                    failed += 1
                else:
                    print(f"  pass {rel}")
                    passed += 1
            else:  # negative
                if not errors:
                    print(
                        f"  FAIL {rel}: negative fixture should fail, but validated cleanly"
                    )
                    failed += 1
                    continue

                expected = meta.get("expected_error_path")
                if expected is not None:
                    matched = any(error_path(err) == expected for err in errors)
                    if not matched:
                        actual = ", ".join(error_path(e) for e in errors[:3])
                        print(
                            f"  FAIL {rel}: expected error at {expected!r}, "
                            f"got: {actual}"
                        )
                        failed += 1
                        continue
                print(f"  pass {rel}")
                passed += 1

    return (passed, failed)


def main(argv: list[str]) -> int:
    targets = argv[1:] if len(argv) > 1 else SCHEMA_NAMES
    bad = [t for t in targets if t not in SCHEMA_NAMES]
    if bad:
        print(
            f"error: unknown schema(s): {bad}. Known: {SCHEMA_NAMES}", file=sys.stderr
        )
        return 2

    try:
        registry = load_schema_registry()
    except Exception as exc:
        print(f"error: failed to load schema registry: {exc}", file=sys.stderr)
        return 2

    total_passed = 0
    total_failed = 0
    for name in targets:
        print(f"# {name}")
        p, f = run_schema(name, registry)
        total_passed += p
        total_failed += f

    print()
    print(f"summary: {total_passed} passed, {total_failed} failed")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
