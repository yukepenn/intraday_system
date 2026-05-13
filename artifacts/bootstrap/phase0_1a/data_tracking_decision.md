# Data tracking decision (Phase 0/1A)

## Inputs

- Inventory: `raw_data_inventory.csv` / `.md`.
- Total files: **104**.
- Total size: **34.264 MiB** (35,927,994 bytes).
- Largest file: **0.407 MiB** (well under 1 MiB).
- Layout: 100% `legacy_qt_like`.
- Git LFS available locally: **yes** (`git-lfs/3.4.1`).

## Decision

- **Git LFS is NOT enabled** by this phase. Justification: every parquet is sub-megabyte; normal Git handles them comfortably.
- **All files classified `safe_normal_git`** by the catalog.
- **Raw parquet is NOT staged in the Phase 0/1A commit.** The inventory manifest is staged instead. Rationale:
  1. Phase 0/1A is a structural bootstrap. Raw data tracking is a separate, reversible decision.
  2. Keeping the first commit narrow makes review easier on GitHub.
  3. The user can subsequently run `git add data/raw/ibkr` to track raw bytes once the tracking decision is finalized.
- **Cache (`data/cache/**`) is never tracked** — enforced by `.gitignore`.
- **Hot NumPy artifacts (`*.npy`, `*.npz`, `*.memmap`) are never tracked** — enforced by `.gitignore`.

## Thresholds applied

| Threshold | Bytes | Outcome |
| --- | --- | --- |
| `large_warn` (≥ 50 MiB) | 52,428,800 | none triggered |
| `too_large_requires_lfs` (≥ 100 MiB) | 104,857,600 | none triggered |

## Follow-up

If future datasets (e.g. tick-level futures, multi-symbol cross-section) exceed these thresholds:

1. Re-run `intraday data inventory --root data/raw/ibkr --output ...`.
2. If any file ≥ 50 MiB: warn in a new tracking-decision doc.
3. If any file ≥ 100 MiB and LFS is not configured: keep local-only.
4. If LFS is enabled: `git lfs track "*.parquet"`, commit `.gitattributes`, then track parquet via LFS.
