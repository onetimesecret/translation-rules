# Rationale — harmonize is keys-only

A "harmonize" task is a structural pass: it may align key paths, placeholder
names, JSON/YAML structure, and whitespace. It must never touch register,
tone, terminology, or the text content of a translated string. The boundary is
the line between safe automation and the failure that produced the 2026-04-12
de_AT register flip: a manual "harmonize" that rewrote text under the same
label. The sanctioned, automated harmonize (the website's key-sync action) is
safe precisely because it only adds and removes keys. If a harmonize task
appears to need text rewrites, it is mislabeled — stop and file a retrospective.
