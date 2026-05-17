"""Layer1 candidate-selection dry-run function tests."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.layer1.grid import load_grid_document, resolve_grid_combos
from intraday.layer1.selection import (
    DECISION_HOLD,
    DECISION_REJECT,
    run_layer1_candidate_selection_dry_run,
)

BASE = "configs/strategies/base/pa_buy_sell_close_trend.yaml"
GRID = "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"


def _write_synthetic_sweep(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "run_id",
        "combo_id",
        "config_hash",
        "params_json",
        "signal_entries",
        "valid_intents",
        "executed_results",
        "accepted_trades",
        "rejected_trades",
        "total_r",
        "avg_r",
        "median_r",
        "win_rate",
        "profit_factor_r",
        "max_drawdown_r",
        "avg_bars_held",
        "exit_reason_counts_json",
        "reject_reason_counts_json",
        "skip_reason_counts_json",
        "adapter_skip_reasons_json",
        "feature_hash",
        "signal_hash",
        "execution_mode",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def _combo_row(
    combo_id: str,
    *,
    total_r: float = 6.5,
    profit_factor_r: float = 1.14,
    max_drawdown_r: float = 5.7,
) -> dict[str, object]:
    root = repo_root()
    doc = load_grid_document(root / GRID)
    combos = {c.combo_id: c for c in resolve_grid_combos(doc)}
    combo = combos[combo_id]
    return {
        "run_id": "SYNTH_SWEEP",
        "combo_id": combo_id,
        "config_hash": combo.config_hash,
        "params_json": combo.params_json,
        "signal_entries": 4380,
        "accepted_trades": 124,
        "rejected_trades": 0,
        "total_r": total_r,
        "avg_r": 0.05,
        "median_r": 0.1,
        "win_rate": 0.52,
        "profit_factor_r": profit_factor_r,
        "max_drawdown_r": max_drawdown_r,
        "skip_reason_counts_json": '{"max_trades_per_session": 3598}',
    }


def test_dry_run_two_rows_pass_and_pf_reject(tmp_path: Path) -> None:
    sweep = tmp_path / "sweep.csv"
    _write_synthetic_sweep(
        sweep,
        [
            _combo_row("combo_0003"),
            _combo_row("combo_0001", total_r=-5.0, profit_factor_r=0.8, max_drawdown_r=15.0),
        ],
    )
    root = repo_root()
    result = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    assert result.row_count == 2
    assert result.reconstruction_pass_count == 2
    by_combo = {r.combo_id: r for r in result.rows}
    assert by_combo["combo_0003"].decision.decision == DECISION_HOLD
    assert by_combo["combo_0001"].decision.decision == DECISION_REJECT
    assert all(not r.decision.promotion_allowed_now for r in result.rows)


def test_dry_run_reconstruction_mismatch_fails_closed(tmp_path: Path) -> None:
    row = _combo_row("combo_0003")
    row["config_hash"] = "0" * 64
    sweep = tmp_path / "sweep.csv"
    _write_synthetic_sweep(sweep, [row])
    root = repo_root()
    result = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    assert result.reconstruction_pass_count == 0
    assert "config_reconstruction_failed" in result.rows[0].decision.reject_reasons


def test_dry_run_missing_combo_id_fails_closed(tmp_path: Path) -> None:
    row = _combo_row("combo_0003")
    row["combo_id"] = ""
    sweep = tmp_path / "sweep.csv"
    _write_synthetic_sweep(sweep, [row])
    root = repo_root()
    result = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    assert result.reconstruction_pass_count == 0
    assert "config_reconstruction_failed" in result.rows[0].decision.reject_reasons


def test_dry_run_deterministic_repeat(tmp_path: Path) -> None:
    sweep = tmp_path / "sweep.csv"
    _write_synthetic_sweep(sweep, [_combo_row("combo_0003")])
    root = repo_root()
    r1 = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    r2 = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    assert r1.rows[0].decision == r2.rows[0].decision
    assert r1.rows[0].rank == r2.rows[0].rank


def test_dry_run_no_candidate_yaml_written(tmp_path: Path) -> None:
    sweep = tmp_path / "sweep.csv"
    _write_synthetic_sweep(sweep, [_combo_row("combo_0003")])
    root = repo_root()
    run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    candidates = root / "configs" / "candidates"
    yaml_files = list(candidates.rglob("*.yaml")) + list(candidates.rglob("*.yml"))
    assert yaml_files == []


def test_dry_run_missing_sweep_raises(tmp_path: Path) -> None:
    root = repo_root()
    with pytest.raises(ConfigError):
        run_layer1_candidate_selection_dry_run(
            sweep_results_path=tmp_path / "missing.csv",
            base_config_path=root / BASE,
            grid_config_path=root / GRID,
        )


def test_dry_run_malformed_row_does_not_abort_other_rows(tmp_path: Path) -> None:
    sweep = tmp_path / "sweep.csv"
    bad = _combo_row("combo_0001")
    bad["total_r"] = "not-a-number"
    _write_synthetic_sweep(sweep, [_combo_row("combo_0003"), bad])
    root = repo_root()
    result = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep,
        base_config_path=root / BASE,
        grid_config_path=root / GRID,
    )
    assert result.row_count == 2
    by_combo = {r.combo_id: r for r in result.rows}
    assert "invalid_metrics" in by_combo["combo_0001"].decision.reject_reasons
    assert by_combo["combo_0003"].decision.decision == DECISION_HOLD
    assert all(not r.decision.promotion_allowed_now for r in result.rows)
