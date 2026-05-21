# Setup-Code Registry

This document is the governance policy for strategy setup codes. The
authoritative runtime registry lives in
`src/intraday/strategies/setup_codes.py`.

## Purpose

- Setup codes are **stable audit identifiers** for the strategy/side that
  produced a signal.
- Setup codes are **not** optimization parameters.
- Setup codes are **not** grid axes.
- Setup codes must **not drift** after a design has been accepted.

## Scope

- Every built-in strategy has a `SetupCodeSpec` in the runtime registry.
- The spec exposes `long_code` and (optionally) `short_code`.
- Long and short codes are **side-specific**. A strategy may emit only the
  setup code assigned to the side it actually emits.
- Long stops are `< reference_close`, short stops are `> reference_close`. The
  setup code identifies the side and the strategy; it does not encode price or
  R semantics.

## Sources of truth and audit surfaces

| Layer                                      | Role                  |
|--------------------------------------------|-----------------------|
| `src/intraday/strategies/setup_codes.py`   | Runtime source of truth |
| `StrategyDef.setup_code_long/short`         | Mirrors registry      |
| Strategy module constants (e.g. `SETUP_CODE_LONG`) | Imported from registry |
| Strategy metadata YAML `setup_codes`        | Mirrors registry (audit) |
| CSV/MD review artifacts                     | Mirrors registry (audit) |

Runtime code must **not** read CSV/MD artifacts. CSV/MD artifacts must be
regenerated from the runtime registry when codes are added or revised.

## Approved registry (Phase19 immediate fix)

### Current-10

| Strategy                      | Long  | Short |
|-------------------------------|-------|-------|
| pa_buy_sell_close_trend       | 1001  | 8001  |
| orb_continuation              | 2001  | 9001  |
| orb_retest_continuation       | 2002  | 9002  |
| failed_orb                    | 2003  | 9003  |
| gap_acceptance_failure        | 3001  | 10001 |
| vwap_trend_pullback           | 4001  | 11001 |
| vwap_reclaim_reject           | 4002  | 11002 |
| prior_day_level_trap          | 5001  | 12001 |
| cci_extreme_snapback          | 6001  | 13001 |
| stochastic_oversold_cross     | 6002  | 13002 |

The long codes are historical and unchanged. The short codes are introduced by
the Phase19 immediate fix for the current-10 side-aware retrofit. A current-10
strategy emits the short code only when its configured `signal.side_mode`
explicitly permits short.

### Phase19 core strategies 11-17

| Strategy                            | Long | Short |
|-------------------------------------|------|-------|
| pa_second_entry_pullback            | 7101 | 7201  |
| pa_trading_range_bls_hs             | 7102 | 7202  |
| pa_failed_breakout_trap             | 7103 | 7203  |
| pa_opening_reversal_sr              | 7104 | 7204  |
| pa_breakout_pullback_continuation   | 7105 | 7205  |
| pa_tight_channel_pullback           | 7106 | 7206  |
| pa_broad_channel_zone               | 7107 | 7207  |

The Phase19B implementation initially shipped with placeholder codes
`1101/1102` through `1701/1702`. Those values are **rejected** going forward.
Source, configs, metadata, and current artifacts have been repaired to the
accepted Phase19 codes above.

### Phase19 diagnostic strategies 18-20 (reserved, not implemented)

| Strategy                            | Long | Short |
|-------------------------------------|------|-------|
| pa_mtr_reversal_diagnostic          | 7108 | 7208  |
| pa_wedge_reversal_diagnostic        | 7109 | 7209  |
| pa_climax_reversal_diagnostic       | 7110 | 7210  |

### Future reservations (not yet assigned to strategy names)

| Range          | Long      | Short      |
|----------------|-----------|------------|
| strategies 21-30 | 7301-7310 | 7401-7410 |
| strategies 31-40 | 7501-7510 | 7601-7610 |
| strategies 41-50 | 7701-7710 | 7801-7810 |

## Governance rules

1. Codes are int16. The registry validates this at import time and fails fast.
2. Codes are globally unique across long and short. The registry validates this
   at import time.
3. A strategy may emit only the side(s) permitted by its configured
   `signal.side_mode`. Execution remains the final authority on whether a side
   is allowed to fill (see `EXECUTION_CONTRACT.md`).
4. New strategies must reserve their code range in this document **before**
   implementation begins.
5. Strategy module constants (e.g. `SETUP_CODE_LONG`, `SETUP_CODE_SHORT`) must
   be imported from the registry, not redeclared.
6. Metadata YAMLs must mirror the registry under a `setup_codes:` mapping with
   `long:` and (optionally) `short:` keys.
7. CSV/MD review artifacts must mirror the registry; if the registry changes,
   the artifacts must be regenerated, not the runtime read back from them.
