# Phase19A — System-Wide Side-Support Foundation Design

This design is not a new runtime contract. It operationalizes existing contracts (`docs/STRATEGY_CONTRACT.md`, `docs/EXECUTION_CONTRACT.md`, `docs/CONFIG_CONTRACT.md`, `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`) for Phase19 Brooks PA strategy onboarding. If this design conflicts with the core contract docs, the contract docs win.

## 1. Current state (read-only baseline)

- `Side` enum (`src/intraday/core/types.py`): `FLAT = 0`, `LONG = +1`, `SHORT = -1`. Numba-stable.
- `RejectReason.SHORT_NOT_ALLOWED = 5` exists (`src/intraday/core/types.py`).
- `ExecutionSpec.allow_short: bool` exists (`src/intraday/execution/spec.py`).
- `materialize_trade` already rejects `side == SHORT` with `SHORT_NOT_ALLOWED` when `allow_short=false` (`src/intraday/execution/materialize.py`).
- `simulate_trade_path_reference` and `simulate_trade_path_fast` already support short fills (intrabar stop/target inverted, slippage sign flipped) once materialization accepts the intent.
- `configs/execution/intraday_default.yaml` ships with `allow_short: false`, making the current default research universe long-only.
- `SignalMatrix`/`validate_signal_matrix` (`src/intraday/strategies/contracts.py`) currently enforces a long-only entry convention: `side[entry] == LONG_SIDE`, `stop[entry] < close`. There is no published short-entry convention.
- `build_trade_intents_from_signals` (`src/intraday/backtest/signal_adapter.py`) rejects any `side != LONG` with `skip_reason="invalid_side"` — the adapter is hard-coded long-only.
- All current-10 strategy YAMLs (`configs/strategies/base/`, `configs/strategies/base/phase18b/`) set `signal.side: long_only`. All current-10 strategies emit `side=+1` only.
- No current strategy emits `side=-1`. No current YAML uses `side_mode`.

**Net conclusion:** execution already speaks long+short. The strategy + adapter + SignalMatrix validator are deliberately long-only and need a system-wide, contract-aligned uplift before any Phase19 strategy can emit `side=-1`.

## 2. Why side support must be system-wide, not PA-specific

- Short support is not a PA feature — it is an architecture capability that any strategy family may opt into (PA, ORB, gap, levels, indicators, etc.).
- Splitting long/short into two strategy files per family would double the strategy registry, duplicate setup-code spaces, complicate adapter logic, and inflate Layer1 grid surfaces.
- A single per-strategy `signal.side_mode` field plus a system-wide adapter/contract upgrade keeps every family on the same surface and preserves the "one strategy = one StrategyDef" rule in `docs/STRATEGY_FAMILY_ONBOARDING_CONTRACT.md`.
- Execution already has `allow_short`. The signal-side contract must catch up before strategies are allowed to express short intent. Anything else creates two truths or hidden coupling.

## 3. Default behavior preservation (current-10 must not change)

- The current default execution YAML (`configs/execution/intraday_default.yaml`) must keep `allow_short: false` unchanged.
- All existing current-10 base configs under `configs/strategies/base/` and `configs/strategies/base/phase18b/` must keep `signal.side: long_only` semantics (treated as `side_mode: long_only`).
- The signal-side contract upgrade must be backward-compatible: a strategy that does not specify `signal.side_mode` and continues to emit `side=+1` must still pass validation.
- Existing tests under `tests/unit/test_strategy_<current10>.py`, `tests/unit/test_phase18b_*`, `tests/unit/test_phase18c_*`, `tests/unit/test_phase18d_*`, and `tests/smoke/` must continue to pass without any economic change.
- The current-10 long-only setup-code space (1001, 2001, 2002, 2003, 3001, 4001, 4002, 5001, 6001, 6002) is reserved. Phase19 short setup codes must be additive and non-overlapping.

## 4. Strategy config: `signal.side_mode` (proposed contract operationalization)

Phase19 strategy base configs (only Phase19 strategies) introduce an explicit `signal.side_mode` field with three allowed values:

```yaml
signal:
  side_mode: long_only   # or short_only, or both
```

Semantics:

| `side_mode` | Long branch enabled | Short branch enabled | Notes |
|-------------|---------------------|----------------------|-------|
| `long_only` | yes | no | Default for Phase19 implementations until short support tested |
| `short_only` | no | yes | Requires execution `allow_short=true` |
| `both` | yes | yes | Strategy may emit either side on different bars |

Rules:

- Phase19 strategy YAMLs MUST define `signal.side_mode` explicitly.
- For backward compatibility, existing current-10 YAMLs MAY continue to use `signal.side: long_only`. Phase19 implementation may keep both keys readable transitionally; if both are present they must agree, otherwise `ConfigError`.
- Phase19 strategy `validate_config` MUST reject any other value with `ConfigError`.
- Phase19 strategy `validate_config` MUST raise `ConfigError` if `side_mode != long_only` while `signal.side` is also set to `long_only`.
- A strategy's `signal.side_mode = short_only` or `both` MUST NOT silently override execution `allow_short`. If execution `allow_short=false` and a strategy emits `side=-1`, execution will continue to deterministically reject the intent with `SHORT_NOT_ALLOWED` (current contract preserved).

## 5. SignalMatrix entry conventions (operationalized)

Phase19 must operationalize the strategy contract for non-long entries while preserving the current long convention. The implementation phase must extend `validate_signal_matrix` accordingly (no parallel validator).

Non-entry rows (no change):

- `entry = False`, `side = 0`, `stop = NaN`, `target_r = NaN`, `score = NaN`, `setup_code = 0`.

Long entry (no change):

- `entry = True`, `side = +1`, `stop` finite and `stop < reference_close`, `target_r` finite and `> 0`, `score` finite, `setup_code != 0`.

Short entry (new operationalization, contract-aligned with execution materialization rules):

- `entry = True`, `side = -1`, `stop` finite and `stop > reference_close`, `target_r` finite and `> 0`, `score` finite, `setup_code != 0`.
- `reference_close` is the bar-close price at the signal bar (`bars.close[t]`). The strategy emits the raw stop price; execution materializes the actual entry and final stop checks against the slippaged entry per `docs/EXECUTION_CONTRACT.md` §5. The strategy-level inequality (`stop > close`) is a conservative no-flip guard, matching the existing long-side guard.
- `setup_code` for short setups must be drawn from a stable Phase19 short setup-code namespace (see Section 9).

`validate_signal_matrix` must accept rows where `side[entry] ∈ {+1, -1}` and apply the correct inequality based on side; mixed long/short within one `SignalMatrix` is allowed (this is what `side_mode: both` enables).

## 6. Signal adapter behavior (operationalized)

The current `build_trade_intents_from_signals` rejects any non-LONG side via `invalid_side`. Phase19 implementation must:

- Accept rows with `side == +1` or `side == -1`.
- Validate finite `stop` (no inequality vs close inside the adapter — the adapter trusts the SignalMatrix validator and execution materializer).
- Validate finite `target_r > 0`.
- Continue to track `total_entries`, `valid_intents`, `skipped_invalid`, `skip_reasons`.
- Keep `invalid_side` as the skip reason for any `side ∉ {LONG, SHORT}` (e.g. `0` on a row marked `entry=True` due to a strategy bug).
- Pass the side to `TradeIntent.side` unchanged. Execution remains the only authority on whether the short intent is actually fillable (`SHORT_NOT_ALLOWED` is the existing reject reason).

The adapter MUST NOT branch on the strategy-level `side_mode`. The adapter is strategy-agnostic.

## 7. Execution config strategy for short-enabled research

- The default `configs/execution/intraday_default.yaml` MUST remain `allow_short: false`.
- A new opt-in execution config under `configs/execution/` is OUT OF SCOPE for Phase19 design. Phase19 implementation MAY add `configs/execution/intraday_default_short_enabled.yaml` with `allow_short: true`. Implementation phase decides; design does not require it.
- Phase19 Layer1 `grid-inspect-only` configs for strategies with `side_mode != long_only` must point at an execution config with `allow_short: true` only if such a config exists; otherwise they remain inspect-only artifacts that document the dependency.
- Per-strategy `side_mode = short_only` or `both` running against the default execution config (`allow_short: false`) is allowed; the adapter will pass short intents through and execution will reject them with `SHORT_NOT_ALLOWED`. This is the conservative default until short execution is verified end-to-end.

## 8. Setup-code namespace (operationalized)

Existing current-10 reserves `1xxx`–`6xxx`. Phase19 setup codes:

- `7101` ... `7110`: Phase19 long setup codes (one per strategy 11-20).
- `7201` ... `7210`: Phase19 short setup codes (one per strategy 11-20).
- Each Phase19 strategy emits its long setup code only when `side=+1`, and its short setup code only when `side=-1`.
- Diagnostic strategies (18-20) use the same scheme; the diagnostic-only flag is enforced at the metadata level, not the setup-code level.

Reservations:

| Strategy | Long code | Short code |
|----------|-----------|------------|
| 11 pa_second_entry_pullback | 7101 | 7201 |
| 12 pa_trading_range_bls_hs | 7102 | 7202 |
| 13 pa_failed_breakout_trap | 7103 | 7203 |
| 14 pa_opening_reversal_sr | 7104 | 7204 |
| 15 pa_breakout_pullback_continuation | 7105 | 7205 |
| 16 pa_tight_channel_pullback | 7106 | 7206 |
| 17 pa_broad_channel_zone | 7107 | 7207 |
| 18 pa_mtr_reversal_diagnostic | 7108 | 7208 |
| 19 pa_wedge_reversal_diagnostic | 7109 | 7209 |
| 20 pa_climax_reversal_diagnostic | 7110 | 7210 |

These numbers are part of the Phase19 design contract; implementation must reuse them.

## 9. Stop geometry (operationalized)

Long stops (no change): finite, strictly below the reference close on the signal bar; execution scan applies intrabar `low <= stop` for STOP fills.

Short stops (operationalized): finite, strictly above the reference close on the signal bar; execution scan applies intrabar `high >= stop` for STOP fills.

For each Phase19 strategy, the design matrix names the geometric anchor for both long and short stops (signal high/low, prior swing high/low, prior breakout extreme, ORB high/low, range mid, etc.). Strategies emit `stop` as a raw price. They do not compute risk-per-share, target price, or R outcome — execution does.

## 10. `target_r` policy (operationalized, unchanged)

- Strategies emit `target_r` (a positive R multiple) only. No target price.
- Execution computes `target_price = entry +/- target_r * risk_per_share` per `docs/EXECUTION_CONTRACT.md` §5.
- Phase19 strategies are NOT allowed to introduce `target_mode = range_mid`, `magnet_target`, or any non-`fixed_r` mode in the strategy layer. Target management is a future Layer2/management concern, not a strategy concern. Phase19 strategies use `risk.target_mode: fixed_r`.

## 11. Required tests before Phase19 short branches are accepted

The implementation phase must add tests of the following classes before any Phase19 strategy is allowed to emit `side=-1` against a non-default execution config:

1. **SignalMatrix contract — long entry** unchanged: `side=+1`, finite stop below close, finite `target_r>0`, finite score, nonzero setup code.
2. **SignalMatrix contract — short entry**: `side=-1`, finite stop above close, finite `target_r>0`, finite score, nonzero setup code.
3. **SignalMatrix non-entry** unchanged: `side=0`, NaN stop/target_r/score, zero setup code.
4. **SignalMatrix mixed long+short**: rows where one bar emits long and another short pass validation; setup codes are drawn from the correct namespace per side.
5. **side_mode=long_only** — synthetic features satisfying short conditions never produce a `side=-1` row.
6. **side_mode=short_only** — synthetic features satisfying long conditions never produce a `side=+1` row.
7. **side_mode=both** — synthetic features can produce either side on different bars in the same run.
8. **Adapter — short accepted** when `side=-1` and stop/target_r are valid: produces a `TradeIntent` with `side=-1`, regardless of execution `allow_short`.
9. **Adapter — invalid_side bookkeeping** unchanged when `side ∉ {LONG, SHORT}`.
10. **Execution — short rejected when `allow_short=false`** (already tested for materialization; Phase19 adds a Layer1-level integration test that uses a Phase19 strategy YAML).
11. **Execution — short accepted/materialized when `allow_short=true`** (synthetic, Phase19-level).
12. **Long stop geometry**: long entry stops are strictly below close.
13. **Short stop geometry**: short entry stops are strictly above close.
14. **Missing-feature ConfigError on short branch**: a strategy with `side_mode != long_only` whose short branch requires a feature that is absent raises `ConfigError` (not silent skip).
15. **No-lookahead on short branch**: perturbing future bars/features does not change signals at `t` for either side.
16. **Session reset on short branch**: short-branch rolling state resets at `session_id` boundaries.
17. **Deterministic signal hash with side_mode**: identical config + features yields identical `signal_hash` regardless of whether `side_mode` changes the configured branches.
18. **Backward compatibility**: any current-10 strategy still passes its existing unit tests; no behavior change.

Tests 1–7 belong to `tests/unit/test_phase19_side_support_contract.py`. Tests 8–11 belong to `tests/unit/test_phase19_signal_adapter_short_support.py`. Tests 12–17 attach to per-strategy `tests/unit/test_phase19_brooks_strategy_signals.py`. Test 18 is a regression umbrella covered by existing Phase18B/C/D test suites continuing to pass.

## 12. Current-10 backward compatibility plan

- No existing strategy source file is modified by Phase19 design or implementation. Strategy source changes are confined to new Phase19 files.
- No existing strategy YAML is modified. Phase19 YAMLs live under new directories (`configs/strategies/base/phase19/`, `configs/strategies/grids/phase19/`, `configs/strategies/metadata/phase19/`, `configs/layer1/phase19_brooks_pa_grid_inspect/`).
- `validate_signal_matrix` is the only shared contract function that will be extended by Phase19 implementation. The extension MUST preserve current long-only assertions byte-for-byte when only long entries are present.
- `build_trade_intents_from_signals` is the only shared adapter function that will be extended. The extension MUST preserve all current `skip_reasons` semantics; only `invalid_side` becomes side-aware (LONG and SHORT both accepted, anything else stays `invalid_side`).
- `configs/execution/intraday_default.yaml` is not touched.
- `register_builtin_strategies()` is appended to, never reordered.

## 13. Non-goals for Phase19A

- No Layer2 router behavior, no priority-with-regime-permissions logic, no portfolio sizing.
- No conflict resolution between long and short signals from the same strategy on the same bar (Phase19 strategies must design their long/short setups to be mutually exclusive on any given bar; if both fire, the strategy emits the higher-score side).
- No execution truth change (no new `RejectReason`, no new exit semantics).
- No management overlays (no scale-out, trailing stops, no-followthrough — these are Layer2/management overlays).
- No promotion, no candidate YAML, no select-dry-run, no WFO, no live, no paper.
- No expansion of side support to current-10 strategies. Phase19 explicitly does not retrofit short branches onto current-10 in this design.

## 14. Open items deferred to future phases (not Phase19)

- A shared `configs/execution/intraday_default_short_enabled.yaml` for systematic short research. Phase19 implementation MAY add this file under explicit user/Codex approval; the design does not commit to it.
- A formal `LayerFlow` documentation update describing the side-aware SignalMatrix convention. Phase19 implementation should add a one-paragraph note in `docs/STRATEGY_CONTRACT.md` (or a Phase19 addendum) once the validator is extended; the design does not require contract doc edits in this phase.
- Long/short conflict policy for portfolio-level routing. That is Layer2 work.

## 15. Summary

Phase19A is the minimal, system-wide, contract-aligned uplift that makes `side=-1` representable in `SignalMatrix`, accepted by the adapter, and round-tripped through execution under `allow_short=true`. It is not a PA-specific feature, does not change current-10 behavior, and does not introduce a second PnL truth. It is the prerequisite for the Phase19 Brooks PA strategies 11-20 design (Phase19C).
