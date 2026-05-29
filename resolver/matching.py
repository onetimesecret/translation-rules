"""Token/target string matching. SPEC.md §2.3 step 6.

One matcher, reused by two callers:
  - lint's forbidden-token pass (register `forbidden_tokens[].context`)
  - the model's example->sense routing and lint's example-target check

The four modes are exactly the `forbiddenToken.context` enum
(register.schema.json), so the same vocabulary describes both "this token must
be absent" and "this sense target must be present". Matching is
case-insensitive and Unicode-aware.

Default mode for the example/target check is `word_prefix` (Gap A, decided
2026-05-29): every German `good` example in the corpus places the sense term in
head position (Geheimnis -> Geheimnisses), never as a tail/interior compound,
so whole-word-prefix never false-positives and is strictly tighter than
`substring`. A per-sense override is a SPEC §8 extend-when-touched change,
deferred until real data needs it.
"""

from __future__ import annotations

import unicodedata

VALID_MODES = ("standalone_word", "word_prefix", "substring", "any")

# Default for the example<->sense-target presence check.
DEFAULT_TARGET_MODE = "word_prefix"


def _casefold(text: str) -> str:
    # NFC first so composed/decomposed umlauts compare equal, then casefold.
    return unicodedata.normalize("NFC", text).casefold()


def _is_word_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"


def contains(haystack: str, needle: str, mode: str) -> bool:
    """True if `needle` is present in `haystack` under `mode`.

    - standalone_word: needle bounded by non-word chars on both sides
    - word_prefix:     needle begins a word (left boundary), any suffix allowed
    - substring:       needle appears anywhere
    - any:             alias of substring (kept for register-enum parity)
    """
    if mode not in VALID_MODES:
        raise ValueError(f"unknown match mode {mode!r}; valid: {VALID_MODES}")
    if not needle:
        return False
    hay = _casefold(haystack)
    need = _casefold(needle)
    if mode in ("substring", "any"):
        return need in hay
    start = 0
    nlen = len(need)
    while True:
        idx = hay.find(need, start)
        if idx < 0:
            return False
        left_ok = idx == 0 or not _is_word_char(hay[idx - 1])
        if mode == "word_prefix":
            if left_ok:
                return True
        else:  # standalone_word
            right = idx + nlen
            right_ok = right == len(hay) or not _is_word_char(hay[right])
            if left_ok and right_ok:
                return True
        start = idx + 1
