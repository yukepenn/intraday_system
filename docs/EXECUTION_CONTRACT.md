# EXECUTION_CONTRACT — intraday_system

Execution is the only PnL accounting truth. Strategies never compute PnL.

## 1. Truth rule

`src/intraday/execution/reference.py` defines the canonical fill / stop / target / EOD / max-hold / R-multiple semantics. The `simulate_trade_path_reference` function is the single source of truth for what a trade is and what its PnL is.

`src/intraday/execution/fast.py` is the Numba-accelerated mirror. It must parity-match the reference engine on every covered scenario. A parity gap is a bug.

## 2. ExecutionSpec (canonical fields)

```python
@dataclass(frozen=True)
class ExecutionSpec:
    entry_timing: Literal["next_open"]
    same_bar_policy: Literal["stop_first", "target_first", "conservative"]
    slippage_per_share: float
    commission_per_trade: float
    min_risk_per_share: float
    eod_exit_minute: int        # 0..389 for US equity RTH
    allow_short: bool
    max_hold_bars_default: int | None
    semantics_version: str      # e.g. "execution_v1"
```

Default values live in `configs/execution/intraday_default.yaml`.

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
    max_hold_bars: int
    score: float
    setup_code: int
```

Strategies emit `TradeIntent`s (one per fired signal bar). Execution consumes them.

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

## 5. Reference path responsibilities

The reference engine owns:

- **Next-bar entry** (`entry_timing=next_open`).
- **Session-boundary guard**: never enter on the last bar of a session; never carry across sessions.
- **Entry slippage** (`slippage_per_share` applied per side).
- **Stop materialization** from `raw_stop_price` + `min_risk_per_share` validation.
- **Risk validation**: if `|entry - stop| < min_risk_per_share`, reject with `RISK_TOO_SMALL`.
- **Target materialization** from actual entry price + `target_r * risk`.
- **Same-bar policy** when both stop and target hit on the same bar.
- **EOD exit** at `eod_exit_minute` (and never beyond it).
- **Max-hold exit** after `max_hold_bars` from entry.
- **Stop/target ordering** by bar index.
- **Scale-out events** (when ManagementPlan provides scale-outs).
- **Trailing stop events** (ditto).
- **No-followthrough exits** (ditto).
- **Commission / slippage** applied to gross PnL.
- **R-multiple** computed from realized PnL ÷ risked dollars.
- **Reject reasons** populated per `RejectReason`.

## 6. Fast path

Same responsibilities as reference, implemented as Numba kernels operating on flat NumPy arrays (`open`, `high`, `low`, `close`, `session_id`, `minute`, packed intents, packed spec).

## 7. Parity rule

Every execution behavior must have a parity test in `tests/parity/test_execution_fast_parity.py`. Scenarios:

- Normal target hit.
- Normal stop hit.
- Same-bar stop/target (per `same_bar_policy`).
- EOD exit.
- Max-hold exit.
- Risk too small (reject).
- Cross-session entry attempt (reject).
- Long trade.
- Short trade (when `allow_short=true`).
- Scale-out 50% then 50% of remaining.
- Trailing stop.
- No-followthrough.
- Commission + slippage applied correctly.

## 8. Ownership boundaries

Execution **does not**:

- Generate signals.
- Read strategy configs (consumes `ExecutionSpec` + `TradeIntent` + `ManagementPlan` only).
- Apply portfolio sizing (Layer2 / portfolio).
- Apply daily risk state (Layer2 / portfolio).
- Resolve conflicts between candidates (Layer2).

Strategies **do not**:

- Compute PnL.
- Apply slippage or commission.
- Decide entries beyond `signal_bar` (next-bar entry is execution's job).

## 9. Semantics versioning

`semantics_version` (e.g. `"execution_v1"`) participates in `execution_spec_hash`. Any change to fill semantics increments this version. Cached candidate metrics built against an older `execution_v0` are invalidated by hash mismatch.

## 10. Forbidden

- A second PnL truth (any other module computing fills or R-multiples).
- Dollar amounts inside strategies.
- Fast engine output replacing reference output without parity coverage.
