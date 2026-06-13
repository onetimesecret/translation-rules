"""Emit `.resolved/<locale>.json`. SPEC.md §2.3 step 7b.

A pure projection of the assembled model. Stable key order (sort_keys) and
ensure_ascii=False give byte-for-byte determinism while keeping target terms
greppable by human-readable name (SPEC §6.1). The only non-deterministic field,
`_meta.generated_at`, is injected by the caller, so a fixed value yields a
reproducible file for golden tests.

Per Q3 (2026-05-29) the JSON is NOT content-hash-checked the way the markdown
is — the app-repo CI gate checks `_meta.source_commit == submodule SHA` only
(SPEC §2.4). Determinism here exists for the golden test, not a hash gate.
"""

from __future__ import annotations

import json
from typing import Any


def emit_json(model: dict[str, Any]) -> str:
    """Serialize the resolved model to a stable, newline-terminated JSON string."""
    return json.dumps(model, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
