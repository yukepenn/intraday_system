"""CLI commands for the Phase 5 strategy signal layer."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from intraday.core.paths import repo_root
from intraday.data.loader import load_bars_from_curated
from intraday.features.engine import build_feature_matrix
from intraday.features.specs import load_feature_config
from intraday.strategies.loader import (
    load_strategy_config,
    resolve_strategy_config,
    validate_strategy_config,
)
from intraday.strategies.pa.buy_sell_close_trend import PA_REQUIRED_FEATURE_COLUMNS
from intraday.strategies.registry import get_strategy, list_strategies, register_builtin_strategies


def cmd_strategies_list() -> int:
    register_builtin_strategies()
    print(json.dumps({"strategies": list_strategies()}, indent=2))
    return 0


def cmd_strategies_inspect(*, strategy: str, config: str) -> int:
    root = repo_root()
    register_builtin_strategies()
    defn = get_strategy(strategy)
    cfg_path = Path(config)
    if not cfg_path.is_absolute():
        cfg_path = root / cfg_path
    cfg = resolve_strategy_config(cfg_path)
    validate_strategy_config(strategy, cfg)
    meta_path = root / "configs/strategies/metadata" / f"{strategy}.yaml"
    setup_codes: dict[str, int] = {}
    if meta_path.exists():
        meta = load_strategy_config(meta_path)
        setup_codes = {str(k): v for k, v in (meta.get("setup_codes") or {}).items()}
    print(
        json.dumps(
            {
                "strategy": defn.name,
                "family": defn.family,
                "version": defn.version,
                "required_feature_set": defn.required_feature_set,
                "signal_contract_version": defn.signal_contract_version,
                "signal_side": (cfg.get("signal") or {}).get("side"),
                "setup_codes": setup_codes,
                "required_feature_columns": list(PA_REQUIRED_FEATURE_COLUMNS)
                if strategy == "pa_buy_sell_close_trend"
                else [],
            },
            indent=2,
        )
    )
    return 0


def cmd_strategies_generate_smoke(
    *,
    strategy: str,
    config: str,
    feature_config: str,
    symbol: str,
    start: str,
    end: str,
    data_root: str,
) -> int:
    root = repo_root()
    register_builtin_strategies()
    defn = get_strategy(strategy)

    cfg_path = Path(config)
    if not cfg_path.is_absolute():
        cfg_path = root / cfg_path
    strat_cfg = resolve_strategy_config(cfg_path)
    validate_strategy_config(strategy, strat_cfg)

    feat_path = Path(feature_config)
    if not feat_path.is_absolute():
        feat_path = root / feat_path
    feat_raw = load_feature_config(feat_path)

    droot = Path(data_root)
    if not droot.is_absolute():
        droot = root / droot

    bars = load_bars_from_curated(symbol, start, end, data_root=str(droot), base=root)
    features = build_feature_matrix(bars, feat_raw, store=None, use_cache=False, mode="reference")
    signals = defn.generate_reference(bars, features, strat_cfg)

    entry = np.asarray(signals.entry, dtype=bool)
    n_entry = int(entry.sum())
    out: dict[str, object] = {
        "rows": signals.n_bars,
        "feature_columns": features.n_columns,
        "feature_hash": features.feature_hash,
        "signal_hash": signals.signal_hash,
        "entry_count": n_entry,
        "entry_rate": float(n_entry / signals.n_bars) if signals.n_bars else 0.0,
        "cache_used": False,
    }
    if n_entry:
        idx = np.flatnonzero(entry)
        out["first_entry_bar"] = int(idx[0])
        out["last_entry_bar"] = int(idx[-1])
        out["first_entry_minute"] = int(bars.minute[idx[0]])
        out["last_entry_minute"] = int(bars.minute[idx[-1]])
        out["target_r_min"] = float(np.nanmin(signals.target_r[entry]))
        out["target_r_max"] = float(np.nanmax(signals.target_r[entry]))
        out["score_min"] = float(np.nanmin(signals.score[entry]))
        out["score_max"] = float(np.nanmax(signals.score[entry]))
        codes, counts = np.unique(signals.setup_code[entry], return_counts=True)
        out["setup_code_distribution"] = {
            int(c): int(n) for c, n in zip(codes, counts, strict=True)
        }
        out["nan_stop_on_entry"] = int(np.isnan(signals.stop[entry]).sum())
        out["invalid_stop_on_entry"] = int((signals.stop[entry] >= bars.close[entry]).sum())
    print(json.dumps(out, indent=2))
    return 0
