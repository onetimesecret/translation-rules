"""Tree merging with per-key provenance. SPEC.md §2.3 step 3.

Rules:
- maps: deep-merged (child keys win, parent keys preserved otherwise)
- scalars: child replaces parent
- lists: governed by `merge_strategy` (append | replace | prepend | dedup);
  default is `replace`. The strategy is taken from the most child-specific
  document that declares one; per-field overrides are deferred to P1-3+.

Provenance is a flat dict keyed by JSONPath-style strings (e.g. `/rules/0/id`)
mapping to the path of the file that contributed the leaf value. It is
returned alongside the merged tree, NOT inlined into it — keeping the merged
output a clean schema-compatible document for downstream emit.
"""

from __future__ import annotations

from typing import Any

from resolver.inheritance import ChainNode

DEFAULT_LIST_STRATEGY = "replace"
VALID_LIST_STRATEGIES = ("append", "replace", "prepend", "dedup")


class MergeError(Exception):
    """Raised on incompatible merge (e.g. type mismatch between layers)."""


def _merge_lists(parent: list, child: list, strategy: str) -> list:
    if strategy == "replace":
        return _copy_list(child)
    if strategy == "append":
        return _copy_list(parent) + _copy_list(child)
    if strategy == "prepend":
        return _copy_list(child) + _copy_list(parent)
    if strategy == "dedup":
        seen: set = set()
        out: list = []
        for item in _copy_list(parent) + _copy_list(child):
            try:
                key = item if isinstance(item, (str, int, float, bool, type(None))) else repr(item)
            except Exception:
                key = repr(item)
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
        return out
    raise MergeError(f"unknown merge strategy: {strategy!r}; valid: {VALID_LIST_STRATEGIES}")


def _stamp_subtree(value: Any, provenance: dict[str, str], cursor: str, source: str) -> None:
    """Stamp every leaf path under `value` with `source`."""
    if isinstance(value, dict):
        if not value:
            provenance[cursor or "/"] = source
            return
        for key, sub in value.items():
            _stamp_subtree(sub, provenance, f"{cursor}/{key}", source)
    elif isinstance(value, list):
        provenance[cursor or "/"] = source
        for i, sub in enumerate(value):
            _stamp_subtree(sub, provenance, f"{cursor}/{i}", source)
    else:
        provenance[cursor or "/"] = source


def _merge_pair(
    parent: Any,
    child: Any,
    child_source: str,
    strategy: str,
    provenance: dict[str, str],
    cursor: str,
) -> Any:
    """Merge child into parent. Provenance is updated in place.

    - parent: a value already in the accumulator (provenance already populated)
    - child: a value from the next layer being folded in
    - child_source: file path string for stamping new/replaced provenance
    """
    # Both maps: deep-merge.
    if isinstance(parent, dict) and isinstance(child, dict):
        out: dict[str, Any] = {}
        # Preserve parent-only keys; their provenance is already set.
        for key, p_val in parent.items():
            if key not in child:
                out[key] = p_val
        # Merge or stamp child keys.
        for key, c_val in child.items():
            sub_cursor = f"{cursor}/{key}"
            if key in parent:
                out[key] = _merge_pair(parent[key], c_val, child_source, strategy, provenance, sub_cursor)
            else:
                out[key] = _copy_value(c_val)
                _stamp_subtree(c_val, provenance, sub_cursor, child_source)
        return out

    # Both lists: strategy-driven.
    if isinstance(parent, list) and isinstance(child, list):
        merged = _merge_lists(parent, child, strategy)
        # Lists are opaque under merge; stamp the list and its elements with
        # the child as latest contributor. Element-level multi-source provenance
        # is a P1-3 enhancement if needed.
        _stamp_subtree(merged, provenance, cursor, child_source)
        return merged

    # Container/scalar mismatch: hard error to surface authoring bugs.
    if isinstance(parent, (dict, list)) or isinstance(child, (dict, list)):
        # Special case: parent missing (None) is permitted — child wins cleanly.
        if parent is None:
            _stamp_subtree(child, provenance, cursor, child_source)
            return _copy_value(child)
        raise MergeError(
            f"type mismatch at {cursor or '/'}: parent={type(parent).__name__} "
            f"vs child={type(child).__name__} (source: {child_source})"
        )

    # Scalars: child wins.
    provenance[cursor or "/"] = child_source
    return child


def merge_chain(chain: list[ChainNode]) -> tuple[dict[str, Any], dict[str, str]]:
    """Merge a chain produced by build_chain. Returns (merged_tree, provenance).

    Chain order is child-first (de_AT, de, base). We fold from base down to
    child so child values win on conflict.
    """
    if not chain:
        raise MergeError("cannot merge empty chain")

    # Strategy: most-specific declaration wins. Walk child-first; first one
    # with `merge_strategy:` set is authoritative for the whole document.
    strategy = DEFAULT_LIST_STRATEGY
    for node in chain:
        raw = node.data.get("merge_strategy")
        if isinstance(raw, str):
            strategy = raw
            break
    if strategy not in VALID_LIST_STRATEGIES:
        raise MergeError(f"invalid merge_strategy {strategy!r}; valid: {VALID_LIST_STRATEGIES}")

    # Initialise from root (base).
    root = chain[-1]
    merged: dict[str, Any] = _copy_value(root.data)
    provenance: dict[str, str] = {}
    _stamp_subtree(root.data, provenance, "", str(root.path))

    # Fold parents -> child.
    for node in reversed(chain[:-1]):
        merged = _merge_pair(
            merged,
            node.data,
            child_source=str(node.path),
            strategy=strategy,
            provenance=provenance,
            cursor="",
        )

    if not isinstance(merged, dict):
        raise MergeError("merge produced a non-mapping at the top level")

    return merged, provenance


def _copy_value(v: Any) -> Any:
    if isinstance(v, dict):
        return {k: _copy_value(sub) for k, sub in v.items()}
    if isinstance(v, list):
        return [_copy_value(sub) for sub in v]
    return v


def _copy_list(v: list) -> list:
    return [_copy_value(sub) for sub in v]
