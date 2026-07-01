"""Emit `.resolved/<locale>.json`. SPEC.md §2.3 step 7b.

A pure projection of the assembled model. Stable key order (sort_keys) and
ensure_ascii=False give byte-for-byte determinism while keeping target terms
greppable by human-readable name (SPEC §6.1). The only non-deterministic field,
`_meta.generated_at`, is injected by the caller, so a fixed value yields a
reproducible file for golden tests.

Determinism matters beyond golden tests: under the no-vendor model (ADR-005)
consumers derive this file on demand and CI regenerates it from scratch at the
pin, so byte-stable output is what lets the regenerate-in-CI freshness gate
pass. There is no committed copy and no content-hash / `source_commit ==
submodule-SHA` gate — both retired with the vendored corpus (ADR-005).
"""

from __future__ import annotations

import json
from typing import Any


def emit_json(model: dict[str, Any]) -> str:
    """Serialize the resolved model to a stable, newline-terminated JSON string."""
    return json.dumps(model, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
