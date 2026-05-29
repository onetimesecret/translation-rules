"""YAML / Markdown-frontmatter loaders. SPEC.md §2.3 step 1.

Centralises the StringDateLoader pattern from tests/schema/run.py so the
resolver and the schema fixture runner do not diverge. The runner can switch
to importing from here in a follow-up; for now the runner keeps its own copy
to remain self-contained as a PEP 723 script.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


class StringDateLoader(yaml.SafeLoader):
    """SafeLoader variant that keeps ISO date/datetime values as strings.

    PyYAML's default behavior maps `2026-04-12` to a `datetime.date` object,
    which fails JSON Schema `type: string` validation. Schemas in this repo
    validate ISO dates via the `isoDate` regex on raw strings, so the
    timestamp resolver is disabled here.

    The resolvers dict is rebuilt without the timestamp tag rather than
    mutating the inherited SafeLoader dict — otherwise yaml.safe_load global
    behavior would silently change for any other consumer in the same process.
    """


StringDateLoader.yaml_implicit_resolvers = {
    ch: [(tag, regex) for tag, regex in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


class LoaderError(Exception):
    """Raised when a file cannot be loaded as YAML or frontmatter."""


def load_yaml_file(path: Path) -> Any:
    """Load a YAML document, returning the parsed Python object.

    Empty files return None. Multi-document YAML is rejected — every YAML in
    this repo is a single document.
    """
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.load(text, Loader=StringDateLoader)
    except yaml.YAMLError as exc:
        raise LoaderError(f"{path}: malformed YAML: {exc}") from exc
    return data


def load_retro_frontmatter(path: Path) -> dict[str, Any]:
    """Load YAML frontmatter from a retrospective Markdown file.

    The body prose is intentionally discarded — only frontmatter is
    schema-validated per SPEC.md §3.
    """
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise LoaderError(f"{path}: missing YAML frontmatter")
    try:
        data = yaml.load(match.group(1), Loader=StringDateLoader)
    except yaml.YAMLError as exc:
        raise LoaderError(f"{path}: malformed frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise LoaderError(f"{path}: frontmatter must be a mapping")
    return data
