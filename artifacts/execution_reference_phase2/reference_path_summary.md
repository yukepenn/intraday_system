# Reference path summary

`simulate_trade_path_reference` walks forward from `entry_bar` within the entry session only.

**Per bar ordering**

1. Intrabar stop/target using high/low vs triggers.
2. Both touched: `stop_first` / `conservative` → STOP; `target_first` → TARGET.
3. Else if `minute >= eod_exit_minute` → EOD at close.
4. Else if `bars_held >= max_hold` → MAX_HOLD at close.

**Session roll**: if index hits first bar of the next session, exit previous bar’s close as **EOD**.

**Truncated window**: if loop exhausts bars in-session without exit, exit last bar close as **EOD**.

**Management**: non-`None` `management_plan` raises `IntradaySystemError`.

**Exit fill**: `apply_exit_slippage` on raw exit reference (stop/target price or session close).
