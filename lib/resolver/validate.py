"""Schema validation. SPEC.md §2.3 step 1.

Each YAML file kind maps to exactly one schema. The mapping is centralised
here so the CLI and any future bin/validate share it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SCHEMA_NAMES = ("base", "rules", "register", "glossary", "baselines", "retrospective")


class ValidationFailed(Exception):
    """Raised when a YAML/frontmatter document fails schema validation."""

    def __init__(self, path: Path, errors: list[ValidationError]) -> None:
        self.path = path
        self.errors = errors
        super().__init__(self._render())

    def _render(self) -> str:
        lines = [f"{self.path}: schema validation failed ({len(self.errors)} error(s))"]
        for err in self.errors[:10]:
            loc = (
                "/" + "/".join(str(p) for p in err.absolute_path)
                if err.absolute_path
                else "/"
            )
            lines.append(f"  {loc}: {err.message}")
        if len(self.errors) > 10:
            lines.append(f"  ... and {len(self.errors) - 10} more")
        return "\n".join(lines)


class SchemaBundle:
    """Schema registry + per-name lookup of raw schema bodies for validator construction."""

    def __init__(self, schema_dir: Path) -> None:
        self.schema_dir = schema_dir
        self._schemas: dict[str, dict[str, Any]] = {}
        self.registry = self._build()

    def _build(self) -> Registry:
        resources: list[tuple[str, Resource]] = []
        for name in SCHEMA_NAMES:
            path = self.schema_dir / f"{name}.schema.json"
            if not path.exists():
                raise FileNotFoundError(f"schema missing: {path}")
            with path.open() as fh:
                schema = json.load(fh)
            self._schemas[name] = schema
            resource = Resource(contents=schema, specification=DRAFT202012)
            if "$id" in schema:
                resources.append((schema["$id"], resource))
            resources.append((f"{name}.schema.json", resource))
        return Registry().with_resources(resources)

    def validator_for(self, schema_name: str) -> Draft202012Validator:
        if schema_name not in self._schemas:
            raise KeyError(f"unknown schema: {schema_name}")
        return Draft202012Validator(self._schemas[schema_name], registry=self.registry)


def build_registry(schema_dir: Path) -> SchemaBundle:
    """Load every schema/*.schema.json into a SchemaBundle (registry + lookup)."""
    return SchemaBundle(schema_dir)


def validate_file(
    path: Path, data: Any, schema_name: str, bundle: SchemaBundle
) -> None:
    """Validate `data` against the named schema. Raises ValidationFailed on error."""
    validator = bundle.validator_for(schema_name)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        raise ValidationFailed(path, errors)


def schema_for_filename(filename: str) -> str | None:
    """Return the schema name that governs a given filename, or None.

    Naming convention: `<kind>.yaml` ⇒ `<kind>` schema. Retrospective .md
    files are handled separately by the caller (frontmatter extraction).
    """
    stem = Path(filename).stem
    return stem if stem in SCHEMA_NAMES else None
