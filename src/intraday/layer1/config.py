"""Layer1 smoke YAML — runtime config for one-strategy plumbing checks."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.layer1.grid import grid_document_combo_count, load_grid_document

ExecutionMode = Literal["reference", "fast", "both"]


@dataclass(frozen=True)
class Layer1SmokeConfig:
    run_id: str
    description: str
    symbol: str
    asset: str
    timeframe: str
    start: str
    end: str
    data_root: str
    feature_config: str
    feature_use_cache: bool
    strategy_name: str
    strategy_config: str
    execution_config: str
    execution_mode: ExecutionMode
    max_trades_per_session: int
    skip_while_trade_open: bool
    count_rejected_intents: bool
    save_row_level_trades: bool
    artifact_root: str


def _req(d: Mapping[str, Any], key: str, where: str) -> Any:
    if key not in d:
        raise ConfigError(f"missing {key!r} in {where}")
    return d[key]


def _as_bool(v: Any, field: str) -> bool:
    if isinstance(v, bool):
        return v
    raise ConfigError(f"{field} must be bool, got {v!r}")


def load_layer1_smoke_config(path: Path | str) -> Layer1SmokeConfig:
    """Load Layer1 smoke config YAML."""
    raw = load_yaml(path)
    run_id = str(raw.get("run_id", "")).strip()
    if not run_id:
        raise ConfigError("run_id is required")
    data_root = _req(raw, "data", "layer1 smoke root")
    feat = _req(raw, "feature", "layer1 smoke root")
    strat = _req(raw, "strategy", "layer1 smoke root")
    exe = _req(raw, "execution", "layer1 smoke root")
    bt = _req(raw, "backtest", "layer1 smoke root")
    out = _req(raw, "output", "layer1 smoke root")

    if not isinstance(data_root, Mapping):
        raise ConfigError("data must be a mapping")
    if not isinstance(feat, Mapping):
        raise ConfigError("feature must be a mapping")
    if not isinstance(strat, Mapping):
        raise ConfigError("strategy must be a mapping")
    if not isinstance(exe, Mapping):
        raise ConfigError("execution must be a mapping")
    if not isinstance(bt, Mapping):
        raise ConfigError("backtest must be a mapping")
    if not isinstance(out, Mapping):
        raise ConfigError("output must be a mapping")

    mode_raw = str(exe.get("mode", "reference")).lower()
    if mode_raw not in ("reference", "fast", "both"):
        raise ConfigError(f"execution.mode must be reference|fast|both, got {mode_raw!r}")

    save_rows = bt.get("save_row_level_trades", False)
    save_rows_b = _as_bool(save_rows, "backtest.save_row_level_trades")
    if save_rows_b:
        raise ConfigError("Phase 6 smoke requires backtest.save_row_level_trades=false")

    mts = int(bt.get("max_trades_per_session", 1))
    if mts <= 0:
        raise ConfigError("backtest.max_trades_per_session must be > 0")

    art = str(out.get("artifact_root", "")).strip()
    if not art:
        raise ConfigError("output.artifact_root required")
    if Path(art).is_absolute():
        raise ConfigError("output.artifact_root must be a relative repo path")

    return Layer1SmokeConfig(
        run_id=run_id,
        description=str(raw.get("description", "")),
        symbol=str(_req(raw, "symbol", "layer1 smoke root")),
        asset=str(raw.get("asset", "equity")),
        timeframe=str(raw.get("timeframe", "1m")),
        start=str(_req(raw, "start", "layer1 smoke root")),
        end=str(_req(raw, "end", "layer1 smoke root")),
        data_root=str(data_root.get("data_root", "data/curated/bars_1m_rth")),
        feature_config=str(_req(feat, "config", "feature")),
        feature_use_cache=_as_bool(feat.get("use_cache", False), "feature.use_cache"),
        strategy_name=str(_req(strat, "name", "strategy")),
        strategy_config=str(_req(strat, "config", "strategy")),
        execution_config=str(_req(exe, "config", "execution")),
        execution_mode=mode_raw,  # type: ignore[assignment]
        max_trades_per_session=mts,
        skip_while_trade_open=_as_bool(
            bt.get("skip_while_trade_open", True), "backtest.skip_while_trade_open"
        ),
        count_rejected_intents=_as_bool(
            bt.get("count_rejected_intents", True), "backtest.count_rejected_intents"
        ),
        save_row_level_trades=save_rows_b,
        artifact_root=art,
    )


def validate_layer1_smoke_config(config: Layer1SmokeConfig) -> None:
    """Validate paths against repo root (existence checks)."""
    root = repo_root()

    def resolve(rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (root / p)

    for label, rel in (
        ("feature.config", config.feature_config),
        ("strategy.config", config.strategy_config),
        ("execution.config", config.execution_config),
    ):
        p = resolve(rel)
        if not p.is_file():
            raise ConfigError(f"{label} not found: {p}")

    # ISO date smoke check (strict YYYY-MM-DD)
    for label, s in ("start", config.start), ("end", config.end):
        parts = s.split("-")
        if len(parts) != 3 or len(parts[0]) != 4:
            raise ConfigError(f"{label} must be YYYY-MM-DD, got {s!r}")
        try:
            int(parts[0])
            int(parts[1])
            int(parts[2])
        except ValueError as exc:
            raise ConfigError(f"{label} invalid date: {s!r}") from exc

    if config.strategy_name.strip() != config.strategy_name:
        raise ConfigError("strategy.name must not have leading/trailing whitespace")


MAX_CONTROLLED_GRID_COMBOS = 24


@dataclass(frozen=True)
class Layer1ControlledGridConfig:
    run_id: str
    description: str
    symbol: str
    asset: str
    timeframe: str
    start: str
    end: str
    data_root: str
    feature_config: str
    feature_use_cache: bool
    strategy_name: str
    strategy_base_config: str
    strategy_grid_path: str
    execution_config: str
    execution_mode: ExecutionMode
    max_trades_per_session: int
    skip_while_trade_open: bool
    count_rejected_intents: bool
    save_row_level_trades: bool
    grid_max_combos: int | None
    grid_allow_prefix_slicing: bool
    grid_require_no_fixed_grid_overlap: bool
    artifact_root: str


def load_layer1_controlled_grid_config(path: Path | str) -> Layer1ControlledGridConfig:
    """Load Layer1 controlled grid YAML (Phase 6b)."""
    raw = load_yaml(path)
    run_id = str(raw.get("run_id", "")).strip()
    if not run_id:
        raise ConfigError("run_id is required")
    data_root = _req(raw, "data", "layer1 controlled grid root")
    feat = _req(raw, "feature", "layer1 controlled grid root")
    strat = _req(raw, "strategy", "layer1 controlled grid root")
    exe = _req(raw, "execution", "layer1 controlled grid root")
    bt = _req(raw, "backtest", "layer1 controlled grid root")
    gsect = _req(raw, "grid", "layer1 controlled grid root")
    out = _req(raw, "output", "layer1 controlled grid root")

    if not isinstance(data_root, Mapping):
        raise ConfigError("data must be a mapping")
    if not isinstance(feat, Mapping):
        raise ConfigError("feature must be a mapping")
    if not isinstance(strat, Mapping):
        raise ConfigError("strategy must be a mapping")
    if not isinstance(exe, Mapping):
        raise ConfigError("execution must be a mapping")
    if not isinstance(bt, Mapping):
        raise ConfigError("backtest must be a mapping")
    if not isinstance(gsect, Mapping):
        raise ConfigError("grid must be a mapping")
    if not isinstance(out, Mapping):
        raise ConfigError("output must be a mapping")

    mode_raw = str(exe.get("mode", "reference")).lower()
    if mode_raw not in ("reference", "fast", "both"):
        raise ConfigError(f"execution.mode must be reference|fast|both, got {mode_raw!r}")

    save_rows = bt.get("save_row_level_trades", False)
    save_rows_b = _as_bool(save_rows, "backtest.save_row_level_trades")
    if save_rows_b:
        raise ConfigError("controlled grid requires backtest.save_row_level_trades=false")

    mts = int(bt.get("max_trades_per_session", 1))
    if mts <= 0:
        raise ConfigError("backtest.max_trades_per_session must be > 0")

    art = str(out.get("artifact_root", "")).strip()
    if not art:
        raise ConfigError("output.artifact_root required")
    if Path(art).is_absolute():
        raise ConfigError("output.artifact_root must be a relative repo path")

    allow_slice = gsect.get("allow_prefix_slicing", False)
    allow_slice_b = _as_bool(allow_slice, "grid.allow_prefix_slicing")
    if allow_slice_b:
        raise ConfigError("controlled grid forbids grid.allow_prefix_slicing=true")

    req_overlap = gsect.get("require_no_fixed_grid_overlap", True)
    req_overlap_b = _as_bool(req_overlap, "grid.require_no_fixed_grid_overlap")
    if not req_overlap_b:
        raise ConfigError("grid.require_no_fixed_grid_overlap must be true for Phase 6b")

    max_c = gsect.get("max_combos", None)
    grid_max: int | None
    if max_c is None:
        grid_max = None
    else:
        grid_max = int(max_c)
        if grid_max <= 0:
            raise ConfigError("grid.max_combos must be null or > 0")

    return Layer1ControlledGridConfig(
        run_id=run_id,
        description=str(raw.get("description", "")),
        symbol=str(_req(raw, "symbol", "layer1 controlled grid root")),
        asset=str(raw.get("asset", "equity")),
        timeframe=str(raw.get("timeframe", "1m")),
        start=str(_req(raw, "start", "layer1 controlled grid root")),
        end=str(_req(raw, "end", "layer1 controlled grid root")),
        data_root=str(data_root.get("data_root", "data/curated/bars_1m_rth")),
        feature_config=str(_req(feat, "config", "feature")),
        feature_use_cache=_as_bool(feat.get("use_cache", False), "feature.use_cache"),
        strategy_name=str(_req(strat, "name", "strategy")),
        strategy_base_config=str(_req(strat, "base_config", "strategy")),
        strategy_grid_path=str(_req(strat, "grid", "strategy")),
        execution_config=str(_req(exe, "config", "execution")),
        execution_mode=mode_raw,  # type: ignore[assignment]
        max_trades_per_session=mts,
        skip_while_trade_open=_as_bool(
            bt.get("skip_while_trade_open", True), "backtest.skip_while_trade_open"
        ),
        count_rejected_intents=_as_bool(
            bt.get("count_rejected_intents", True), "backtest.count_rejected_intents"
        ),
        save_row_level_trades=save_rows_b,
        grid_max_combos=grid_max,
        grid_allow_prefix_slicing=allow_slice_b,
        grid_require_no_fixed_grid_overlap=req_overlap_b,
        artifact_root=art,
    )


def validate_layer1_controlled_grid_config(config: Layer1ControlledGridConfig) -> None:
    """Validate paths, dates, and grid combo bounds."""
    root = repo_root()

    def resolve(rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (root / p)

    for label, rel in (
        ("feature.config", config.feature_config),
        ("strategy.base_config", config.strategy_base_config),
        ("strategy.grid", config.strategy_grid_path),
        ("execution.config", config.execution_config),
    ):
        p = resolve(rel)
        if not p.is_file():
            raise ConfigError(f"{label} not found: {p}")

    for label, s in ("start", config.start), ("end", config.end):
        parts = s.split("-")
        if len(parts) != 3 or len(parts[0]) != 4:
            raise ConfigError(f"{label} must be YYYY-MM-DD, got {s!r}")
        try:
            int(parts[0])
            int(parts[1])
            int(parts[2])
        except ValueError as exc:
            raise ConfigError(f"{label} invalid date: {s!r}") from exc

    if config.strategy_name.strip() != config.strategy_name:
        raise ConfigError("strategy.name must not have leading/trailing whitespace")

    gpath = resolve(config.strategy_grid_path)
    gdoc = load_grid_document(gpath)
    doc_strategy = str(gdoc.get("strategy", "")).strip()
    if doc_strategy and doc_strategy != config.strategy_name:
        raise ConfigError(
            f"grid YAML strategy {doc_strategy!r} must match config strategy.name "
            f"{config.strategy_name!r}"
        )
    gbase = str(gdoc.get("base_config", "")).strip()
    if gbase != config.strategy_base_config:
        raise ConfigError(
            "strategy.base_config must match grid document base_config "
            f"(config {config.strategy_base_config!r} vs grid {gbase!r})"
        )
    try:
        n = grid_document_combo_count(gdoc)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"invalid grid document: {exc}") from exc
    if n > MAX_CONTROLLED_GRID_COMBOS:
        raise ConfigError(
            f"grid has {n} combos; Phase 6b allows at most {MAX_CONTROLLED_GRID_COMBOS}"
        )
    if config.grid_max_combos is not None and n > config.grid_max_combos:
        raise ConfigError(f"grid has {n} combos; exceeds grid.max_combos={config.grid_max_combos}")
