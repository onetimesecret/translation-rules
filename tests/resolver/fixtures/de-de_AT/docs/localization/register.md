# Rationale — register lock (fixture)

The locale's register is a fixed linguistic decision. This fixture doc exists
so the rationale_index path in base.yaml resolves on disk now that the docs
lint enforces doc-path existence; it must stay free of bare forbidden tokens.
Mentioning `du` inside an inline code span is an allowed mention, as is Duden
(allowlisted exception).
