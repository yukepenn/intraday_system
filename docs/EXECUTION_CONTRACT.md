# EXECUTION_CONTRACT — intraday_system

Execution is the only PnL accounting truth. Strategies never compute PnL.

## 1. Truth rule

`src/intraday/execution/reference.py` defines the canonical fill / stop / target / EOD / max-hold / R-multiple semantics. The `simulate_trade_path_reference` function is the single source of truth for what a trade is and what its PnL is.

`src/intraday/execution/fast.py` provides **`simulate_trade_path_fast`**, a Numba-accelerated mirror for the **same** `TradeIntent` + `BarMatrix` + `ExecutionSpec` → `TradeResult` contract. It uses the **same** `materialize_trade` implementation as reference, then a Numba kernel for the post-entry scan. **Fast output is not a second accounting truth**; it is valid research acceleration **only where parity tests pass** (`tests/parity/test_execution_fast_parity.py`).

## 2. ExecutionSpec (canonical fields)

```python
@dataclass(frozen=True)
class ExecutionSpec:
    entry_timing: Literal["next_open"]
    same_bar_policy: Literal["stop_first", "target_first", "conservative"]
    slippage_per_share: float
    commission_per_trade: float
    min_risk_per_share: float
    eod_exit_minute: int        # 0..389 for US equity RTH 1-min
    allow_short: bool
    max_hold_bars_default: int | None
    semantics_version: str      # e.g. "execution_v1"
```

- `entry_timing` must be `next_open` (other values are rejected at config validation).
- `same_bar_policy`: `conservative` is defined to match **`stop_first`** (stop wins when both stop and target are touched on the same bar).
- `eod_exit_minute` is inclusive: if the entry bar’s `minute == eod_exit_minute`, the trade may still **EOD-exit on that bar** after intrabar stop/target checks if neither fired.
- `max_hold_bars_default`: `None` means “no default cap”; otherwise must be `>= 1`.
- `allow_short` is parsed with safe bool-like coercion (YAML booleans and common strings); unsafe string truthiness is avoided.
- Strategy YAML never enables short execution. Strategy `signal.side_mode`
  controls signal/intent eligibility only; `ExecutionSpec.allow_short` remains
  the final execution authority.

Default values live in `configs/execution/intraday_default.yaml`. Use `ExecutionSpec.from_config` / `load_execution_spec` for validated construction.

## 3. TradeIntent

```python
@dataclass(frozen=True)
class TradeIntent:
    candidate_id: int
    signal_bar: int
    side: int                    # Side.LONG=+1, Side.SHORT=-1
    qty: float
    raw_stop_price: float
    target_r: float
    max_hold_bars: int           # 0 = use ExecutionSpec.max_hold_bars_default
    score: float
    setup_code: int
```

**Pre-trade validation** (deterministic rejects):

- `signal_bar` must satisfy `0 <= signal_bar < n_bars`; else `RejectReason.INVALID_INTENT`.
- `side` must be `LONG` or `SHORT`; else `INVALID_INTENT`.
- `qty` must be finite and `> 0`; else `INVALID_INTENT`.
- `target_r` must be finite and `> 0`; else `INVALID_INTENT`.
- `raw_stop_price` must be finite; else `INVALID_STOP` (non-finite stop is not a valid risk anchor).

Strategies emit `TradeIntent`s (one per fired signal bar). Execution consumes them.
The signal adapter should pass structurally valid short intents when
`signal.side_mode` allows them; it must not preemptively suppress shorts solely
because an execution config has `allow_short: false`.

## 4. TradeResult

```python
@dataclass(frozen=True)
class TradeResult:
    accepted: bool
    reject_reason: int           # RejectReason enum
    candidate_id: int
    signal_bar: int
    entry_bar: int
    exit_bar: int
    side: int
    qty: float
    entry_price: float
    stop_price: float
    target_price: float
    exit_price: float
    gross_pnl: float
    net_pnl: float
    r_multiple: float
    exit_reason: int             # ExitReason enum
    bars_held: int
```

**Rejected convention** (`TradeResult.rejected`):

- `accepted=False`
- `reject_reason` set; `exit_reason=ExitReason.REJECTED`
- `entry_bar=-1`, `exit_bar=-1`, `bars_held=0`
- price fields are **NaN**; `gross_pnl=net_pnl=r_multiple=0`

## 5. Phase 2 — Materialization (`materialize_trade`)

- **Next-open entry**: `entry_bar = signal_bar + 1`.
- **No next bar**: if `entry_bar >= n_bars` → `RejectReason.NO_NEXT_BAR`.
- **Cross-session entry**: if `session_id[entry_bar] != session_id[signal_bar]` → `CROSS_SESSION_ENTRY`.
- **Outside trading window**: if `minute[entry_bar] > eod_exit_minute` → `OUTSIDE_TRADING_WINDOW` (strict `>`; entry **on** the EOD minute is allowed).
- **Short guard**: `SHORT_NOT_ALLOWED` when `side==SHORT` and `allow_short` is false.
- **Entry price**: raw reference `open[entry_bar]` must be **finite**; else `RejectReason.INVALID_MARKET_DATA`. Otherwise **adverse entry slippage** — long: `+slippage_per_share`, short: `-slippage_per_share`.
- **Stop / risk**: `stop_price = raw_stop_price`. Long requires `stop < entry`; short requires `stop > entry`. `risk_per_share = |entry - stop|` in the profitable-stop direction. If `risk_per_share <= 0` → `INVALID_STOP`. If `risk_per_share < min_risk_per_share` → `RISK_TOO_SMALL`.
- **Target**: `target_r` must be `> 0` (intent validation). `target_price = entry +/- target_r * risk_per_share` (long `+`, short `-`). Targets are **never** computed outside execution.
- **Max hold**: if `intent.max_hold_bars > 0`, use it; else if `spec.max_hold_bars_default` is not `None`, use that; else **no** max-hold cap. **Definition**: `bars_held = exit_bar - entry_bar + 1`. `max_hold_bars == 1` allows exit at the **close of the entry bar** if no stop/target/EOD fired first on that bar’s ordering.

## 6. Phase 2 — Reference path (`simulate_trade_path_reference`)

**Truth rule:** `simulate_trade_path_reference` remains the canonical specification of post-entry behavior. The fast path must parity-match it on all covered scenarios.

**Management**: `management_plan` must be `None`. A non-`None` value raises `IntradaySystemError` (Phase 2 does not implement overlays). The fast wrapper uses the **same** error class and message.

**Session rule**: simulation only walks bars with `session_id == session_id[entry_bar]`. If the index advances into a **new session** while the trade is still open, the engine exits at the **prior bar’s close** with `ExitReason.EOD` (session roll / defensive close). The prior bar’s close must be finite; else `INVALID_MARKET_DATA`.

**Per-bar ordering** (same bar `i`):

1. Intrabar **stop** and **target** using `high[i]` / `low[i]` vs trigger levels. `high[i]` and `low[i]` must be finite; else `INVALID_MARKET_DATA` (rejected row convention).
2. If both touched: `stop_first` or `conservative` → **STOP**; `target_first` → **TARGET**.
3. Else if `minute[i] >= eod_exit_minute` → **EOD** at `close[i]` (after adverse exit slippage). `close[i]` must be finite; else `INVALID_MARKET_DATA`.
4. Else if max-hold active and `bars_held >= max_hold_bars` → **MAX_HOLD** at `close[i]` (finite `close` required).
5. Else continue.

**EOD vs max-hold**: on the same bar, **EOD is evaluated before max-hold**; if both would apply, **EOD wins**.

**Touch definitions**:

- Long: stop if `low <= stop_price`; target if `high >= target_price`.
- Short: stop if `high >= stop_price`; target if `low <= target_price`.

**Exit slippage** (adverse): long exit `raw_exit - slippage_per_share`; short exit `raw_exit + slippage_per_share`. Applies to STOP, TARGET, EOD, MAX_HOLD, and session-roll exits. Raw exit price must be finite before slippage; otherwise `INVALID_MARKET_DATA`.

**Truncated data / end of window**: if the scan reaches the end of the `BarMatrix` while still in the entry session without a prior exit, exit at the **last available bar’s close** with `ExitReason.EOD` (defensive fallback). Non-finite last close → `INVALID_MARKET_DATA`.

## 7. Costs and R-multiple

- `gross_pnl = side * (exit_price - entry_price) * qty` with `side ∈ {+1,-1}`.
- `net_pnl = gross_pnl - commission_per_trade` (fixed per completed trade).
- `r_multiple = net_pnl / (risk_per_share * qty)` (uses **net** PnL so commission and slippage flow into R).

Helpers live in `src/intraday/execution/cost.py`.

## 8. Fast path (Phase 3)

- **Active API:** `simulate_trade_path_fast` returns `TradeResult` with the same materialization and post-entry semantics as reference on the Phase 2 fixed-R single-trade surface.
- **Implementation:** shared `materialize_trade`; `@njit(cache=True)` kernel `_simulate_trade_path_fast_kernel` on packed NumPy slices (`high`/`low`/`close`/`session_id`/`minute`).
- **Unsupported in Phase 3:** batch `simulate_trade_paths_fast` (still raises `IntradaySystemError`); any `management_plan` overlay; strategy or Layer1/2/3 logic.

**Supported fast semantics (must match reference):** next-open entry (via shared materializer), cross-session entry rejection, stop/target/EOD/max-hold ordering, same-bar policies (`conservative` = `stop_first` for both touched), min-risk rejection, slippage and commission, fixed-R target from actual (slippaged) entry, long and short when `allow_short`, session roll and truncated-window EOD fallback, deterministic rejects including `INVALID_MARKET_DATA` for non-finite required prices during materialization or scan.

**Unsupported semantics (not in execution fast path):** scale-out, trailing, no-followthrough, portfolio sizing, router decisions, multi-intent batch simulation.

## 9. Parity rule

Every covered execution behavior has a synthetic parity test: `tests/parity/test_execution_fast_parity.py`. Helpers: `src/intraday/execution/parity.py` (`compare_trade_results`, `assert_trade_results_equal`). **Do not treat fast output as valid for research if these tests fail or are bypassed.**

## 10. Ownership boundaries

Execution **does not**:

- Generate signals.
- Read strategy configs (consumes `ExecutionSpec` + `TradeIntent` only).
- Apply portfolio sizing (Layer2 / portfolio).
- Apply daily risk state (Layer2 / portfolio).
- Resolve conflicts between candidates (Layer2).
- Apply **management overlays** (scale-out, trailing, no-followthrough) in reference or fast single-trade paths.

Strategies **do not**:

- Compute PnL.
- Apply slippage or commission.
- Decide entries beyond `signal_bar` (next-bar entry is execution’s job).

## 11. Semantics versioning

`semantics_version` (e.g. `"execution_v1"`) participates in `execution_spec_hash`. Any change to fill semantics increments this version. Cached candidate metrics built against an older hash are invalidated by hash mismatch.

## 12. RejectReason extensions

- `INVALID_INTENT` — invalid `signal_bar` OOB, `side` not long/short, non-finite or `<= 0` `qty`, or non-finite or `<= 0` `target_r`.
- `INVALID_MARKET_DATA` — non-finite `open[entry_bar]` at materialization, or non-finite `high`/`low`/`close` on a bar when that value is required for the reference scan / finalize path.

## 13. Forbidden

- A second PnL truth (any other module computing fills or R-multiples for research truth).
- Dollar fill semantics inside strategies or data loaders.
- Fast engine output replacing reference output without parity coverage.
