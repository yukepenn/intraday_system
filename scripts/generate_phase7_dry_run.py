"""One-off Phase 7 dry-run artifact generator (design review only)."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from intraday.core.paths import repo_root
from intraday.layer1.grid import reconstruct_resolved_config_for_combo
from intraday.layer1.selection import (
    DECISION_HOLD,
    DECISION_PASS,
    DECISION_REJECT,
    GATE_LABEL_PA_L1_SELECTION_DESIGN_V1,
    evaluate_selection_gates,
)

ROOT = repo_root()
OUT = ROOT / "artifacts/layer1_pa_candidate_selection_design_phase7"
SWEEP = ROOT / "artifacts/layer1_pa_grid_review_phase6c/sweep_results_review.csv"
BASE = "configs/strategies/base/pa_buy_sell_close_trend.yaml"
GRID = "configs/strategies/grids/pa_buy_sell_close_trend_controlled_small.yaml"


def _rank_key(row: dict) -> tuple:
    hard = row["hard_gate_pass"] in (True, "True", "true", 1)
    return (
        0 if hard else 1,
        -float(row["profit_factor_r"]),
        -float(row["total_r"]),
        float(row["max_drawdown_r"]),
        -int(row["accepted_trades"]),
        row["combo_id"],
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows_out: list[dict] = []
    with SWEEP.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            combo_id = row["combo_id"]
            config_hash = row["config_hash"]
            recon_ok = False
            recon_note = ""
            try:
                reconstruct_resolved_config_for_combo(
                    base_config_path=BASE,
                    grid_config_path=GRID,
                    combo_id=combo_id,
                    expected_config_hash=config_hash,
                )
                recon_ok = True
            except Exception as exc:  # noqa: BLE001 — audit artifact
                recon_note = str(exc)
            eval_row = dict(row)
            eval_row["config_reconstruction_safe"] = recon_ok
            decision = evaluate_selection_gates(eval_row)
            if not recon_ok and decision.hard_gate_pass:
                decision = evaluate_selection_gates(
                    {**eval_row, "config_reconstruction_safe": False}
                )
            rows_out.append(
                {
                    "combo_id": combo_id,
                    "decision": decision.decision,
                    "rank": "",
                    "total_r": row["total_r"],
                    "avg_r": row["avg_r"],
                    "profit_factor_r": row["profit_factor_r"],
                    "max_drawdown_r": row["max_drawdown_r"],
                    "accepted_trades": row["accepted_trades"],
                    "win_rate": row["win_rate"],
                    "params_json": row["params_json"],
                    "config_hash": config_hash,
                    "gate_label": GATE_LABEL_PA_L1_SELECTION_DESIGN_V1,
                    "hard_gate_pass": str(decision.hard_gate_pass),
                    "reject_reasons_json": decision.reject_reasons_json(),
                    "warning_flags_json": decision.warning_flags_json(),
                    "candidate_id_preview": decision.candidate_id_preview,
                    "promotion_allowed_now": "false",
                    "config_reconstruction_safe": str(recon_ok),
                    "notes": recon_note or "dry-run design only",
                }
            )

    rankable = [r for r in rows_out if r["decision"] in (DECISION_PASS, DECISION_HOLD)]
    rankable.sort(key=_rank_key)
    for i, r in enumerate(rankable, start=1):
        r["rank"] = str(i)
    for r in rows_out:
        if r["decision"] == DECISION_REJECT:
            r["rank"] = ""

    fieldnames = list(rows_out[0].keys()) if rows_out else []
    with (OUT / "dry_run_selection_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_out)

    rejects = [r for r in rows_out if r["decision"] == DECISION_REJECT]
    with (OUT / "dry_run_rejects.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rejects)

    warnings_rows = []
    for r in rows_out:
        flags = json.loads(r["warning_flags_json"])
        for flag in flags:
            warnings_rows.append({"combo_id": r["combo_id"], "warning_flag": flag})
    with (OUT / "dry_run_warnings.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["combo_id", "warning_flag"])
        w.writeheader()
        w.writerows(warnings_rows)

    hard_pass = sum(1 for r in rows_out if r["hard_gate_pass"] == "True")
    hold = sum(1 for r in rows_out if r["decision"] == DECISION_HOLD)
    rejected = sum(1 for r in rows_out if r["decision"] == DECISION_REJECT)
    passed = sum(1 for r in rows_out if r["decision"] == DECISION_PASS)
    top = rankable[0] if rankable else None
    reject_counter = Counter()
    warn_counter = Counter()
    for r in rows_out:
        for reason in json.loads(r["reject_reasons_json"]):
            reject_counter[reason] += 1
        for flag in json.loads(r["warning_flags_json"]):
            warn_counter[flag] += 1

    summary = {
        "total_rows": len(rows_out),
        "hard_pass_count": hard_pass,
        "pass_decision_count": passed,
        "hold_count": hold,
        "rejected_count": rejected,
        "promotion_allowed_now": False,
        "top_combo_preview": top["combo_id"] if top else "",
        "top_rank": top["rank"] if top else "",
    }
    with (OUT / "dry_run_selection_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary.keys()))
        w.writeheader()
        w.writerow(summary)

    md_lines = [
        "# Dry-run selection summary (Phase 7)",
        "",
        f"- Total rows: **{len(rows_out)}**",
        f"- Hard gate pass: **{hard_pass}**",
        f"- Decision PASS: **{passed}**",
        f"- Decision HOLD: **{hold}**",
        f"- Decision REJECT: **{rejected}**",
        f"- promotion_allowed_now: **false** (all rows)",
        "",
        "## Top ranked preview (pass or hold only)",
        "",
    ]
    if top:
        md_lines.append(
            f"- `{top['combo_id']}` rank={top['rank']} "
            f"total_r={top['total_r']} PF={top['profit_factor_r']} "
            f"max_dd={top['max_drawdown_r']}"
        )
    else:
        md_lines.append("- None")
    md_lines.extend(
        [
            "",
            "## Common reject reasons",
            "",
        ]
    )
    for reason, count in reject_counter.most_common():
        md_lines.append(f"- `{reason}`: {count}")
    md_lines.extend(["", "## Common warning flags", ""])
    for flag, count in warn_counter.most_common():
        md_lines.append(f"- `{flag}`: {count}")
    md_lines.append(
        "\nMulti-window confirmation is required before any future promotion.\n"
    )
    (OUT / "dry_run_selection_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    results_md = ["# Dry-run selection results", "", "| combo_id | decision | rank | total_r | PF | hard_pass |", "| --- | --- | --- | --- | --- | --- |"]
    for r in sorted(rows_out, key=lambda x: (x["rank"] == "", x["rank"] or "999")):
        results_md.append(
            f"| {r['combo_id']} | {r['decision']} | {r['rank'] or '-'} | "
            f"{float(r['total_r']):.2f} | {float(r['profit_factor_r']):.3f} | {r['hard_gate_pass']} |"
        )
    (OUT / "dry_run_selection_results.md").write_text("\n".join(results_md), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
