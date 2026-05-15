"""Write small Layer1 smoke artifacts (summaries only)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from intraday.layer1.config import Layer1SmokeConfig
from intraday.layer1.result import Layer1SmokeResult, layer1_smoke_result_to_jsonable


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
