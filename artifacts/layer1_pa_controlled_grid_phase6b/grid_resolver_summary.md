# Grid resolver summary

- `load_grid_document` — load grid YAML.
- `normalize_override_mapping` — dotted keys → path tuples.
- `expand_grid` — cartesian product; deterministic axis order = YAML key order.
- `resolve_grid_combos` — `ResolvedGridCombo` with `params_json` (grid axes only, `stable_json_dumps`), `config_hash` (`hash_config(resolved_config)`), stable `combo_0001`… ids.
- Merge: deep-copy base from `base_config` path, apply fixed, apply combo.

CSV: `grid_resolver_summary.csv`.
