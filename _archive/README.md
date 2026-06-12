# `_archive/` — prescriptive-vs-descriptive firewall

This tree is the firewall described in SPEC.md §2.1. Content here is
descriptive history, never prescriptive guidance: nothing in this directory
is ever compiled into resolver output, and the resolver never reads it.

Ground rules:

- **Adding** files here and **editing** them in place is unrestricted.
- **Moving or copying** a file out of `_archive/` — or **deleting** one —
  requires the `prescriptive-promotion` label on the PR. A deletion is gated
  because it is indistinguishable from the first half of a move that rename
  detection missed; the label is the escape hatch either way.

CI-enforced by `resolver/archive_firewall.py` via
`.github/workflows/archive-firewall.yml`. The same gate covers
`retrospectives/_archive/` (superseded retros).
