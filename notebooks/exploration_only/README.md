# notebooks/exploration_only/

Human exploration only. Notebooks here are scratchpads. They are NOT part of any pipeline and they are NOT the source of truth for any number.

Rules:

- Notebooks may read from `data/raw/`, `data/curated/`, `data/cache/`, `configs/`, `artifacts/`.
- Notebooks may NOT write into `configs/`.
- Notebooks may NOT write into `artifacts/layer1/runs/`, `artifacts/layer2/runs/`, `artifacts/layer3/runs/`.
- Notebooks may write into `artifacts/diagnostics/` (with care) for ad-hoc reviews.
- Strip outputs before committing.
- Prefer Python scripts + CLI commands for anything reproducible.

This folder is empty in Phase 0/1A.
