"""Phase19 polish doc/config consistency guards."""

from __future__ import annotations

from pathlib import Path

from intraday.core.config import load_yaml
from intraday.strategies.registry import get_strategy, register_builtin_strategies
from intraday.strategies.setup_codes import SETUP_CODES

REPO = Path(__file__).resolve().parents[2]

CURRENT10 = (
    "pa_buy_sell_close_trend",
    "orb_continuation",
    "orb_retest_continuation",
    "failed_orb",
    "gap_acceptance_failure",
    "vwap_trend_pullback",
    "vwap_reclaim_reject",
    "prior_day_level_trap",
    "cci_extreme_snapback",
    "stochastic_oversold_cross",
)

PHASE19 = (
    "pa_second_entry_pullback",
    "pa_trading_range_bls_hs",
    "pa_failed_breakout_trap",
    "pa_opening_reversal_sr",
    "pa_breakout_pullback_continuation",
    "pa_tight_channel_pullback",
    "pa_broad_channel_zone",
)


def _text(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_phase_plan_current_next_step_not_stale_phase18() -> None:
    text = _text("docs/PHASE_PLAN.md")
    assert (
        "Current next step: **`IMPLEMENT_PHASE18_APPROVED_EXISTING_10_STRATEGY_IMPROVEMENTS`**"
        not in text
    )
    assert "PHASE19_IMMEDIATE_FIX_POLISH_RUNTIME_TESTS_AND_DOC_CONFIG_CONSISTENCY" in text


def test_normative_docs_reference_side_mode_and_setup_registry() -> None:
    assert "signal.side_mode" in _text("docs/CONFIG_CONTRACT.md")
    assert "legacy `signal.side: long_only`" in _text("docs/CONFIG_CONTRACT.md")
    assert "docs/SETUP_CODE_REGISTRY.md" in _text("docs/STRATEGY_CONTRACT.md")


def test_project_structure_lists_current_contract_docs() -> None:
    text = _text("docs/PROJECT_STRUCTURE.md")
    for name in (
        "FEATURE_CONTRACT.md",
        "STRATEGY_CONTRACT.md",
        "BACKTEST_CONTRACT.md",
        "LAYER1_CONTRACT.md",
        "LAYER1_CANDIDATE_SELECTION_CONTRACT.md",
        "STRATEGY_FAMILY_ONBOARDING_CONTRACT.md",
        "SETUP_CODE_REGISTRY.md",
    ):
        assert name in text


def test_layer2_layer3_readmes_do_not_claim_phase8_or_phase10_activation() -> None:
    assert "They land in Phase 8" not in _text("configs/layer2/README.md")
    assert "They land in Phase 10" not in _text("configs/layer3/README.md")


def test_new_strategy_configs_use_side_mode_not_legacy_side() -> None:
    for strategy in CURRENT10:
        cfg = load_yaml(REPO / "configs/strategies/base" / f"{strategy}.yaml")
        assert cfg["signal"].get("side_mode") == "long_only"
        assert "side" not in cfg["signal"]
    for strategy in PHASE19:
        cfg = load_yaml(REPO / "configs/strategies/base/phase19" / f"{strategy}.yaml")
        assert cfg["signal"].get("side_mode") == "long_only"
        assert "side" not in cfg["signal"]


def test_legacy_signal_side_limited_to_phase18b_configs() -> None:
    offenders: list[str] = []
    for path in (REPO / "configs").rglob("*.yaml"):
        rel = path.relative_to(REPO).as_posix()
        cfg = load_yaml(path)
        signal = cfg.get("signal") if isinstance(cfg, dict) else None
        if isinstance(signal, dict) and "side" in signal and "phase18b" not in rel:
            offenders.append(rel)
    assert offenders == []


def test_no_strategy_yaml_sets_execution_allow_short() -> None:
    offenders: list[str] = []
    for path in (REPO / "configs/strategies").rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        if "allow_short" in text:
            offenders.append(path.relative_to(REPO).as_posix())
    assert offenders == []


def test_metadata_setup_codes_match_runtime_registry() -> None:
    register_builtin_strategies()
    for strategy in (*CURRENT10, *PHASE19):
        meta_dir = (
            "configs/strategies/metadata/phase19"
            if strategy in PHASE19
            else "configs/strategies/metadata"
        )
        meta = load_yaml(REPO / meta_dir / f"{strategy}.yaml")
        spec = SETUP_CODES[strategy]
        defn = get_strategy(strategy)
        assert meta["setup_codes"]["long"] == spec.long_code == defn.setup_code_long
        assert meta["setup_codes"]["short"] == spec.short_code == defn.setup_code_short


def test_grids_do_not_grid_setup_codes() -> None:
    offenders: list[str] = []
    for path in (REPO / "configs/strategies/grids").rglob("*.yaml"):
        cfg = load_yaml(path)
        grid = cfg.get("grid") if isinstance(cfg, dict) else None
        fixed = cfg.get("fixed") if isinstance(cfg, dict) else None
        keys = [*(grid or {}).keys(), *(fixed or {}).keys()]
        if any("setup_code" in str(k) for k in keys):
            offenders.append(path.relative_to(REPO).as_posix())
    assert offenders == []


def test_side_aware_grids_are_inspect_only_no_economic_claims() -> None:
    grid_root = REPO / "configs/strategies/grids/phase19_immediate_fix_current10_side_aware"
    for path in grid_root.glob("*.yaml"):
        cfg = load_yaml(path)
        assert cfg["grid_inspect_only"] is True
        assert cfg["economic_claims_allowed"] is False


def test_phase19_layer1_configs_are_labeled_grid_inspect_only() -> None:
    roots = (
        REPO / "configs/layer1/phase19_brooks_pa_grid_inspect",
        REPO / "configs/layer1/phase19_immediate_fix_current10_side_aware_grid_inspect",
    )
    for root in roots:
        for path in root.glob("*.yaml"):
            text = path.read_text(encoding="utf-8").lower()
            assert "grid-inspect" in text
            assert "economic grid" in text
