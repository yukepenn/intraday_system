"""Write Layer1 candidate-selection dry-run review artifacts (CSV/MD only)."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from intraday.layer1.selection import (
    DECISION_REJECT,
    SelectionDryRunResult,
    SelectionDryRunRow,
)

_RESULTS_FIELDS = [
    "combo_id",
    "decision",
    "rank",
    "total_r",
    "avg_r",
    "profit_factor_r",
    "max_drawdown_r",
    "accepted_trades",
    "win_rate",
    "params_json",
    "config_hash",
    "gate_label",
    "hard_gate_pass",
    "config_reconstruction_safe",
    "reject_reasons_json",
    "warning_flags_json",
    "candidate_id_preview",
    "promotion_allowed_now",
    "notes",
]


def _row_to_csv_dict(row: SelectionDryRunRow) -> dict[str, str]:
    sweep = row.sweep_row
    d = row.decision
    return {
        "combo_id": row.combo_id,
        "decision": d.decision,
        "rank": "" if row.rank is None else str(row.rank),
        "total_r": str(sweep.get("total_r", "")),
        "avg_r": str(sweep.get("avg_r", "")),
        "profit_factor_r": str(sweep.get("profit_factor_r", "")),
        "max_drawdown_r": str(sweep.get("max_drawdown_r", "")),
        "accepted_trades": str(sweep.get("accepted_trades", "")),
        "win_rate": str(sweep.get("win_rate", "")),
        "params_json": str(sweep.get("params_json", "")),
        "config_hash": str(sweep.get("config_hash", "")),
        "gate_label": d.gate_label,
        "hard_gate_pass": str(d.hard_gate_pass),
        "config_reconstruction_safe": str(row.config_reconstruction_safe),
        "reject_reasons_json": d.reject_reasons_json(),
        "warning_flags_json": d.warning_flags_json(),
        "candidate_id_preview": d.candidate_id_preview,
        "promotion_allowed_now": "false",
        "notes": row.notes,
    }


def write_layer1_candidate_selection_dry_run_artifacts(
    result: SelectionDryRunResult,
    output_root: Path,
) -> None:
    """Write deterministic dry-run selection CSV/MD artifacts (review only)."""
    output_root.mkdir(parents=True, exist_ok=True)
    rows = list(result.rows)
    csv_rows = [_row_to_csv_dict(r) for r in rows]

    results_path = output_root / "dry_run_selection_results.csv"
    with results_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_RESULTS_FIELDS)
        w.writeheader()
        w.writerows(csv_rows)

    rejects = [r for r in csv_rows if r["decision"] == DECISION_REJECT]
    with (output_root / "dry_run_rejects.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_RESULTS_FIELDS)
        w.writeheader()
        w.writerows(rejects)

    warnings_rows: list[dict[str, str]] = []
    for r in csv_rows:
        flags = json.loads(r["warning_flags_json"])
        for flag in flags:
            warnings_rows.append({"combo_id": r["combo_id"], "warning_flag": flag})
    with (output_root / "dry_run_warnings.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["combo_id", "warning_flag"])
        w.writeheader()
        w.writerows(warnings_rows)

    hard_pass = sum(1 for r in rows if r.decision.hard_gate_pass)
    top = next((r for r in rows if r.rank == 1), None)
    reject_counter: Counter[str] = Counter()
    warn_counter: Counter[str] = Counter()
    for r in rows:
        for reason in r.decision.reject_reasons:
            reject_counter[reason] += 1
        for flag in r.decision.warning_flags:
            warn_counter[flag] += 1

    summary = {
        "run_id": result.run_id,
        "source_sweep_path": result.source_sweep_path.name,
        "row_count": str(result.row_count),
        "hard_pass_count": str(hard_pass),
        "pass_decision_count": str(result.pass_count),
        "hold_count": str(result.hold_count),
        "reject_count": str(result.reject_count),
        "reconstruction_pass_count": str(result.reconstruction_pass_count),
        "promotion_allowed_now": "false",
        "top_combo_preview": top.combo_id if top else "",
        "top_rank": str(top.rank) if top and top.rank is not None else "",
    }
    with (output_root / "dry_run_selection_summary.csv").open(
        "w", encoding="utf-8", newline=""
    ) as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary.keys()))
        w.writeheader()
        w.writerow(summary)

    md_lines = [
        "# Dry-run selection summary (Layer1 Phase 7b)",
        "",
        f"- run_id: `{result.run_id}`",
        f"- source sweep: `{result.source_sweep_path.name}`",
        f"- Total rows: **{result.row_count}**",
        f"- Hard gate pass: **{hard_pass}**",
        f"- Decision PASS: **{result.pass_count}**",
        f"- Decision HOLD: **{result.hold_count}**",
        f"- Decision REJECT: **{result.reject_count}**",
        f"- Config reconstruction pass: **{result.reconstruction_pass_count}**",
        "- promotion_allowed_now: **false** (all rows)",
        "",
        "## Top ranked preview (pass or hold only)",
        "",
    ]
    if top:
        sweep = top.sweep_row
        md_lines.append(
            f"- `{top.combo_id}` rank={top.rank} "
            f"total_r={sweep.get('total_r')} PF={sweep.get('profit_factor_r')} "
            f"max_dd={sweep.get('max_drawdown_r')}"
        )
    else:
        md_lines.append("- None")
    md_lines.extend(["", "## Common reject reasons", ""])
    for reason, count in reject_counter.most_common():
        md_lines.append(f"- `{reason}`: {count}")
    md_lines.extend(["", "## Common warning flags", ""])
    for flag, count in warn_counter.most_common():
        md_lines.append(f"- `{flag}`: {count}")
    md_lines.append("\nReview-only dry run. No promotion. Multi-window confirmation required.\n")
    (output_root / "dry_run_selection_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    results_md = [
        "# Dry-run selection results",
        "",
        "| combo_id | decision | rank | total_r | PF | hard_pass | recon |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in sorted(rows, key=lambda x: (x.rank is None, x.rank or 999)):
        sweep = r.sweep_row
        results_md.append(
            f"| {r.combo_id} | {r.decision.decision} | {r.rank or '-'} | "
            f"{float(sweep.get('total_r', 0)):.2f} | "
            f"{float(sweep.get('profit_factor_r', 0)):.3f} | "
            f"{r.decision.hard_gate_pass} | {r.config_reconstruction_safe} |"
        )
    (output_root / "dry_run_selection_results.md").write_text(
        "\n".join(results_md), encoding="utf-8"
    )
