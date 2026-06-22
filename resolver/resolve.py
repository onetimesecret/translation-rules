#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.21,<5",
#   "referencing>=0.32,<1",
#   "pyyaml>=6,<7",
# ]
# ///
"""Translation rules resolver. SPEC.md §2.3 steps 1-4.

Pipeline:
  1. Load + schema-validate base.yaml, locales/<locale>/*.yaml, retrospectives/*.md
  2. Build inheritance chain for rules.yaml (de_AT -> de -> base)
  3. Merge with provenance
  4. Resolve every dotted/uuid/retro reference against a combined index;
     emit resolver/index.json

Usage:
    resolver/resolve.py de_AT --validate-only
    resolver/resolve.py de_AT --locales-dir locales --base-file base.yaml

Exit codes:
    0  success
    1  validation/resolution error in input data
    2  harness/setup error (missing schema, unreadable file, etc.)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Allow running as a script or as a module.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resolver.ids import (
    ID_RE,
    IdError,
    IdIndex,
    IdRecord,
    parse_id,
)
from resolver.inheritance import (
    InheritanceError,
    build_chain,
)
from resolver.loader import (
    LoaderError,
    load_retro_frontmatter,
    load_yaml_file,
)
from resolver.merge import MergeError, merge_chain, merge_glossary_terms
from resolver.model import ModelError, build_model
from resolver.lint import lint_model
from resolver.emit_json import emit_json
from resolver.emit_markdown import emit_markdown
from resolver.validate import (
    SchemaBundle,
    ValidationFailed,
    build_registry,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA_DIR = REPO_ROOT / "schema"

# Reference field names by shape.
DOTTED_REF_FIELDS = {
    "rule_ref",
    "rule_refs",
    "affected_rules",
    "register_ref",
    "glossary_ref",
    "baseline_ref",
    "baseline_pins",
}
RETRO_REF_FIELDS = {"retro_refs", "supersedes"}
UUID_REF_FIELDS = {"examples_added"}


@dataclass
class CombinedIndex:
    """Lookup for every authored id, irrespective of shape."""

    by_dotted: dict[str, IdRecord] = field(default_factory=dict)
    by_retro: dict[str, IdRecord] = field(default_factory=dict)
    by_uuid: IdIndex = field(default_factory=IdIndex)

    def add_dotted(self, rec: IdRecord) -> None:
        existing = self.by_dotted.get(rec.id)
        if existing is not None and existing.file != rec.file:
            raise IdError(
                f"duplicate dotted id {rec.id!r}: declared in {existing.file} and {rec.file}"
            )
        self.by_dotted[rec.id] = rec

    def add_retro(self, rec: IdRecord) -> None:
        existing = self.by_retro.get(rec.id)
        if existing is not None and existing.file != rec.file:
            raise IdError(
                f"duplicate retro id {rec.id!r}: declared in {existing.file} and {rec.file}"
            )
        self.by_retro[rec.id] = rec

    def add_uuid(self, rec: IdRecord) -> None:
        self.by_uuid.add(rec)

    def resolves(self, ref: str) -> bool:
        if ID_RE.match(ref):
            return self.by_uuid.lookup_id(ref) is not None
        if _looks_like_retro_id(ref):
            return ref in self.by_retro
        return ref in self.by_dotted

    def all_records(self) -> list[IdRecord]:
        out: list[IdRecord] = list(self.by_dotted.values())
        out.extend(self.by_retro.values())
        out.extend(self.by_uuid.by_id.values())
        return out


def _looks_like_retro_id(value: str) -> bool:
    parts = value.split("-", 3)
    return len(parts) == 4 and parts[0].isdigit() and len(parts[0]) == 4


@dataclass
class LoadedFile:
    path: Path
    schema_name: str
    data: Any
    locale: str | None  # for per-locale leaves; None for base/baselines/retro


@dataclass
class ResolverInputs:
    base_path: Path
    locales_dir: Path
    retros_dir: Path | None
    schema_dir: Path
    index_path: Path
    project_root: Path  # paths in index.json are stored relative to this


def _format_error(prefix: str, exc: Exception) -> str:
    return f"{prefix}: {exc}"


def _rel(path: Path, root: Path) -> str:
    """Path string relative to project root if possible, else absolute."""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _load_locale_files(
    locale: str,
    inputs: ResolverInputs,
    bundle: SchemaBundle,
) -> list[LoadedFile]:
    """Load and validate every <locales_dir>/<locale>/*.yaml file."""
    locale_dir = inputs.locales_dir / locale
    out: list[LoadedFile] = []
    if not locale_dir.exists():
        return out
    for path in sorted(locale_dir.iterdir()):
        if path.suffix != ".yaml" or not path.is_file():
            continue
        schema_name = path.stem
        if schema_name not in {"rules", "register", "glossary"}:
            # Future-proof: ignore unknown leaf files in P1-2 rather than fail.
            continue
        data = load_yaml_file(path)
        from resolver.validate import validate_file

        validate_file(path, data, schema_name, bundle)
        out.append(
            LoadedFile(path=path, schema_name=schema_name, data=data, locale=locale)
        )
    return out


def _load_retros(inputs: ResolverInputs, bundle: SchemaBundle) -> list[LoadedFile]:
    """Load + validate every retrospective frontmatter in retrospectives/."""
    out: list[LoadedFile] = []
    if inputs.retros_dir is None or not inputs.retros_dir.exists():
        return out
    for path in sorted(inputs.retros_dir.iterdir()):
        if path.suffix != ".md" or not path.is_file() or path.name == "README.md":
            continue
        data = load_retro_frontmatter(path)
        from resolver.validate import validate_file

        validate_file(path, data, "retrospective", bundle)
        out.append(
            LoadedFile(path=path, schema_name="retrospective", data=data, locale=None)
        )
    return out


def _load_baselines(inputs: ResolverInputs, bundle: SchemaBundle) -> LoadedFile | None:
    path = inputs.base_path.parent / "baselines.yaml"
    if not path.exists():
        return None
    data = load_yaml_file(path)
    from resolver.validate import validate_file

    validate_file(path, data, "baselines", bundle)
    return LoadedFile(path=path, schema_name="baselines", data=data, locale=None)


def _index_dotted_ids_in_rules(
    data: dict[str, Any], file_path: Path, sink: CombinedIndex, root: Path
) -> None:
    """Capture top-level + nested rule/anti_pattern dotted ids."""
    rel = _rel(file_path, root)
    top_id = data.get("id")
    if isinstance(top_id, str):
        # base.yaml's top id is "base"; locale rules files use "rules.<locale>".
        top_kind = "base" if top_id == "base" else "rules"
        sink.add_dotted(
            IdRecord(id=top_id, kind=top_kind, key=top_id, file=rel, json_pointer="/id")
        )
    for partition in ("rules", "anti_patterns"):
        items = data.get(partition)
        if not isinstance(items, list):
            continue
        for i, item in enumerate(items):
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                rid = item["id"]
                sink.add_dotted(
                    IdRecord(
                        id=rid,
                        kind=partition,
                        key=rid,
                        file=rel,
                        json_pointer=f"/{partition}/{i}/id",
                    )
                )


def _index_register(
    data: dict[str, Any], file_path: Path, sink: CombinedIndex, root: Path
) -> None:
    rel = _rel(file_path, root)
    rid = data.get("id")
    if isinstance(rid, str):
        sink.add_dotted(
            IdRecord(id=rid, kind="register", key=rid, file=rel, json_pointer="/id")
        )


def _index_glossary(
    data: dict[str, Any], file_path: Path, sink: CombinedIndex, root: Path
) -> None:
    rel = _rel(file_path, root)
    rid = data.get("id")
    if isinstance(rid, str):
        sink.add_dotted(
            IdRecord(id=rid, kind="glossary", key=rid, file=rel, json_pointer="/id")
        )
    terms = data.get("terms")
    if not isinstance(terms, list):
        return
    for ti, term in enumerate(terms):
        if not isinstance(term, dict):
            continue
        tid = term.get("id")
        if isinstance(tid, str) and ID_RE.match(tid):
            kind, key, _suf = parse_id(tid)
            sink.add_uuid(
                IdRecord(
                    id=tid, kind=kind, key=key, file=rel, json_pointer=f"/terms/{ti}/id"
                )
            )
        for ei, ex in enumerate(term.get("examples") or []):
            if (
                isinstance(ex, dict)
                and isinstance(ex.get("id"), str)
                and ID_RE.match(ex["id"])
            ):
                kind, key, _ = parse_id(ex["id"])
                sink.add_uuid(
                    IdRecord(
                        id=ex["id"],
                        kind=kind,
                        key=key,
                        file=rel,
                        json_pointer=f"/terms/{ti}/examples/{ei}/id",
                    )
                )


def _index_baselines(
    data: dict[str, Any], file_path: Path, sink: CombinedIndex, root: Path
) -> None:
    rel = _rel(file_path, root)
    rid = data.get("id")
    if isinstance(rid, str):
        sink.add_dotted(
            IdRecord(id=rid, kind="baselines", key=rid, file=rel, json_pointer="/id")
        )
    blocks = data.get("baselines")
    if isinstance(blocks, dict):
        for locale in blocks:
            sink.add_dotted(
                IdRecord(
                    id=f"baselines.{locale}",
                    kind="baselines",
                    key=locale,
                    file=rel,
                    json_pointer=f"/baselines/{locale}",
                )
            )


def _index_retro(
    data: dict[str, Any], file_path: Path, sink: CombinedIndex, root: Path
) -> None:
    rel = _rel(file_path, root)
    rid = data.get("id")
    if isinstance(rid, str):
        sink.add_retro(
            IdRecord(
                id=rid, kind="retrospective", key=rid, file=rel, json_pointer="/id"
            )
        )


def _walk_refs(data: Any, cursor: str, out: list[tuple[str, str]]) -> None:
    """Collect every (cursor, ref_value) for known reference fields."""
    if isinstance(data, dict):
        for key, value in data.items():
            sub = f"{cursor}/{key}"
            if (
                key in DOTTED_REF_FIELDS
                or key in RETRO_REF_FIELDS
                or key in UUID_REF_FIELDS
            ):
                if isinstance(value, str):
                    out.append((sub, value))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str):
                            out.append((f"{sub}/{i}", item))
            _walk_refs(value, sub, out)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            _walk_refs(item, f"{cursor}/{i}", out)


def _check_refs(scope: str, data: Any, index: CombinedIndex, errors: list[str]) -> None:
    refs: list[tuple[str, str]] = []
    _walk_refs(data, "", refs)
    for cursor, ref in refs:
        if not index.resolves(ref):
            errors.append(f"{scope}: dangling reference {ref!r} at {cursor or '/'}")


def resolve_locale(
    locale: str,
    inputs: ResolverInputs,
    *,
    validate_only: bool = False,
) -> dict[str, Any]:
    """Run the full P1-2 pipeline for one locale. Returns a result dict."""
    if not inputs.base_path.exists():
        raise FileNotFoundError(f"base file missing: {inputs.base_path}")
    if not inputs.locales_dir.exists():
        raise FileNotFoundError(f"locales dir missing: {inputs.locales_dir}")
    bundle = build_registry(inputs.schema_dir)

    # Step 1a: load + validate base.
    base_data = load_yaml_file(inputs.base_path)
    from resolver.validate import validate_file

    validate_file(inputs.base_path, base_data, "base", bundle)

    # Step 1b: load + validate locale leaves (rules, register, glossary).
    locale_files = _load_locale_files(locale, inputs, bundle)
    if not locale_files:
        raise FileNotFoundError(
            f"no YAML files found under {inputs.locales_dir / locale}"
        )

    # Step 1c: parents on the inheritance chain for rules.yaml only.
    rules_files = [f for f in locale_files if f.schema_name == "rules"]
    if len(rules_files) > 1:
        raise InheritanceError(f"multiple rules.yaml under {locale}")

    chain_nodes = []
    if rules_files:
        # Pre-load+validate every parent in the chain.
        def loader(p: Path):
            data = load_yaml_file(p)
            schema_name = "base" if p == inputs.base_path else "rules"
            validate_file(p, data, schema_name, bundle)
            return data

        chain_nodes = build_chain(locale, inputs.locales_dir, inputs.base_path, loader)
        merged_rules, provenance = merge_chain(chain_nodes)
    else:
        # No rules.yaml on this locale — surface a clear message; this is rare
        # in practice (Phase 1 de_AT will have one).
        merged_rules = base_data
        provenance = {}

    # Glossary inheritance: merge along the same chain as rules, child-first.
    # ADR-001: a child glossary that omits a term inherits the parent's term
    # (term-key override). Without this, an fr_CA delta-only glossary would
    # emit a `.resolved` missing inherited `fr` terminology — exactly the
    # failure mode #29 surfaced. Register is intentionally NOT merged: registers
    # are per-locale by design (see ADR-001 §Decision).
    leaf_glossary = next(
        (f.data for f in locale_files if f.schema_name == "glossary"), None
    )
    glossaries_child_first: list[dict] = []
    if leaf_glossary is not None:
        glossaries_child_first.append(leaf_glossary)
    for node in chain_nodes:
        if node.path == inputs.base_path or node.locale == locale:
            continue
        parent_glossary_path = inputs.locales_dir / node.locale / "glossary.yaml"
        if not parent_glossary_path.exists():
            continue
        parent_glossary = load_yaml_file(parent_glossary_path)
        validate_file(parent_glossary_path, parent_glossary, "glossary", bundle)
        glossaries_child_first.append(parent_glossary)
    merged_glossary = merge_glossary_terms(glossaries_child_first)

    # Step 1d: baselines + retrospectives (project-wide, locale-agnostic).
    baselines = _load_baselines(inputs, bundle)
    retros = _load_retros(inputs, bundle)

    # Step 4 prep: build the combined index.
    index = CombinedIndex()
    root = inputs.project_root
    _index_dotted_ids_in_rules(base_data, inputs.base_path, index, root)
    for f in locale_files:
        if f.schema_name == "rules":
            _index_dotted_ids_in_rules(f.data, f.path, index, root)
        elif f.schema_name == "register":
            _index_register(f.data, f.path, index, root)
        elif f.schema_name == "glossary":
            _index_glossary(f.data, f.path, index, root)
    for node in chain_nodes:
        if node.path != inputs.base_path:
            _index_dotted_ids_in_rules(node.data, node.path, index, root)
    if baselines is not None:
        _index_baselines(baselines.data, baselines.path, index, root)
    for retro in retros:
        _index_retro(retro.data, retro.path, index, root)

    # Step 4: walk merged rules + per-locale leaves + baselines + retros for refs.
    # The glossary is checked from the inheritance-merged view so inherited
    # terms' refs are validated against the same combined index — leaf-only
    # checking would silently skip parent terms.
    errors: list[str] = []
    _check_refs(f"rules ({locale})", merged_rules, index, errors)
    for f in locale_files:
        if f.schema_name in ("rules", "glossary"):
            continue
        _check_refs(f"{f.schema_name} ({locale})", f.data, index, errors)
    if merged_glossary is not None:
        _check_refs(f"glossary ({locale})", merged_glossary, index, errors)
    if baselines is not None:
        _check_refs("baselines", baselines.data, index, errors)
    for retro in retros:
        # A retro's refs are only meaningful for the locales it targets. A
        # de_AT-scoped retro referencing rule.de_AT-formality must not be
        # ref-checked against the `de` layer's index (where that rule does not
        # exist). Universal retros (empty affected_locales) check everywhere.
        locs = retro.data.get("affected_locales") or []
        if locs and locale not in locs:
            continue
        _check_refs(f"retro {retro.path.name}", retro.data, index, errors)

    if errors:
        raise ResolutionError("dangling references:\n  " + "\n  ".join(errors))

    # NOTE: index.json is no longer written here. Under --all this function is
    # called once per locale, and writing inside the loop made the dump
    # last-write-wins (the committed index could never carry more than the final
    # locale). The caller (main) now owns the dump: it writes a single locale's
    # index for a single-locale run, or the UNION across every locale for --all.
    # The CombinedIndex is surfaced so the caller can accumulate that union.

    return {
        "locale": locale,
        "merged_rules": merged_rules,
        "provenance": provenance,
        "chain": [n.locale for n in chain_nodes],
        "index": index,
        "index_records": len(index.all_records()),
        # Raw per-locale leaves + retros surfaced for the P1-3 assemble step
        # (resolver/model.py). emit/lint are pure projections of these.
        "register": next(
            (f.data for f in locale_files if f.schema_name == "register"), None
        ),
        "glossary": merged_glossary,
        "retros": [r.data for r in retros],
    }


class ResolutionError(Exception):
    """Raised when ID resolution fails (dangling refs, etc.)."""


def _accumulate_records(idx_out: IdIndex, records: list[IdRecord]) -> None:
    """Add every record into idx_out, raising on a genuine cross-locale clash.

    base.yaml / baselines.yaml / retrospective ids are SHARED — they appear in
    every locale's CombinedIndex — so under --all the union re-adds identical
    records many times. IdIndex.add is idempotent for an identical (id -> same
    kind,key) re-add and only raises IdError when the SAME id maps to a
    DIFFERENT (kind, key). We deliberately let that IdError propagate: a real
    cross-locale id collision must surface, not be silently dropped.
    """
    for rec in records:
        idx_out.add(rec)


def _resolve_source_commit(repo_root: Path, override: str | None) -> str:
    """The translation-rules commit pinned into emitted artifacts. Explicit
    override wins (tests pass a stub); else the rules repo HEAD; else UNPINNED
    when not a git tree."""
    if override:
        return override
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "UNPINNED"


def _discover_locales(locales_dir: Path) -> list[str]:
    # A locale dir is one that actually carries leaf YAML (rules/register/
    # glossary). Skip helper dirs that live under locales/ but hold tooling
    # rather than translations (e.g. locales/scripts/) — otherwise --all would
    # try to resolve them and trip the "no YAML files found" guard with exit 2.
    return (
        sorted(
            p.name
            for p in locales_dir.iterdir()
            if p.is_dir() and not p.name.startswith(".") and any(p.glob("*.yaml"))
        )
        if locales_dir.exists()
        else []
    )


def load_lint_docs(
    inputs: ResolverInputs, locale: str, model: dict[str, Any]
) -> dict[str, str]:
    """Embedded rationale docs for the step-6 docs lint, keyed by
    project-root-relative path: every *.md under base/docs/ and
    locales/<locale>/docs/, plus every `rationale_index` path that exists on
    disk. A rationale_index path absent from the returned mapping surfaces as
    a dangling-doc finding in lint_model (doc paths are not ref-walked by the
    step-4 ID resolution, so existence is enforced at lint time)."""
    root = inputs.project_root
    docs: dict[str, str] = {}
    for docs_dir in (root / "base" / "docs", inputs.locales_dir / locale / "docs"):
        if not docs_dir.is_dir():
            continue
        for path in sorted(docs_dir.rglob("*.md")):
            docs[_rel(path, root)] = path.read_text(encoding="utf-8")
    for paths in (model.get("rationale_index") or {}).values():
        for rel_path in paths:
            path = root / rel_path
            if rel_path not in docs and path.is_file():
                docs[rel_path] = path.read_text(encoding="utf-8")
    return docs


def _emit_for_locale(
    locale: str,
    result: dict[str, Any],
    *,
    inputs: ResolverInputs,
    formats: set[str],
    do_lint: bool,
    source_commit: str,
    generated_at: str,
    emit_dir: Path,
) -> dict[str, Any]:
    """Assemble the model once, then project to the requested outputs + lint."""
    model = build_model(
        locale=locale,
        merged_rules=result["merged_rules"],
        register=result.get("register"),
        glossary=result.get("glossary"),
        retros=result.get("retros") or [],
        source_commit=source_commit,
        generated_at=generated_at,
    )
    written: list[str] = []
    if "json" in formats:
        path = emit_dir / ".resolved" / f"{locale}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(emit_json(model), encoding="utf-8")
        written.append(str(path))
    if "md" in formats:
        # SPEC §2.3: the human guide is emitted to
        # <emit-dir>/guides/for-translators/<locale>.md (the app repo vendors it
        # at locales/guides/for-translators/), alongside the JSON's
        # <emit-dir>/.resolved/. Keeping the `guides/` segment lets a single
        # `--emit-dir locales` land both artifacts in their canonical homes.
        path = emit_dir / "guides" / "for-translators" / f"{locale}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(emit_markdown(model, source_commit), encoding="utf-8")
        written.append(str(path))

    lint_result = None
    if do_lint:
        lint_result = lint_model(model, docs=load_lint_docs(inputs, locale, model))
    return {"model": model, "written": written, "lint": lint_result}


def _emit_formats(raw: str | None) -> set[str]:
    if not raw:
        return set()
    out = {f.strip() for f in raw.split(",") if f.strip()}
    unknown = out - {"md", "json"}
    if unknown:
        raise argparse.ArgumentTypeError(
            f"unknown --emit format(s): {sorted(unknown)}; valid: md, json"
        )
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="resolver/resolve.py", description=__doc__)
    parser.add_argument(
        "locale", nargs="?", help="Locale code, e.g. de_AT. Omit with --all."
    )
    parser.add_argument(
        "--all", action="store_true", help="Resolve every locale under --locales-dir."
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run pipeline but do not write resolver/index.json or artifacts.",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run step-6 lint on the resolved model; non-zero exit on error findings.",
    )
    parser.add_argument(
        "--emit",
        type=_emit_formats,
        default=set(),
        help="Comma-separated artifacts to write: md,json (default: none).",
    )
    parser.add_argument(
        "--emit-dir",
        default=".",
        help="Root for emitted artifacts: <dir>/.resolved/ and <dir>/guides/for-translators/ (default: .).",
    )
    parser.add_argument(
        "--source-commit",
        default=None,
        help="Override the translation-rules SHA pinned into artifacts (default: git HEAD or UNPINNED).",
    )
    parser.add_argument(
        "--generated-at",
        default=None,
        help="Override _meta.generated_at (ISO 8601). Default: now (UTC). Pin for reproducible output.",
    )
    parser.add_argument(
        "--locales-dir",
        default="locales",
        help="Directory containing per-locale YAML files (default: locales).",
    )
    parser.add_argument(
        "--base-file",
        default="base.yaml",
        help="Path to universal rules YAML (default: base.yaml).",
    )
    parser.add_argument(
        "--retrospectives-dir",
        default="retrospectives",
        help="Directory containing retrospective .md files (default: retrospectives).",
    )
    parser.add_argument(
        "--schema-dir",
        default=str(DEFAULT_SCHEMA_DIR),
        help="Directory containing JSON Schemas (default: <repo>/schema).",
    )
    parser.add_argument(
        "--index-path",
        default="resolver/index.json",
        help="Path to write resolver index (default: resolver/index.json).",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root for relative paths in index.json (default: .).",
    )
    args = parser.parse_args(argv)

    inputs = ResolverInputs(
        base_path=Path(args.base_file).resolve(),
        locales_dir=Path(args.locales_dir).resolve(),
        retros_dir=Path(args.retrospectives_dir).resolve()
        if Path(args.retrospectives_dir).exists()
        else None,
        schema_dir=Path(args.schema_dir).resolve(),
        index_path=Path(args.index_path).resolve(),
        project_root=Path(args.project_root).resolve(),
    )

    if args.all:
        locales = _discover_locales(inputs.locales_dir)
        if not locales:
            print(f"setup: no locale dirs under {inputs.locales_dir}", file=sys.stderr)
            return 2
    elif args.locale:
        locales = [args.locale]
    else:
        parser.error("a locale is required unless --all is given")

    source_commit = _resolve_source_commit(inputs.project_root, args.source_commit)
    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
    emit_dir = Path(args.emit_dir).resolve()

    lint_failures = 0
    # Accumulate the id index across every resolved locale. For a single-locale
    # run this holds just that locale's records; under --all it becomes the
    # UNION of all locales (base/baselines/retro ids are shared and re-added
    # idempotently; a genuine id collision raises IdError via _accumulate_records).
    union_index = IdIndex()
    for locale in locales:
        try:
            result = resolve_locale(locale, inputs, validate_only=args.validate_only)
            if not args.validate_only:
                _accumulate_records(union_index, result["index"].all_records())
            emitted = (
                _emit_for_locale(
                    locale,
                    result,
                    inputs=inputs,
                    formats=args.emit,
                    do_lint=args.lint,
                    source_commit=source_commit,
                    generated_at=generated_at,
                    emit_dir=emit_dir,
                )
                if (args.emit or args.lint)
                else None
            )
        except (
            LoaderError,
            ValidationFailed,
            InheritanceError,
            MergeError,
            ResolutionError,
            IdError,
            ModelError,
        ) as exc:
            print(_format_error(f"error ({locale})", exc), file=sys.stderr)
            return 1
        except FileNotFoundError as exc:
            print(_format_error(f"setup ({locale})", exc), file=sys.stderr)
            return 2

        chain_str = " -> ".join(result["chain"]) if result["chain"] else "(no chain)"
        summary = (
            f"resolved {locale}: chain={chain_str}, "
            f"refs={result['index_records']} ids indexed"
        )

        if args.validate_only and not args.emit:
            # Per issue #8: --validate-only prints merged tree to stdout, exits 0.
            json.dump(result["merged_rules"], sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            print(summary, file=sys.stderr)
        else:
            print(summary)
        if emitted:
            for path in emitted["written"]:
                print(f"emitted {path}")
            lint_result = emitted["lint"]
            if lint_result is not None:
                status = "pass" if lint_result.ok else "FAIL"
                print(f"lint {locale}: {status} ({len(lint_result.findings)} findings)")
                for f in lint_result.findings:
                    where = ""
                    if f.doc is not None:
                        where = f" ({f.doc}:{f.line})" if f.line else f" ({f.doc})"
                    print(
                        f"  [{f.severity}] {f.check}: {f.message}{where}",
                        file=sys.stderr,
                    )
                if not lint_result.ok:
                    lint_failures += 1

    # Dump the index ONCE, after the loop, over the accumulated union. This is
    # the fix for the old last-write-wins bug: under --all the committed index
    # now carries every locale's ids, not just the final one. --validate-only
    # writes nothing; --index-path is honored via inputs.index_path.
    if not args.validate_only:
        union_index.dump(inputs.index_path)
        print(f"wrote {inputs.index_path}")

    if lint_failures:
        print(f"lint: {lint_failures} locale(s) failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
