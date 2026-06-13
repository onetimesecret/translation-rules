"""ID minting and lookup. SPEC.md §4.

Stable ID format: `<kind>.<key>#<8hex>`. The 8-char suffix survives renames
and file moves; the kind+key is the grep target. The resolver is the sole
writer of `lib/resolver/index.json`. `bin/mint-id` is read-only against the
index — it computes a deterministic suffix and verifies (or refuses) based
on whether `<kind>.<key>` is already registered.

Determinism: `sha256(f"{kind}.{key}").hexdigest()[:8]`. If the deterministic
suffix collides with a different `(kind, key)` already in the index, a salt
is appended and re-hashed until unique. Re-minting an existing `(kind, key)`
is a no-op (returns the registered id) so the operation is idempotent.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

ID_RE = re.compile(r"^([a-z][a-z0-9_-]*)\.([a-z][a-zA-Z0-9_-]*)#([0-9a-f]{8})$")
KIND_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
KEY_RE = re.compile(r"^[a-z][a-zA-Z0-9_-]*$")


class IdError(Exception):
    """Raised when an id is malformed, unresolvable, or collides irreconcilably."""


@dataclass
class IdRecord:
    """One entry in lib/resolver/index.json."""

    id: str
    kind: str
    key: str
    file: str  # repo-relative path
    json_pointer: str  # JSONPath-style cursor inside the file

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "kind": self.kind,
            "key": self.key,
            "file": self.file,
            "json_pointer": self.json_pointer,
        }


@dataclass
class IdIndex:
    """In-memory id index. Persists as lib/resolver/index.json (sorted by id)."""

    by_id: dict[str, IdRecord] = field(default_factory=dict)
    by_kind_key: dict[tuple[str, str], IdRecord] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "IdIndex":
        idx = cls()
        if not path.exists():
            return idx
        with path.open() as fh:
            payload = json.load(fh)
        for entry in payload.get("ids", []):
            rec = IdRecord(
                id=entry["id"],
                kind=entry["kind"],
                key=entry["key"],
                file=entry.get("file", ""),
                json_pointer=entry.get("json_pointer", ""),
            )
            idx.add(rec)
        return idx

    def add(self, rec: IdRecord) -> None:
        if rec.id in self.by_id:
            existing = self.by_id[rec.id]
            if (existing.kind, existing.key) != (rec.kind, rec.key):
                raise IdError(
                    f"id collision: {rec.id} maps to {(existing.kind, existing.key)} "
                    f"and {(rec.kind, rec.key)}"
                )
        self.by_id[rec.id] = rec
        self.by_kind_key[(rec.kind, rec.key)] = rec

    def lookup_id(self, id_: str) -> IdRecord | None:
        return self.by_id.get(id_)

    def lookup_kind_key(self, kind: str, key: str) -> IdRecord | None:
        return self.by_kind_key.get((kind, key))

    def dump(self, path: Path) -> None:
        payload: dict[str, Any] = {
            "schema_version": 1,
            "ids": [self.by_id[i].to_dict() for i in sorted(self.by_id)],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")


def parse_id(id_: str) -> tuple[str, str, str]:
    """Split `<kind>.<key>#<8hex>` into (kind, key, suffix)."""
    m = ID_RE.match(id_)
    if not m:
        raise IdError(f"malformed id: {id_!r}")
    return m.group(1), m.group(2), m.group(3)


def deterministic_suffix(kind: str, key: str, salt: str = "") -> str:
    """8-char hex suffix from `<kind>.<key>` (+ optional salt for collision recovery)."""
    h = hashlib.sha256(f"{kind}.{key}{salt}".encode("utf-8")).hexdigest()
    return h[:8]


def mint_id(kind: str, key: str, index: IdIndex) -> str:
    """Mint or return the existing id for (kind, key).

    Idempotent: re-minting a known (kind, key) returns the registered id
    without modifying the index. Determinism guarantees that two clean
    runs with the same input produce the same suffix.
    """
    if not KIND_RE.match(kind):
        raise IdError(f"invalid kind {kind!r}; must match {KIND_RE.pattern}")
    if not KEY_RE.match(key):
        raise IdError(f"invalid key {key!r}; must match {KEY_RE.pattern}")

    existing = index.lookup_kind_key(kind, key)
    if existing is not None:
        return existing.id

    salt = ""
    attempt = 0
    while True:
        suffix = deterministic_suffix(kind, key, salt)
        candidate = f"{kind}.{key}#{suffix}"
        clash = index.lookup_id(candidate)
        if clash is None:
            return candidate
        if (clash.kind, clash.key) == (kind, key):
            return clash.id
        attempt += 1
        if attempt > 1024:
            raise IdError(f"could not find collision-free suffix for {kind}.{key}")
        salt = f":{attempt}"


def collect_ids_from_tree(
    data: Any, file_path: str, kinds: Iterable[str] | None = None
) -> list[IdRecord]:
    """Walk a parsed YAML tree, returning every `id:` field whose value matches the uuid form.

    Records the JSONPath cursor where each id was found. `kinds`, if given,
    restricts which kinds are collected.
    """
    out: list[IdRecord] = []
    allowed = set(kinds) if kinds else None
    _walk(data, file_path, "", out, allowed)
    return out


def _walk(
    value: Any,
    file_path: str,
    cursor: str,
    out: list[IdRecord],
    allowed: set[str] | None,
) -> None:
    if isinstance(value, dict):
        # If this mapping itself has an `id:` of uuid form, record it.
        raw_id = value.get("id")
        if isinstance(raw_id, str):
            try:
                kind, key, _suffix = parse_id(raw_id)
            except IdError:
                pass  # not a uuid-form id; that's fine for dottedId rule ids
            else:
                if allowed is None or kind in allowed:
                    out.append(
                        IdRecord(
                            id=raw_id,
                            kind=kind,
                            key=key,
                            file=file_path,
                            json_pointer=cursor or "/",
                        )
                    )
        for k, v in value.items():
            _walk(v, file_path, f"{cursor}/{k}", out, allowed)
    elif isinstance(value, list):
        for i, sub in enumerate(value):
            _walk(sub, file_path, f"{cursor}/{i}", out, allowed)
