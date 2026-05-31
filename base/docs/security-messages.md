# Rationale — generic security messages

Authentication and rate-limit messages in the `web.auth.security.*` namespace
must stay generic to avoid information disclosure. Revealing which credential
failed enables credential enumeration; revealing precise timing enables timing
attacks; revealing attempt counts lets an attacker track progress. The
canonical English forms and per-message rules are in
`local-guides/SECURITY-TRANSLATION-GUIDE.md` (OWASP ASVS 2.2.1/2.2.2, NIST
SP 800-63B). Translations preserve the generic semantics exactly.
