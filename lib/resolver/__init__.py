"""Translation rules resolver. SPEC.md §2.3 steps 1-4.

P1-2 scope: load + schema-validate, inheritance chain, merge with provenance,
ID resolution against an index. Lint, retro attachment, and emit are P1-3+.

Submodules are imported on demand by callers — keeping this file empty avoids
forcing every consumer (e.g. bin/mint-id, which only needs ids.py) to install
schema-validation dependencies.
"""
