"""Layer1 candidate selection gates (Phase 7 design — evaluation only).

Pure deterministic gate evaluation for dry-run selection review.
No candidate YAML writes, no promotion side effects.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

GATE_LABEL_PA_L1_SELECTION_DESIGN_V1 = "PA_L1_SELECTION_DESIGN_V1"

DECISION_PASS = "PASS_FOR_SELECTION_DESIGN"
DECISION_REJECT = "REJECT_FOR_SELECTION_DESIGN"
DECISION_HOLD = "HOLD_FOR_REVIEW"

DEFAULT_POLICY: dict[str, Any] = {
    "gate_label": GATE_LABEL_PA_L1_SELECTION_DESIGN_V1,
    "min_accepted_trades": 100,
    "min_profit_factor_r": 1.05,
    "min_total_r": 0.0,
    "max_drawdown_r": 10.0,
    "max_rejected_trades_ratio": 0.05,
    "require_config_reconstruction_safe": True,
    "single_window_design": True,
    "warn_stop_mode_dominance": True,
}

__all__ = [
    "DECISION_HOLD",
    "DECISION_PASS",
    "DECISION_REJECT",
    "DEFAULT_POLICY",
    "GATE_LABEL_PA_L1_SELECTION_DESIGN_V1",
    "SelectionDecision",
    "SelectionGateResult",
    "evaluate_selection_gates",
    "preview_candidate_id",
]


@dataclass(frozen=True)
class SelectionGateResult:
    """Outcome of one selection gate."""

    gate_name: str
    gate_type: str  # "hard" | "soft"
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class SelectionDecision:
    """Dry-run selection decision for one grid row."""

    gate_label: str
    decision: str
    hard_gate_pass: bool
    reject_reasons: tuple[str, ...] = ()
    warning_flags: tuple[str, ...] = ()
    gate_results: tuple[SelectionGateResult, ...] = ()
    promotion_allowed_now: bool = False
    candidate_id_preview: str = ""
    rank: int | None = None

    def reject_reasons_json(self) -> str:
        return json.dumps(list(self.reject_reasons), sort_keys=True)

    def warning_flags_json(self) -> str:
        return json.dumps(list(self.warning_flags), sort_keys=True)


def _float_metric(row: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    raw = row.get(key)
    if raw is None or raw == "":
        return default
    return float(raw)


def _int_metric(row: Mapping[str, Any], key: str, default: int = 0) -> int:
    raw = row.get(key)
    if raw is None or raw == "":
        return default
    return int(raw)


def _params_stop_mode(row: Mapping[str, Any]) -> str | None:
    raw = row.get("params_json")
    if not raw:
        return None
    try:
        params = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    risk = params.get("risk") if isinstance(params, dict) else None
    if isinstance(risk, dict):
        mode = risk.get("stop_mode")
        return str(mode) if mode is not None else None
    return None


def preview_candidate_id(row: Mapping[str, Any], *, symbol: str = "QQQ") -> str:
    """Non-stable preview id for dry-run tables only (not runtime identity)."""
    combo = str(row.get("combo_id", "unknown"))
    cfg_hash = str(row.get("config_hash", ""))[:12]
    return f"preview_{symbol.lower()}_{combo}_{cfg_hash}"


def evaluate_selection_gates(
    row: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> SelectionDecision:
    """Evaluate provisional Layer1 PA selection gates on one sweep row.

    Reads metrics and optional reconstruction flags from ``row`` only.
    Never writes files or promotes candidates.
    """
    pol: dict[str, Any] = {**DEFAULT_POLICY, **(dict(policy) if policy else {})}
    gate_label = str(pol.get("gate_label", GATE_LABEL_PA_L1_SELECTION_DESIGN_V1))

    accepted = _int_metric(row, "accepted_trades")
    rejected = _int_metric(row, "rejected_trades")
    total_r = _float_metric(row, "total_r")
    profit_factor = _float_metric(row, "profit_factor_r")
    max_dd = _float_metric(row, "max_drawdown_r")

    gate_results: list[SelectionGateResult] = []
    reject_reasons: list[str] = []
    warning_flags: list[str] = []

    # Hard: trade count
    min_trades = int(pol["min_accepted_trades"])
    trades_ok = accepted >= min_trades
    gate_results.append(
        SelectionGateResult(
            "min_accepted_trades",
            "hard",
            trades_ok,
            f"accepted_trades={accepted} need>={min_trades}",
        )
    )
    if not trades_ok:
        reject_reasons.append("insufficient_trades")

    # Hard: profit factor
    min_pf = float(pol["min_profit_factor_r"])
    pf_ok = profit_factor >= min_pf
    gate_results.append(
        SelectionGateResult(
            "profit_factor_r",
            "hard",
            pf_ok,
            f"profit_factor_r={profit_factor:.4f} need>={min_pf}",
        )
    )
    if not pf_ok:
        reject_reasons.append("weak_profit_factor")

    # Hard: total R
    min_total = float(pol["min_total_r"])
    total_ok = total_r > min_total
    gate_results.append(
        SelectionGateResult(
            "total_r",
            "hard",
            total_ok,
            f"total_r={total_r:.4f} need>{min_total}",
        )
    )
    if not total_ok:
        reject_reasons.append("negative_total_r")

    # Hard: drawdown magnitude (positive R units in metrics)
    max_dd_limit = float(pol["max_drawdown_r"])
    dd_ok = max_dd <= max_dd_limit
    gate_results.append(
        SelectionGateResult(
            "max_drawdown_r",
            "hard",
            dd_ok,
            f"max_drawdown_r={max_dd:.4f} need<={max_dd_limit}",
        )
    )
    if not dd_ok:
        reject_reasons.append("excessive_drawdown")

    # Hard: execution rejection anomaly
    ratio_limit = float(pol.get("max_rejected_trades_ratio", 0.05))
    denom = max(accepted + rejected, 1)
    rej_ratio = rejected / denom
    rej_ok = rejected == 0 or rej_ratio <= ratio_limit
    gate_results.append(
        SelectionGateResult(
            "execution_rejection_anomaly",
            "hard",
            rej_ok,
            f"rejected_trades={rejected} ratio={rej_ratio:.4f}",
        )
    )
    if not rej_ok:
        reject_reasons.append("manual_review_required")

    # Hard: config reconstruction (caller may set bool on row)
    recon_required = bool(pol.get("require_config_reconstruction_safe", True))
    recon_flag = row.get("config_reconstruction_safe")
    if recon_flag is None:
        recon_ok = True
        recon_detail = "not_checked"
    else:
        recon_ok = bool(recon_flag)
        recon_detail = f"config_reconstruction_safe={recon_flag!r}"
    if recon_required:
        gate_results.append(
            SelectionGateResult("config_reconstruction_safe", "hard", recon_ok, recon_detail)
        )
        if not recon_ok:
            reject_reasons.append("config_reconstruction_failed")

    # Invalid metrics guard
    if accepted < 0 or profit_factor < 0:
        gate_results.append(
            SelectionGateResult("valid_metrics", "hard", False, "negative metric values")
        )
        if "invalid_metrics" not in reject_reasons:
            reject_reasons.append("invalid_metrics")

    hard_gate_pass = not reject_reasons

    # Soft warnings (never flip hard pass to reject)
    if pol.get("single_window_design", True):
        warning_flags.append("single_window_only")
        warning_flags.append("needs_multi_window_validation")

    if pol.get("warn_stop_mode_dominance", True):
        stop_mode = _params_stop_mode(row)
        if stop_mode == "rolling_low":
            warning_flags.append("stop_mode_dominance")
            warning_flags.append("parameter_sensitivity")

    warning_flags.append("resolved_config_from_reconstruction_not_embedded")
    warning_flags.append("candidate_id_preview_not_runtime_id")

    pf_margin = profit_factor - min_pf
    if hard_gate_pass and 0 <= pf_margin < 0.05:
        warning_flags.append("low_margin_pf")

    skip_raw = row.get("skip_reason_counts_json")
    if skip_raw:
        try:
            skips = json.loads(skip_raw) if isinstance(skip_raw, str) else dict(skip_raw)
            signal_entries = _int_metric(row, "signal_entries", 1)
            max_sess = int(skips.get("max_trades_per_session", 0))
            if signal_entries > 0 and max_sess / signal_entries > 0.85:
                warning_flags.append("high_skip_rate")
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    if hard_gate_pass:
        warning_flags.append("SINGLE_WINDOW_DESIGN_ONLY")
        warning_flags.append("NEEDS_CONFIRMATION_WINDOW")

    # Deduplicate while preserving order
    seen: set[str] = set()
    warning_flags_unique: list[str] = []
    for w in warning_flags:
        if w not in seen:
            seen.add(w)
            warning_flags_unique.append(w)

    reject_unique = tuple(dict.fromkeys(reject_reasons))
    warn_unique = tuple(warning_flags_unique)

    if not hard_gate_pass:
        decision = DECISION_REJECT
    elif warn_unique:
        decision = DECISION_HOLD
    else:
        decision = DECISION_PASS

    combo_id = str(row.get("combo_id", ""))
    preview = preview_candidate_id(row)

    return SelectionDecision(
        gate_label=gate_label,
        decision=decision,
        hard_gate_pass=hard_gate_pass,
        reject_reasons=reject_unique,
        warning_flags=warn_unique,
        gate_results=tuple(gate_results),
        promotion_allowed_now=False,
        candidate_id_preview=preview if combo_id else "",
    )
