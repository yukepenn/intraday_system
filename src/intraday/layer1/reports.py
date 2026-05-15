"""Write small Layer1 smoke artifacts (summaries only)."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from intraday.layer1.config import Layer1SmokeConfig
from intraday.layer1.result import (
    Layer1GridResult,
    Layer1GridRow,
    Layer1SmokeResult,
    layer1_smoke_result_to_jsonable,
)


def write_layer1_smoke_artifacts(
    artifact_root: Path,
    *,
    smoke: Layer1SmokeConfig,
    result: Layer1SmokeResult,
    adapter_skip_reasons: dict[str, int],
) -> None:
    artifact_root.mkdir(parents=True, exist_ok=True)

    summary_path = artifact_root / "layer1_smoke_summary.json"
    payload = layer1_smoke_result_to_jsonable(result)
    payload["adapter_skip_reasons"] = dict(adapter_skip_reasons)
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    metrics = result.metrics
    _write_dist_csv(artifact_root / "exit_reason_distribution.csv", metrics.exit_reason_counts)
    _write_dist_csv(artifact_root / "reject_reason_distribution.csv", metrics.reject_reason_counts)
    _write_dist_csv(artifact_root / "skip_reason_distribution.csv", result.skip_counts)

    metrics_md = artifact_root / "metrics_snapshot.md"
    lines = [
        "# Layer1 smoke metrics snapshot",
        "",
        f"- run_id: `{result.run_id}`",
        f"- executed_results: {result.executed_results}",
        f"- accepted_trades: {metrics.accepted_trades}",
        f"- rejected_trades: {metrics.rejected_trades}",
        f"- total_r: {metrics.total_r}",
        f"- avg_r: {metrics.avg_r}",
        f"- win_rate: {metrics.win_rate}",
        f"- profit_factor_r: {metrics.profit_factor_r}",
        f"- max_drawdown_r: {metrics.max_drawdown_r}",
        "",
    ]
    metrics_md.write_text("\n".join(lines), encoding="utf-8")


def _write_dist_csv(path: Path, counts: dict[str, int]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["reason", "count"])
        for k in sorted(counts.keys()):
            w.writerow([k, counts[k]])


def write_config_manifest(artifact_root: Path, smoke_dict: dict[str, Any]) -> None:
    """Persist a copy of the smoke YAML-derived manifest for audit."""
    artifact_root.mkdir(parents=True, exist_ok=True)
    p = artifact_root / "smoke_config_manifest.json"
    p.write_text(json.dumps(smoke_dict, indent=2), encoding="utf-8")


_SWEEPS_HEADER = [
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


def _row_as_sweep_list(r: Layer1GridRow) -> list[Any]:
    pfr = r.profit_factor_r
    pfr_cell = "inf" if pfr == float("inf") else pfr
    return [
        r.run_id,
        r.combo_id,
        r.config_hash,
        r.params_json,
        r.signal_entries,
        r.valid_intents,
        r.executed_results,
        r.accepted_trades,
        r.rejected_trades,
        r.total_r,
        r.avg_r,
        r.median_r,
        r.win_rate,
        pfr_cell,
        r.max_drawdown_r,
        r.avg_bars_held,
        r.exit_reason_counts_json,
        r.reject_reason_counts_json,
        r.skip_reason_counts_json,
        r.adapter_skip_reasons_json,
        r.feature_hash,
        r.signal_hash,
        r.execution_mode,
    ]


def _merge_json_counts(rows: list[Layer1GridRow], field: str) -> dict[str, int]:
    ctr: Counter[str] = Counter()
    for r in rows:
        blob = getattr(r, field)
        d = json.loads(blob)
        for k, v in d.items():
            ctr[str(k)] += int(v)
    return dict(sorted(ctr.items()))


def write_layer1_grid_artifacts(result: Layer1GridResult, output_root: Path) -> None:
    """Write CSV/MD summaries for a controlled grid run (no row-level trades)."""
    output_root.mkdir(parents=True, exist_ok=True)
    rows = list(result.rows)

    sweep_path = output_root / "sweep_results.csv"
    with sweep_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(_SWEEPS_HEADER)
        for r in rows:
            w.writerow(_row_as_sweep_list(r))

    cfg_inv = output_root / "config_inventory.csv"
    with cfg_inv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["combo_id", "config_hash", "params_json"])
        for r in rows:
            w.writerow([r.combo_id, r.config_hash, r.params_json])

    grid_inv = output_root / "grid_inventory.csv"
    with grid_inv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["combo_id", "config_hash", "params_json", "signal_hash"])
        for r in rows:
            w.writerow([r.combo_id, r.config_hash, r.params_json, r.signal_hash])

    exit_ctr = _merge_json_counts(rows, "exit_reason_counts_json")
    rej_ctr = _merge_json_counts(rows, "reject_reason_counts_json")
    skip_ctr: Counter[str] = Counter()
    for r in rows:
        for k, v in json.loads(r.skip_reason_counts_json).items():
            skip_ctr[str(k)] += int(v)
    _write_dist_csv(output_root / "exit_reason_distribution.csv", exit_ctr)
    _write_dist_csv(output_root / "reject_reason_distribution.csv", rej_ctr)
    _write_dist_csv(output_root / "skip_reason_distribution.csv", dict(sorted(skip_ctr.items())))

    def _pf_sort_key(r: Layer1GridRow) -> float:
        return float("inf") if r.profit_factor_r == float("inf") else float(r.profit_factor_r)

    top_tr = sorted(rows, key=lambda r: r.total_r, reverse=True)
    top_pf = sorted(rows, key=_pf_sort_key, reverse=True)
    top_n = min(10, len(rows))

    with (output_root / "top_rows_by_total_r.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(_SWEEPS_HEADER)
        for r in top_tr[:top_n]:
            w.writerow(_row_as_sweep_list(r))

    with (output_root / "top_rows_by_profit_factor.csv").open(
        "w", encoding="utf-8", newline=""
    ) as fh:
        w = csv.writer(fh)
        w.writerow(_SWEEPS_HEADER)
        for r in top_pf[:top_n]:
            w.writerow(_row_as_sweep_list(r))

    cg_csv = output_root / "controlled_grid_summary.csv"
    with cg_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "run_id",
                "symbol",
                "start",
                "end",
                "combo_count",
                "feature_hash",
                "execution_mode",
                "total_accepted_trades",
            ]
        )
        total_acc = sum(r.accepted_trades for r in rows)
        w.writerow(
            [
                result.run_id,
                result.symbol,
                result.start,
                result.end,
                result.combo_count,
                result.feature_hash,
                result.execution_mode,
                total_acc,
            ]
        )

    cg_md = output_root / "controlled_grid_summary.md"
    best_tr = top_tr[0] if top_tr else None
    best_pf = top_pf[0] if top_pf else None
    lines = [
        "# Layer1 controlled grid summary",
        "",
        f"- run_id: `{result.run_id}`",
        f"- symbol: {result.symbol}",
        f"- window: {result.start} .. {result.end}",
        f"- combos: {result.combo_count}",
        f"- feature_hash: `{result.feature_hash}`",
        f"- execution_mode: {result.execution_mode}",
        f"- total accepted trades (sum over combos): {total_acc}",
    ]
    if best_tr is not None:
        lines.append(f"- best total_r: `{best_tr.combo_id}` → {best_tr.total_r}")
    if best_pf is not None:
        pfr = best_pf.profit_factor_r
        pfs = "inf" if pfr == float("inf") else str(pfr)
        lines.append(f"- best profit_factor_r: `{best_pf.combo_id}` → {pfs}")
    lines.append("")
    cg_md.write_text("\n".join(lines), encoding="utf-8")
