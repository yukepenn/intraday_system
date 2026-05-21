# configs/strategies/grids/

Focused or controlled grid specs. Each file references a base config via `base_config:` and defines:

- `fixed:` — dotted-key overrides applied on top of base.
- `grid:` — cartesian-product keys with list values.

Rules:

- Any key present in both `fixed` and `grid` is a hard error.
- Leaf-list values inside `base_config` (e.g. `vol_windows: [5, 15, 30]`) remain leaves; the grid expander only expands top-level `grid:` keys.
- No prefix-biased max-combos.
- `signal.side_mode` may be a grid axis only for bounded inspect/onboarding
  grids unless an explicit research-run phase authorizes economic grids.
- Setup codes must never be grid axes.
- `risk.target_mode` remains `fixed_r` unless a management phase explicitly
  authorizes otherwise.

Directory inventory:

- Root grids: historical controlled-small current-10 grids.
- `phase18b/`: historical/refined current-10 v2 grids.
- `phase19/`: Brooks PA 11-17 grid-inspect skeletons only.
- `phase19_immediate_fix_current10_side_aware/`: current-10 side-aware
  inspect-only grids, not alpha proof and not candidate input.
