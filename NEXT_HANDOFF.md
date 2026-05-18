# NEXT_HANDOFF

Last updated: **2026-05-18** (`REFINE_PA_GRID_AND_RERUN` / Phase **10**).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Task commit: see local `git log -1` after push
- HEAD should match **`origin/main`** after push (**non-force** only)

---

## B. Task scope (Phase 10)

- Small PA **risk-path diagnostic grid** (12 combos) on QQQ 2024H1 design + 2024H2 stress retest.
- **Did not** change PA strategy, features, execution, promote candidates, or write runtime candidate YAMLs.
- Produced `artifacts/pa_risk_grid_diagnostic_phase10/` review bundle.

---

## C. Schema / hygiene preflight

- `atr_buffer`, `backtest.max_hold_minutes` grid overrides: **supported** (PASS).
- CHANGES Phase 6d stale “latest” heading → historical anchor.
- Phase 10 `local_run` gitignored under `artifacts/pa_risk_grid_diagnostic_phase10/local_run/`.

---

## D. Diagnostic grid design

- Grid: `configs/strategies/grids/pa_buy_sell_close_trend_risk_diagnostic_small.yaml`
- Axes: `stop_mode` [signal_low, atr_buffer], `target_r` [0.8, 1.0, 1.2], `max_hold_minutes` [30, 50]
- Fixed: body_pct 0.56, require_vwap false, long_only entry 60–300; **no rolling_low**; not chosen from H2 winners.

---

## E. Layer1 diagnostic configs

- `configs/layer1/pa_risk_diag_qqq_2024h1.yaml` (design)
- `configs/layer1/pa_risk_diag_qqq_2024h2.yaml` (stress)
- `grid-inspect`: 12 combos each.

---

## F. Data validation

- QQQ 2024H1: 48360 rows, 124 sessions — PASS
- QQQ 2024H2: 49380 rows, 128 sessions — PASS (540 missing minute slots warning)

---

## G. Design-window diagnostic grid

- Best total_r: **−4.79R** (`combo_0005`, signal_low, target_r 1.2, max_hold 30)
- All 12 combos **negative** total_r
- Dry-run: **12/12 REJECT** (`excessive_drawdown`, `negative_total_r`, `weak_profit_factor`)

---

## H. Confirmation-window diagnostic grid

- Best total_r: **+4.68R** (`combo_0005`) — still REJECT (max_dd ~19.8R)
- Dry-run: **12/12 REJECT** (`excessive_drawdown` all)
- H2 is stress retest only (Phase 9 hypothesis window), not fresh holdout.

---

## I. Selection dry-run on both windows

- `promotion_allowed_now=false` on **all 24** rows (12+12).
- Config reconstruction: 12/12 pass per window.
- No candidate YAML.

---

## J. Design-vs-confirmation diagnostic comparison

- **0/12** combos positive total_r in both windows.
- **0/12** combos max_dd ≤ 10R in both.
- `signal_low` dominates `atr_buffer`; max_hold 30 vs 50 negligible.
- Label: **`RISK_DIAGNOSTIC_WEAKENS_PA_PATH`**

---

## K. Diagnostic conclusion

- Risk-path diagnostic **did not** restore design-window economics or cross-window stability.
- **Not** ready for fresh holdout or promotion schema.
- Next: PA feature/logic review — not family expansion yet.

---

## L. Tests / validation

| Check | Status |
| --- | --- |
| `compileall src` | PASS |
| `pytest` smoke+unit | PASS |
| `pytest` full | PASS |
| Ruff format/check | PASS |
| CLI help/doctor/validate | PASS |
| `layer1 grid-inspect` | PASS (12 combos) |
| `layer1 grid` H1/H2 | PASS |
| `select-dry-run` H1/H2 | PASS |

---

## M. Explicit still-not-implemented

Real candidate YAML promotion, Layer2/3, WFO, live/paper, GAP/CCI, PA logic changes, feature kernel changes, broad PA grids, retuning from 2024H2 winners.

---

## N. Risks / blockers

| Risk | Status |
| --- | --- |
| Fixed signal slice vs Phase 6c grid | May explain H1 all-negative vs prior +8.88R rank-1 |
| H2 stress not independent holdout | Documented; fresh holdout still required if path revives |
| Drawdown gate | All rows fail `excessive_drawdown` both windows |

---

## O. Files changed (high-level)

`configs/strategies/grids/pa_buy_sell_close_trend_risk_diagnostic_small.yaml`, `configs/layer1/pa_risk_diag_qqq_2024h*.yaml`, `artifacts/pa_risk_grid_diagnostic_phase10/**`, `CHANGES.md`, status/docs.

---

## P. Artifact hygiene

- No parquet/cache/candidate YAML staged
- `CODEX_REVIEW.md` not modified by Cursor

---

## Q. Decision (exactly one)

### `PA_RISK_DIAGNOSTIC_COMPLETE_HOLD_PA_PATH`

Phase 10 risk diagnostic complete. PA path held pending feature/logic review.

---

## R. Recommended next step (exactly one)

### `REVIEW_PA_FEATURES_OR_LOGIC`

Review PA signal scoring, regime feature use, and grid doctrine before further diagnostics or holdout design. **Not** promotion.
