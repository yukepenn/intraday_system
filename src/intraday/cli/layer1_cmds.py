"""CLI: Layer1 smoke run (Phase 6) and controlled grid (Phase 6b)."""

from __future__ import annotations

import json
from pathlib import Path

from intraday.core.paths import repo_root
from intraday.layer1.config import load_layer1_controlled_grid_config
from intraday.layer1.grid import grid_document_combo_count, load_grid_document
from intraday.layer1.runner import (
    print_layer1_grid_summary,
    print_layer1_smoke_summary,
    run_layer1_controlled_grid,
    run_layer1_smoke,
)
from intraday.layer1.selection import run_layer1_candidate_selection_dry_run
from intraday.layer1.selection_reports import write_layer1_candidate_selection_dry_run_artifacts


def cmd_layer1_run(*, config: str) -> int:
    root = repo_root()
    path = Path(config)
    if not path.is_absolute():
        path = root / path
    res = run_layer1_smoke(path)
    print_layer1_smoke_summary(res)
    return 0


def cmd_layer1_inspect(*, config: str) -> int:
    from intraday.layer1.config import load_layer1_smoke_config, validate_layer1_smoke_config

    root = repo_root()
    path = Path(config)
    if not path.is_absolute():
        path = root / path
    cfg = load_layer1_smoke_config(path)
    validate_layer1_smoke_config(cfg)
    d = {
        "run_id": cfg.run_id,
        "symbol": cfg.symbol,
        "start": cfg.start,
        "end": cfg.end,
        "strategy": cfg.strategy_name,
        "execution_mode": cfg.execution_mode,
        "artifact_root": cfg.artifact_root,
        "max_trades_per_session": cfg.max_trades_per_session,
    }
    print(json.dumps(d, indent=2))
    return 0


def cmd_layer1_grid(*, config: str) -> int:
    root = repo_root()
    path = Path(config)
    if not path.is_absolute():
        path = root / path
    cfg = load_layer1_controlled_grid_config(path)
    res = run_layer1_controlled_grid(path)
    print_layer1_grid_summary(res, artifact_root=cfg.artifact_root)
    return 0


def cmd_layer1_grid_inspect(*, config: str) -> int:
    from intraday.layer1.config import validate_layer1_controlled_grid_config

    root = repo_root()
    path = Path(config)
    if not path.is_absolute():
        path = root / path
    cfg = load_layer1_controlled_grid_config(path)
    validate_layer1_controlled_grid_config(cfg)
    gpath = Path(cfg.strategy_grid_path)
    if not gpath.is_absolute():
        gpath = root / gpath
    gdoc = load_grid_document(gpath)
    n = grid_document_combo_count(gdoc)
    out = {
        "run_id": cfg.run_id,
        "symbol": cfg.symbol,
        "start": cfg.start,
        "end": cfg.end,
        "combo_count": n,
        "strategy": cfg.strategy_name,
        "grid_path": cfg.strategy_grid_path,
        "execution_mode": cfg.execution_mode,
        "artifact_root": cfg.artifact_root,
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_layer1_select_dry_run(
    *,
    sweep_results: str,
    base_config: str,
    grid_config: str,
    output_root: str,
) -> int:
    root = repo_root()
    sweep_path = Path(sweep_results)
    if not sweep_path.is_absolute():
        sweep_path = root / sweep_path
    base_path = Path(base_config)
    if not base_path.is_absolute():
        base_path = root / base_path
    grid_path = Path(grid_config)
    if not grid_path.is_absolute():
        grid_path = root / grid_path
    out_path = Path(output_root)
    if not out_path.is_absolute():
        out_path = root / out_path

    result = run_layer1_candidate_selection_dry_run(
        sweep_results_path=sweep_path,
        base_config_path=base_path,
        grid_config_path=grid_path,
    )
    write_layer1_candidate_selection_dry_run_artifacts(result, out_path)

    print(f"row_count={result.row_count}")
    print(f"pass_count={result.pass_count}")
    print(f"reject_count={result.reject_count}")
    print(f"hold_count={result.hold_count}")
    print(f"reconstruction_pass_count={result.reconstruction_pass_count}")
    print("promotion_allowed_now=false for all rows")

    preview_rows = [r for r in result.rows if r.rank is not None]
    preview_rows.sort(key=lambda r: r.rank or 999)
    for r in preview_rows[:3]:
        sweep = r.sweep_row
        print(
            f"preview rank={r.rank} combo_id={r.combo_id} "
            f"decision={r.decision.decision} total_r={sweep.get('total_r')} "
            f"PF={sweep.get('profit_factor_r')}"
        )
    return 0
