"""Inheritance chain resolution. SPEC.md §2.3 step 2.

Only `rules.yaml` participates in inheritance. `register.yaml` and
`glossary.yaml` are per-locale leaf files: load + validate, do not merge.

Chain shape: child first, root last. de_AT → de → base.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class InheritanceError(Exception):
    """Cycle, missing parent, or malformed inherits field."""


@dataclass(frozen=True)
class ChainNode:
    """One step in an inheritance chain."""

    locale: str  # "base" for the universal root
    path: Path
    data: dict[str, Any]


def _coerce_inherits(raw: Any, source: Path) -> list[str]:
    """`inherits:` may be a single string or a list. Normalise to a list."""
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list) and all(isinstance(x, str) for x in raw):
        return list(raw)
    raise InheritanceError(
        f"{source}: 'inherits' must be a string or list of strings, got {type(raw).__name__}"
    )


def _parent_locale_from_id(rule_id: str) -> str:
    """Extract locale from a `rules.<locale>` id. Used only for error messages."""
    parts = rule_id.split(".")
    return parts[1] if len(parts) >= 2 else rule_id


def _id_to_path(rule_id: str, locales_dir: Path, base_path: Path) -> Path:
    """Map an `inherits` value (e.g. 'rules.de' or 'base') to a YAML file path."""
    if rule_id == "base":
        return base_path
    if rule_id.startswith("rules."):
        locale = rule_id[len("rules.") :]
        return locales_dir / locale / "rules.yaml"
    raise InheritanceError(
        f"unsupported inherits target {rule_id!r}; expected 'base' or 'rules.<locale>'"
    )


def build_chain(
    locale: str,
    locales_dir: Path,
    base_path: Path,
    loader,
) -> list[ChainNode]:
    """Walk inherits: from `locale` up to `base`. Returns child-first chain.

    `loader` is a callable Path -> dict (typically resolver.loader.load_yaml_file)
    so that the chain builder is decoupled from the loader implementation
    and trivially testable with in-memory fakes.
    """
    chain: list[ChainNode] = []
    seen: dict[
        str, Path
    ] = {}  # locale -> path that introduced it; used for cycle messages

    current_id = f"rules.{locale}"
    current_path = _id_to_path(current_id, locales_dir, base_path)

    while True:
        cur_locale = (
            "base" if current_id == "base" else _parent_locale_from_id(current_id)
        )
        if cur_locale in seen:
            cycle = " -> ".join([n.locale for n in chain] + [cur_locale])
            raise InheritanceError(f"inheritance cycle detected: {cycle}")
        if not current_path.exists():
            raise InheritanceError(
                f"inherits target not found: {current_id!r} expected at {current_path}"
            )
        data = loader(current_path)
        if not isinstance(data, dict):
            raise InheritanceError(f"{current_path}: expected mapping at top level")
        chain.append(ChainNode(locale=cur_locale, path=current_path, data=data))
        seen[cur_locale] = current_path

        if cur_locale == "base":
            break

        inherits_raw = data.get("inherits")
        parents = _coerce_inherits(inherits_raw, current_path)
        if not parents:
            # No parent declared and we are not base — implicit root is base.yaml.
            current_id = "base"
            current_path = base_path
            continue
        if len(parents) > 1:
            raise InheritanceError(
                f"{current_path}: multi-parent inheritance not supported in P1-2 (got {parents})"
            )
        current_id = parents[0]
        current_path = _id_to_path(current_id, locales_dir, base_path)

    return chain
