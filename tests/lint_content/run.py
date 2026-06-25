#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests for lib/resolver/lint_content.py — the consumer-content register linter.

Two layers, mirroring tests/resolver/run.py's fixture+programmatic split:

  - Pure-API cases call lint_content()/lint_value() with inline registers and
    content dicts. They pin the behaviours the issue (translation-rules#42)
    calls out: the resolver engine must NOT false-positive where the legacy
    byte-grep did (French `te` in `Hôte`, Vietnamese `bà` in `bài`), MUST catch
    CJK `substring` hits no grep can see, must honour `exceptions` by span
    containment (du-in-Duden), and must scan only rendered strings (SKIP_KEYS).

  - CLI cases drive main() against a temp tree (resolved JSON + content files)
    to lock the exit-code contract (0 clean / 1 hit / 2 config / 3 empty glob).

No third-party deps: lint_content imports nothing outside the stdlib + the
sibling resolver modules, so this runs anywhere Python 3.11 does.

Exit codes: 0 all passed · 1 a case failed · 2 harness setup error.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "lib"))

try:
    from resolver import lint_content as lc
    from resolver.lint_content import (
        SKIP_KEYS,
        iter_content_strings,
        lint_content,
        register_from_resolved,
    )
except ImportError as exc:  # pragma: no cover - setup failure
    print(f"setup: {exc}", file=sys.stderr)
    sys.exit(2)


def _reg(forbidden, exceptions=None):
    return {"forbidden_tokens": forbidden, "exceptions": exceptions or []}


def _tok(token, context="standalone_word", severity="error"):
    return {"token": token, "context": context, "severity": severity}


# --------------------------------------------------------------------------- #
# Pure-API cases. Each returns (ok, message).
# --------------------------------------------------------------------------- #


def case_clean_formal():
    reg = _reg([_tok("du"), _tok("dein", "word_prefix")])
    files = [("f.json", {"k": {"text": "Geben Sie Ihre Daten ein"}})]
    r = lint_content("de_AT", reg, files)
    if not r.ok or r.findings:
        return False, f"expected clean, got {r.as_dict()}"
    if r.strings_scanned != 1 or r.files_scanned != 1:
        return False, f"scan counters off: {r.files_scanned}f/{r.strings_scanned}s"
    return True, "ok"


def case_real_hit():
    reg = _reg([_tok("du")])
    files = [("f.json", {"greeting": {"text": "Hast du Zeit?"}})]
    r = lint_content("de_AT", reg, files)
    if r.ok or len(r.findings) != 1:
        return False, f"expected 1 hit, got {[f.as_dict() for f in r.findings]}"
    f = r.findings[0]
    if f.token != "du" or f.key != "greeting.text" or f.context != "standalone_word":
        return False, f"finding fields wrong: {f.as_dict()}"
    if "du" not in f.snippet:
        return False, f"snippet missing token: {f.snippet!r}"
    return True, "ok"


def case_fp_french_te():
    # The legacy byte-grep cried 57x over `te` inside `Hôte`. The engine must not.
    reg = _reg([_tok("te")])
    files = [("f.json", {"k": {"text": "Bienvenue, Hôte"}})]
    r = lint_content("fr_FR", reg, files)
    if not r.ok or r.findings:
        return False, f"`te`-in-`Hôte` false positive returned: {r.as_dict()}"
    # But a standalone `te` IS a real hit.
    r2 = lint_content("fr_FR", reg, [("f.json", {"k": {"text": "je te vois"}})])
    if r2.ok or len(r2.findings) != 1:
        return False, f"standalone `te` should hit: {r2.as_dict()}"
    return True, "ok"


def case_fp_vietnamese_ba():
    # Legacy grep cried 291x over `bà` inside `bài`. Engine must not.
    reg = _reg([_tok("bà")])
    files = [("f.json", {"k": {"text": "bài viết của bạn"}})]
    r = lint_content("vi", reg, files)
    if not r.ok or r.findings:
        return False, f"`bà`-in-`bài` false positive returned: {r.as_dict()}"
    return True, "ok"


def case_cjk_substring():
    # No grep gate can scan these; `substring` is required.
    reg = _reg([_tok("你", "substring")])
    files = [("f.json", {"k": {"text": "你的账户"}})]
    r = lint_content("zh", reg, files)
    if r.ok or len(r.findings) != 1:
        return False, f"expected 1 CJK substring hit, got {r.as_dict()}"
    if r.findings[0].token != "你":
        return False, f"wrong token: {r.findings[0].as_dict()}"
    return True, "ok"


def case_exception_span_containment():
    # `du` inside the allowlisted `Duden` is suppressed; a standalone `du` in the
    # same string is NOT spared just because `Duden` appears.
    reg = _reg([_tok("du")], exceptions=[{"token": "Duden"}])
    inside = lint_content(
        "de_AT", reg, [("f.json", {"k": {"text": "Das Duden hilft"}})]
    )
    if not inside.ok or inside.findings:
        return False, f"du-in-Duden should be suppressed: {inside.as_dict()}"
    both = lint_content("de_AT", reg, [("f.json", {"k": {"text": "Duden und du"}})])
    if both.ok or len(both.findings) != 1:
        return False, f"standalone du beside Duden must hit: {both.as_dict()}"
    return True, "ok"


def case_metadata_skipped():
    # A forbidden token sitting only in non-rendered keys must NOT be flagged;
    # the same token in `text` must be. Proves the SKIP_KEYS policy.
    reg = _reg([_tok("du")])
    doc = {
        "entry": {
            "text": "Geben Sie acht",  # clean rendered copy
            "source_hash": "du99",  # hash — skipped
            "renderer": "markdown",
            "context": "shown when du presses submit",  # translator note — skipped
            "note": "du note",  # skipped
        },
        "_meta": {"purpose": "du appears here but it's metadata"},  # skipped block
    }
    r = lint_content("de_AT", reg, [("f.json", doc)])
    if not r.ok or r.findings:
        return False, f"metadata keys should be skipped, got {r.as_dict()}"
    # Now move `du` into the rendered text.
    doc["entry"]["text"] = "Hast du das gesehen"
    r2 = lint_content("de_AT", reg, [("f.json", doc)])
    if r2.ok or len(r2.findings) != 1:
        return False, f"rendered `du` must hit: {r2.as_dict()}"
    return True, "ok"


def case_snippet_umlaut_faithful():
    # Casefolding ß->ss changes length; the snippet must still show original text.
    reg = _reg([_tok("du")])
    r = lint_content(
        "de_AT", reg, [("f.json", {"k": {"text": "Straße, hast du recht"}})]
    )
    if len(r.findings) != 1:
        return False, f"expected 1 hit, got {r.as_dict()}"
    snip = r.findings[0].snippet
    if "Straße" not in snip or "du" not in snip:
        return False, f"snippet not faithful to original: {snip!r}"
    return True, "ok"


def case_severity_warning_non_fatal():
    reg = _reg([_tok("du", severity="warning")])
    r = lint_content("de_AT", reg, [("f.json", {"k": {"text": "hast du"}})])
    if not r.ok:
        return False, "warning-severity hit must keep ok=True"
    if len(r.findings) != 1 or r.findings[0].severity != "warning":
        return False, f"expected 1 warning finding, got {r.as_dict()}"
    return True, "ok"


def case_nested_and_list_paths():
    reg = _reg([_tok("du")])
    doc = {
        "a": {"b": {"text": "du hier"}},
        "list": [{"text": "kein Treffer"}, {"text": "auch du"}],
    }
    r = lint_content("de_AT", reg, [("f.json", doc)])
    keys = sorted(f.key for f in r.findings)
    if keys != ["a.b.text", "list.1.text"]:
        return False, f"path traversal wrong: {keys}"
    return True, "ok"


def case_registerless_is_clean():
    # A locale whose resolved model carries no register (or no forbidden_tokens)
    # scans clean — nothing to enforce.
    r = lint_content("xx", None, [("f.json", {"k": {"text": "anything du goes"}})])
    if not r.ok or r.findings:
        return False, f"registerless locale should be clean: {r.as_dict()}"
    r2 = lint_content("xx", _reg([]), [("f.json", {"k": {"text": "du du du"}})])
    if not r2.ok or r2.findings:
        return False, f"empty forbidden_tokens should be clean: {r2.as_dict()}"
    return True, "ok"


def case_iter_skips_and_register_helper():
    doc = {"k": {"text": "hi", "source_hash": "x"}, "_m": {"text": "skip"}}
    got = dict(iter_content_strings(doc))
    if got != {"k.text": "hi"}:
        return False, f"iter_content_strings leaked keys: {got}"
    if "source_hash" not in SKIP_KEYS:
        return False, "SKIP_KEYS missing source_hash"
    resolved = {"_meta": {"locale": "de_AT"}, "register": {"form": "formal"}}
    if register_from_resolved(resolved) != {"form": "formal"}:
        return False, "register_from_resolved did not return the register block"
    if register_from_resolved({"_meta": {}}) is not None:
        return False, "register_from_resolved should be None when absent"
    return True, "ok"


# --------------------------------------------------------------------------- #
# CLI exit-code cases. Each returns (ok, message).
# --------------------------------------------------------------------------- #


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def _run_cli(argv):
    with (
        contextlib.redirect_stdout(io.StringIO()),
        contextlib.redirect_stderr(io.StringIO()),
    ):
        return lc.main(argv)


def case_cli_exit_codes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        resolved = root / ".resolved" / "de_AT.json"
        _write(
            resolved,
            {
                "_meta": {"locale": "de_AT"},
                "register": {"forbidden_tokens": [_tok("du")]},
            },
        )
        _write(
            root / "content" / "de_AT" / "clean.json", {"k": {"text": "Sie sind da"}}
        )
        _write(root / "content" / "de_AT" / "dirty.json", {"k": {"text": "hast du"}})

        # exit 0 — clean only
        rc = _run_cli(
            [
                "--resolved",
                str(resolved),
                "--content-root",
                str(root),
                "content/de_AT/clean.json",
            ]
        )
        if rc != 0:
            return False, f"clean glob exit {rc}, expected 0"

        # exit 1 — a violation present
        rc = _run_cli(
            [
                "--resolved",
                str(resolved),
                "--content-root",
                str(root),
                "content/de_AT/*.json",
            ]
        )
        if rc != 1:
            return False, f"violation glob exit {rc}, expected 1"

        # exit 3 — empty glob
        rc = _run_cli(
            [
                "--resolved",
                str(resolved),
                "--content-root",
                str(root),
                "content/de_AT/none*.json",
            ]
        )
        if rc != 3:
            return False, f"empty glob exit {rc}, expected 3"

        # exit 2 — missing resolved model
        rc = _run_cli(
            [
                "--resolved",
                str(root / "nope.json"),
                "--content-root",
                str(root),
                "content/de_AT/*.json",
            ]
        )
        if rc != 2:
            return False, f"missing-resolved exit {rc}, expected 2"

        # registerless resolved scans clean (exit 0) even over dirty content
        regless = root / ".resolved" / "xx.json"
        _write(regless, {"_meta": {"locale": "xx"}})
        rc = _run_cli(
            [
                "--resolved",
                str(regless),
                "--content-root",
                str(root),
                "content/de_AT/*.json",
            ]
        )
        if rc != 0:
            return False, f"registerless exit {rc}, expected 0"
    return True, "ok"


def case_cli_json_output():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        resolved = root / "de_AT.json"
        _write(
            resolved,
            {
                "_meta": {"locale": "de_AT"},
                "register": {"forbidden_tokens": [_tok("du")]},
            },
        )
        _write(root / "c" / "dirty.json", {"k": {"text": "hast du"}})
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = lc.main(
                [
                    "--resolved",
                    str(resolved),
                    "--content-root",
                    str(root),
                    "c/*.json",
                    "--json",
                ]
            )
        if rc != 1:
            return False, f"json-mode exit {rc}, expected 1"
        payload = json.loads(buf.getvalue())
        if payload["locale"] != "de_AT" or payload["ok"] is not False:
            return False, f"json payload header wrong: {payload}"
        if len(payload["findings"]) != 1 or payload["findings"][0]["token"] != "du":
            return False, f"json findings wrong: {payload['findings']}"
    return True, "ok"


CASES = [
    ("clean-formal", case_clean_formal),
    ("real-hit", case_real_hit),
    ("fp-french-te-in-hote", case_fp_french_te),
    ("fp-vietnamese-ba-in-bai", case_fp_vietnamese_ba),
    ("cjk-substring", case_cjk_substring),
    ("exception-span-containment", case_exception_span_containment),
    ("metadata-skipped", case_metadata_skipped),
    ("snippet-umlaut-faithful", case_snippet_umlaut_faithful),
    ("severity-warning-non-fatal", case_severity_warning_non_fatal),
    ("nested-and-list-paths", case_nested_and_list_paths),
    ("registerless-is-clean", case_registerless_is_clean),
    ("iter-skips-and-register-helper", case_iter_skips_and_register_helper),
    ("cli-exit-codes", case_cli_exit_codes),
    ("cli-json-output", case_cli_json_output),
]


def main(argv: list[str]) -> int:
    targets = set(argv[1:]) if len(argv) > 1 else None
    passed = failed = 0
    for name, fn in CASES:
        if targets and name not in targets:
            continue
        try:
            ok, msg = fn()
        except Exception as exc:  # noqa: BLE001
            ok, msg = False, f"unexpected error: {type(exc).__name__}: {exc}"
        print(f"  {'pass' if ok else 'FAIL'} {name}: {msg}")
        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
    print()
    print(f"summary: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
