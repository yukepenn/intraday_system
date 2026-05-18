# NEXT_HANDOFF

Last updated: **2026-05-18** (Phase **13** — pre-Layer2 strategy library runtime sprint).

---

## A. Git

- Branch: `main`
- Remote: `https://github.com/yukepenn/intraday_system.git`
- Pre-task HEAD: `448a721b543a77ef5362378e8d8bdda1d6c9b8c4`
- Task commit: see `git log -1` after push

---

## B. Task scope (Phase 13)

- Onboarded **9** new long-only strategy runtimes + existing PA anchor (**10** active families).
- Added generic feature groups **`levels`**, **`indicators`** and feature configs for ORB/gap/VWAP/indicator/library paths.
- Base YAML, metadata YAML, controlled small grid skeletons (≤24 combos each).
- Bundle: `artifacts/pre_layer2_strategy_library_runtime_sprint_phase13/`

**Did not:** candidate YAML, promotion, Layer2/3, WFO, live/paper, broad Layer1 grids, execution changes, shorts, QT import.

---

## C. Status / Codex preflight

- `CODEX_REVIEW.md` **not** modified by Cursor.

---

## D. Feature foundation

| Config | Columns | Notes |
| --- | ---: | --- |
| `opening_core_v1` | 16 | ORB family |
| `gap_level_core_v1` | 16 | gap + prior levels |
| `vwap_level_core_v1` | 11 | VWAP family |
| `indicator_core_v1` | 10 | CCI/stoch |
| `strategy_library_core_v1` | 28 | Phase 14 all-strategy smoke |
| `pa_core_v1` | 22 | unchanged |
| `orb_core_v1` | 9 | unchanged; hash `e3c3df12cb5a2bdd787d5a5deaeada374d9b0787d7c0b993a309eb5bfc03d27d` |

---

## E. Strategy library

Registry strategies: `pa_buy_sell_close_trend`, `orb_continuation`, `orb_retest_continuation`, `failed_orb`, `gap_acceptance_failure`, `vwap_trend_pullback`, `vwap_reclaim_reject`, `prior_day_level_trap`, `cci_extreme_snapback`, `stochastic_oversold_cross`.

All **long-only** under `signal_v1`.

---

## F. Tests / validation

| Check | Status |
| --- | --- |
| compileall | PASS |
| pytest full | 441 PASS |
| pytest smoke | 25 PASS |
| ruff (phase13 files) | PASS |
| CLI doctor/validate/features/strategies | PASS |
| features build QQQ | skipped (no curated data) |
| Layer1 grid / selection | not run |

---

## G. Not implemented

Candidate promotion, Layer2/3, WFO, live/paper, broad Layer1 research, Numba strategy fast paths, shorts.

---

## H. Decision (exactly one)

### `PRE_LAYER2_STRATEGY_LIBRARY_RUNTIME_COMPLETE`

---

## I. Recommended next step (exactly one)

### `RUN_LAYER1_STRATEGY_LIBRARY_SMALL_GRID`

Run tiny all-strategy Layer1 small-grid **smoke** across the library (plumbing validation). **Not** promotion.

---

## J. Review reminder

After push: Codex review on `main`. Cursor does not edit `CODEX_REVIEW.md`.
