# Local path hygiene audit

Some **bootstrap** artifacts under `artifacts/bootstrap/phase0_1a/` still contain machine-local absolute paths (marked **local-only** in review).

**General docs**: `docs/QT_REFERENCE_POLICY.md` was sanitized to use `<qt-reference-root>`.

| file_path | matched_pattern | classification | action_taken |
| --- | --- | --- | --- |
| artifacts/bootstrap/phase0_1a/baseline_inventory.md | OneDrive / absolute path | local_only_artifact | noted; optional sanitize later |
| artifacts/bootstrap/phase0_1a/raw_data_inventory.md | D:/OneDrive | local_only_artifact | noted |
| docs/QT_REFERENCE_POLICY.md | drive letter example | general_doc | sanitized to `<qt-reference-root>` |
