# Controlled grid contract (Phase 6b)

**Role:** Prove Layer1 can run a **small explicit** PA grid: base strategy YAML → fixed overrides → cartesian grid → resolved config per combo → same pipeline as smoke → **one metrics row per combo** in `sweep_results.csv`.

**Not:** Broad optimization, candidate promotion, Layer2/3, WFO, profitability claims, prefix-biased `max-combos` slicing.

**Flow:** `base_config` + `fixed` + grid point → `resolved_config` → `FeatureMatrix` (build once per run if feature YAML unchanged) → `SignalMatrix` → signal adapter → execution (**reference** canonical for shipped `controlled_pa_qqq_2024h1.yaml`) → `summarize_trade_results` → `Layer1GridRow`.

**Overlap:** Any dotted path in both `fixed` and `grid` → error (resolver + config `require_no_fixed_grid_overlap: true`).

**Artifacts:** Summary CSV/MD only under `output.artifact_root` (relative). No row-level trade dumps committed. `local_run/` gitignored.

Detail rows: `controlled_grid_contract.csv`.
