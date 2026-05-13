# Data tracking policy (Phase 1)

- Raw parquet and curated parquet are **local-only by default** (ignored via `.gitignore`).
- This repo commits **manifests / CSV / MD summaries** under `artifacts/data_foundation_phase1/`.
- `data/cache/**` remains ignored.
- Git LFS may be considered later if licensing/privacy allows.
