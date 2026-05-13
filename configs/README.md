# configs/

Runtime truth lives here. YAML only. No CSV/MD as runtime config.

## Subfolders

| Folder | Purpose |
| --- | --- |
| `data/` | Dataset, symbols, sessions, roots |
| `execution/` | `ExecutionSpec` defaults |
| `features/` | Feature set specs (`pa_core_v1`, etc.) |
| `strategies/base/` | Canonical strategy base configs (no grids) |
| `strategies/grids/` | Focused/controlled grid specs |
| `strategies/metadata/` | Routing metadata per strategy |
| `candidates/` | Frozen Layer1 outputs (committed) |
| `layer1/` | Layer1 run configs |
| `layer2/` | Layer2 run configs |
| `layer3/` | Layer3 fold + frozen system configs |
| `reports/` | Report-rendering configs |

## Rules

- All paths inside committed YAML are relative to repo root.
- No absolute `D:\` paths.
- Fixed/grid overlap inside a strategy grid file is a hard error.
- No prefix-biased max-combos. The engine resolves the full cartesian product (with explicit slicing only via separately committed grid variants).
- Strategy configs use `base + fixed + grid`; the loader merges them deterministically.

See `docs/CONFIG_CONTRACT.md` for the full contract.
