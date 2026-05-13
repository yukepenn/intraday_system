# configs/strategies/grids/

Focused or controlled grid specs. Each file references a base config via `base_config:` and defines:

- `fixed:` — dotted-key overrides applied on top of base.
- `grid:` — cartesian-product keys with list values.

Rules:

- Any key present in both `fixed` and `grid` is a hard error.
- Leaf-list values inside `base_config` (e.g. `vol_windows: [5, 15, 30]`) remain leaves; the grid expander only expands top-level `grid:` keys.
- No prefix-biased max-combos.

Phase 0/1A intentionally does NOT commit real strategy grids.
