# Resolved-config reconstruction audit

Code references:

```247:261:src/intraday/layer1/grid.py
        grid_nested = _paths_to_nested(combo)
        merged_cfg = _apply_overrides(base_dict, fixed_overrides)
        merged_cfg = _apply_overrides(merged_cfg, combo)
        ov = _deep_merge_dicts(fixed_nested, grid_nested)
        params_json = stable_json_dumps(grid_nested)
        h = hash_config(merged_cfg)
        resolved.append(
            ResolvedGridCombo(
                combo_id=f"combo_{i:04d}",
                overrides=ov,
                fixed_overrides=copy.deepcopy(fixed_nested),
                grid_overrides=copy.deepcopy(grid_nested),
                resolved_config=merged_cfg,
```

`write_layer1_grid_artifacts` persists `params_json` plus `config_hash` (via `Layer1GridRow`), but **`fixed_overrides` and full merged YAML are not serialized per CSV row**, only hashed.

## Operational implications for future promotion workflows

| Stage | Recommendation |
| --- | --- |
| Immediately (design-only) | Document the deterministic reconstruction ritual: pinned **repo SHA**, **base strategy YAML**, **grid YAML**, `combo_id` ordering, **`config_hash` equality check**. |
| Before any promotion engineering | Persist either **`resolved_config_json`** per sweep row OR a split schema with **`fixed_overrides_json`** (and optionally `grid_document_revision`). |

If promotion is attempted without bridging this gap, treat as **`FIX_GRID_REPORTING_SCHEMA`** priority defect class.
