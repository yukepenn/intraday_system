# CONFIG_CONTRACT — intraday_system

Configs are runtime truth. CSV/MD are audit artifacts. This is non-negotiable.

## 1. Truth rule

The only files the runtime ever reads as configuration are YAML files under `configs/`. The runtime never reads Markdown or CSV to decide behavior. Markdown/CSV are review artifacts.

## 2. Config taxonomy

| Folder | Purpose |
| --- | --- |
| `configs/data/` | Dataset definitions, roots, sessions, symbols |
| `configs/execution/` | `ExecutionSpec` defaults |
| `configs/features/` | Feature set specs (`pa_core_v1`, `gap_core_v1`, etc.) |
| `configs/strategies/base/` | Canonical strategy base config (no grids) |
| `configs/strategies/grids/` | Focused/controlled grid specs |
| `configs/strategies/metadata/` | Routing metadata (family, priority, conflict_group) |
| `configs/candidates/` | Frozen Layer1 outputs (committed) |
| `configs/layer1/` | Layer1 run configs |
| `configs/layer2/` | Layer2 run configs |
| `configs/layer3/` | Layer3 fold + frozen system configs |
| `configs/reports/` | Report-rendering configs |

## 3. Strategy base config (target shape)

```yaml
strategy: pa_buy_sell_close_trend
version: strategy_v1

features:
  feature_set: pa_core_v1
  # required feature parameters here

signal:
  side: long_only
  entry_start_minute: 60
  entry_end_minute: 300
  # strategy-specific thresholds

risk:
  stop_mode: signal_low
  target_mode: fixed_r
  target_r: 1.2
  min_risk_per_share: 0.03
  max_trades_per_day: 1

backtest:
  eod_exit_minute: 389
  quantity: 1.0
  commission_per_trade: 0.0
  slippage_per_share: 0.01
  max_hold_minutes: 50
```

## 4. Strategy grid config (target shape)

```yaml
strategy: pa_buy_sell_close_trend
base_config: configs/strategies/base/pa_buy_sell_close_trend.yaml

fixed:
  risk.min_risk_per_share: 0.03
  risk.max_trades_per_day: 1

grid:
  signal.entry_start_minute: [60, 90]
  risk.target_r: [1.0, 1.35, 1.7]
```

## 5. Fixed / grid merge rules

1. Start from `base_config`.
2. Apply every `fixed` override (deep dotted-key merge).
3. For each cartesian point of `grid`, apply that combo on top of `(base + fixed)`.
4. **Hard error** if any key appears in both `fixed` and `grid` (no silent overlap).
5. **No prefix-biased max-combos.** All combos are addressed by their full coordinate.
6. List values that are intended as leaf values (e.g. `vol_windows: [5, 15, 30]`) must remain leaves; the grid expander only expands top-level grid keys.

The implementation lives in `src/intraday/layer1/grid.py`.

## 6. Layer1 run config (target shape)

```yaml
run_id: L1_QQQ_CONTROLLED_2023_2024_V1

symbol: QQQ
asset: equity
timeframe: 1m
data_root: data/curated/bars_1m_rth
start: "2023-01-01"
end: "2024-12-31"

execution_config: configs/execution/intraday_default.yaml

strategies:
  - name: pa_buy_sell_close_trend
    grid: configs/strategies/grids/pa_buy_sell_close_trend_focused.yaml

selection:
  max_per_strategy: 3
  min_trades: 20
  min_profit_factor_r: 1.05
  min_total_r: 0.0
  gate_label: L1_CONTROLLED_STRICT_V1

output:
  artifact_root: artifacts/layer1/runs
  candidate_root: configs/candidates/l1_controlled_qqq_v1
  save_trade_records: false
```

## 7. Layer2 run config (target shape)

```yaml
run_id: L2_QQQ_PA_GAP_CCI_V1
symbol: QQQ
start: "2023-01-01"
end: "2024-12-31"

candidate_root: configs/candidates/l1_controlled_qqq_v1
execution_config: configs/execution/intraday_default.yaml

router:
  mode: priority_with_regime_permissions
  family_priority: {gap: 90, pa: 80, cci: 60}
  conflict_policy:
    max_open_positions: 1
  daily_risk:
    max_trades_per_day: 3
    max_daily_loss_r: -2.0
    cooldown_after_loss_bars: 20

management:
  default_mode: fixed_r
```

## 8. Layer3 frozen config (target shape)

```yaml
system_id: QQQ_INTRADAY_L2_V1
frozen_at_git_sha: "<sha>"

candidate_root: configs/candidates/l1_controlled_qqq_v1
layer2_config: configs/layer2/controlled_pa_gap_cci.yaml
execution_config: configs/execution/intraday_default.yaml
folds_config: configs/layer3/folds_2020_2026.yaml

validation_rules:
  no_tuning_on_oos: true
  require_candidate_root_frozen: true
  require_execution_hash_match: true
```

## 9. Path rules

- All paths in committed YAML are relative to repo root.
- No absolute `D:\` paths in committed configs.
- Layer1 smoke/controlled-grid loaders validate `output.artifact_root` with **`is_absolute_path_like`** (rejects POSIX absolute, Windows drive-qualified, and UNC-style strings even when `Path(...).is_absolute()` is false on Linux).
- Local-only overrides may live in `artifacts/**/local/` (ignored), never in `configs/`.

## 10. Validation entrypoints (later phases)

- `intraday strategies validate --strategy ...`
- `intraday validate candidates --root configs/candidates/...`
- `intraday validate artifacts`
