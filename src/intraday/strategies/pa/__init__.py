"""PA (price-action) strategy family."""

from intraday.strategies.pa.buy_sell_close_trend import (
    PA_BUY_SELL_CLOSE_TREND_DEF,
    generate_pa_buy_sell_close_trend_signals,
)

__all__ = [
    "PA_BUY_SELL_CLOSE_TREND_DEF",
    "generate_pa_buy_sell_close_trend_signals",
]
