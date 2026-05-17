"""Layer1 candidate selection gates (Phase 7 design — evaluation only).

Pure deterministic gate evaluation for dry-run selection review.
No candidate YAML writes, no promotion side effects.
"""

from __future__ import annotations

import csv
import json
import math
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intraday.core.errors import ConfigError
from intraday.core.paths import repo_root
from intraday.layer1.grid import reconstruct_resolved_config_for_combo
from intraday.strategies.config_validation import parse_bool_like as _parse_bool_like

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
    "SelectionDryRunResult",
    "SelectionDryRunRow",
    "SelectionGateResult",
    "evaluate_selection_gates",
    "parse_bool_like",
    "parse_finite_float",
    "parse_finite_int",
    "preview_candidate_id",
    "run_layer1_candidate_selection_dry_run",
]


def parse_bool_like(value: Any, *, field_name: str) -> bool:
    """Strict boolean coercion for selection inputs (no ``bool(string)`` pitfalls)."""
    return _parse_bool_like(value, field_name)


def parse_finite_float(value: Any, *, field_name: str) -> float:
    """Parse a finite float from CSV/metric inputs; reject missing, malformed, and non-finite."""
    if value is None:
        raise ConfigError(f"{field_name}: missing value")
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            raise ConfigError(f"{field_name}: empty value")
        lowered = text.lower()
        if lowered in {"nan", "inf", "-inf", "+inf", "infinity", "-infinity"}:
            raise ConfigError(f"{field_name}: non-finite value {text!r}")
        try:
            parsed = float(text)
        except ValueError as exc:
            raise ConfigError(f"{field_name}: malformed numeric value {text!r}") from exc
    elif isinstance(value, bool):
        raise ConfigError(f"{field_name}: boolean is not a numeric metric")
    elif isinstance(value, int | float):
        parsed = float(value)
    else:
        raise ConfigError(f"{field_name}: unsupported type {type(value).__name__}")
    if not math.isfinite(parsed):
        raise ConfigError(f"{field_name}: non-finite value {parsed!r}")
    return parsed


def parse_finite_int(value: Any, *, field_name: str) -> int:
    """Parse a finite integer metric; numeric strings like ``124`` are accepted."""
    parsed = parse_finite_float(value, field_name=field_name)
    if parsed != int(parsed):
        raise ConfigError(f"{field_name}: expected integer value, got {parsed!r}")
    return int(parsed)


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


@dataclass(frozen=True)
class SelectionDryRunRow:
    """One sweep row with reconstruction outcome and gate decision."""

    combo_id: str
    sweep_row: Mapping[str, Any]
    decision: SelectionDecision
    config_reconstruction_safe: bool
    rank: int | None = None
    notes: str = ""


@dataclass(frozen=True)
class SelectionDryRunResult:
    """Aggregate outcome of a Layer1 candidate-selection dry run."""

    run_id: str
    source_sweep_path: Path
    row_count: int
    pass_count: int
    reject_count: int
    hold_count: int
    reconstruction_pass_count: int
    rows: tuple[SelectionDryRunRow, ...]


def _float_metric(row: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    raw = row.get(key)
    if raw is None or raw == "":
        return default
    try:
        return parse_finite_float(raw, field_name=key)
    except ConfigError:
        return default


def _int_metric(row: Mapping[str, Any], key: str, default: int = 0) -> int:
    raw = row.get(key)
    if raw is None or raw == "":
        return default
    try:
        return parse_finite_int(raw, field_name=key)
    except ConfigError:
        return default


def _parse_row_metrics(
    row: Mapping[str, Any],
) -> tuple[dict[str, float | int] | None, tuple[str, ...]]:
    """Parse required sweep metrics; return ``(metrics, error_fields)``."""
    metrics: dict[str, float | int] = {}
    errors: list[str] = []
    for key in ("accepted_trades", "rejected_trades", "signal_entries"):
        try:
            metrics[key] = parse_finite_int(row.get(key), field_name=key)
        except ConfigError:
            errors.append(key)
    for key in ("total_r", "profit_factor_r", "max_drawdown_r"):
        try:
            metrics[key] = parse_finite_float(row.get(key), field_name=key)
        except ConfigError:
            errors.append(key)
    if errors:
        return None, tuple(errors)
    return metrics, ()


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


def _config_reconstruction_gate(row: Mapping[str, Any]) -> tuple[bool, str]:
    """Parse ``config_reconstruction_safe``; invalid values fail closed."""
    recon_flag = row.get("config_reconstruction_safe")
    if recon_flag is None:
        return True, "not_checked"
    try:
        ok = parse_bool_like(recon_flag, field_name="config_reconstruction_safe")
    except ConfigError:
        return False, f"config_reconstruction_safe invalid: {recon_flag!r}"
    return ok, f"config_reconstruction_safe={recon_flag!r}"


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

    metrics, metric_errors = _parse_row_metrics(row)
    if metrics is None:
        combo_id = str(row.get("combo_id", ""))
        preview = preview_candidate_id(row) if combo_id else ""
        return SelectionDecision(
            gate_label=gate_label,
            decision=DECISION_REJECT,
            hard_gate_pass=False,
            reject_reasons=("invalid_metrics",),
            warning_flags=(),
            gate_results=(
                SelectionGateResult(
                    "valid_metrics",
                    "hard",
                    False,
                    f"invalid fields: {', '.join(metric_errors)}",
                ),
            ),
            promotion_allowed_now=False,
            candidate_id_preview=preview,
        )

    accepted = int(metrics["accepted_trades"])
    rejected = int(metrics["rejected_trades"])
    total_r = float(metrics["total_r"])
    profit_factor = float(metrics["profit_factor_r"])
    max_dd = float(metrics["max_drawdown_r"])

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
    recon_ok, recon_detail = _config_reconstruction_gate(row)
    if recon_required:
        gate_results.append(
            SelectionGateResult("config_reconstruction_safe", "hard", recon_ok, recon_detail)
        )
        if not recon_ok:
            reject_reasons.append("config_reconstruction_failed")

    # Invalid metrics guard (semantic negatives after finite parse)
    if accepted < 0 or profit_factor < 0 or max_dd < 0:
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
            signal_entries = int(metrics["signal_entries"])
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


def _rank_key(row: SelectionDryRunRow) -> tuple:
    sweep = row.sweep_row
    hard = row.decision.hard_gate_pass
    return (
        0 if hard else 1,
        -_float_metric(sweep, "profit_factor_r"),
        -_float_metric(sweep, "total_r"),
        _float_metric(sweep, "max_drawdown_r"),
        -_int_metric(sweep, "accepted_trades"),
        row.combo_id,
    )


def _assign_ranks(rows: list[SelectionDryRunRow]) -> list[SelectionDryRunRow]:
    rankable = [r for r in rows if r.decision.decision in (DECISION_PASS, DECISION_HOLD)]
    rankable.sort(key=_rank_key)
    rank_map = {r.combo_id: i + 1 for i, r in enumerate(rankable)}
    out: list[SelectionDryRunRow] = []
    for r in rows:
        rank = rank_map.get(r.combo_id)
        out.append(
            SelectionDryRunRow(
                combo_id=r.combo_id,
                sweep_row=r.sweep_row,
                decision=r.decision,
                config_reconstruction_safe=r.config_reconstruction_safe,
                rank=rank,
                notes=r.notes,
            )
        )
    return out


def _load_sweep_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ConfigError(f"sweep results file not found: {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ConfigError(f"sweep results CSV has no header: {path}")
        return [dict(row) for row in reader]


def run_layer1_candidate_selection_dry_run(
    *,
    sweep_results_path: Path,
    base_config_path: Path,
    grid_config_path: Path,
    gate_policy: Mapping[str, Any] | None = None,
    gate_label: str = GATE_LABEL_PA_L1_SELECTION_DESIGN_V1,
) -> SelectionDryRunResult:
    """Run deterministic Layer1 candidate-selection dry run on a sweep review CSV.

    Reconstructs and hash-verifies each combo, evaluates selection gates, and
    never writes candidate YAML or promotes rows.
    """
    root = repo_root()
    sweep_path = Path(sweep_results_path)
    if not sweep_path.is_absolute():
        sweep_path = root / sweep_path
    base_path = Path(base_config_path)
    if not base_path.is_absolute():
        base_path = root / base_path
    grid_path = Path(grid_config_path)
    if not grid_path.is_absolute():
        grid_path = root / grid_path

    pol: dict[str, Any] = {**DEFAULT_POLICY, **(dict(gate_policy) if gate_policy else {})}
    pol["gate_label"] = gate_label

    sweep_rows = _load_sweep_rows(sweep_path)
    dry_rows: list[SelectionDryRunRow] = []
    recon_pass = 0

    for row in sweep_rows:
        combo_id = str(row.get("combo_id", "")).strip()
        config_hash = str(row.get("config_hash", "")).strip()
        if not combo_id:
            eval_row = {**row, "config_reconstruction_safe": False}
            decision = evaluate_selection_gates(eval_row, policy=pol)
            dry_rows.append(
                SelectionDryRunRow(
                    combo_id="",
                    sweep_row=row,
                    decision=decision,
                    config_reconstruction_safe=False,
                    notes="missing combo_id",
                )
            )
            continue

        recon_ok = False
        recon_note = ""
        try:
            reconstruct_resolved_config_for_combo(
                base_config_path=base_path,
                grid_config_path=grid_path,
                combo_id=combo_id,
                expected_config_hash=config_hash or None,
            )
            recon_ok = True
            recon_pass += 1
        except Exception as exc:  # noqa: BLE001 — fail closed per row
            recon_note = str(exc)

        eval_row = dict(row)
        eval_row["config_reconstruction_safe"] = recon_ok
        decision = evaluate_selection_gates(eval_row, policy=pol)
        if not recon_ok and decision.hard_gate_pass:
            decision = evaluate_selection_gates(
                {**eval_row, "config_reconstruction_safe": False},
                policy=pol,
            )

        dry_rows.append(
            SelectionDryRunRow(
                combo_id=combo_id,
                sweep_row=row,
                decision=decision,
                config_reconstruction_safe=recon_ok,
                notes=recon_note or "selection dry-run review only",
            )
        )

    dry_rows = _assign_ranks(dry_rows)

    pass_count = sum(1 for r in dry_rows if r.decision.decision == DECISION_PASS)
    reject_count = sum(1 for r in dry_rows if r.decision.decision == DECISION_REJECT)
    hold_count = sum(1 for r in dry_rows if r.decision.decision == DECISION_HOLD)

    run_id = ""
    if sweep_rows:
        run_id = str(sweep_rows[0].get("run_id", "")).strip()
    if not run_id:
        run_id = f"L1_SELECT_DRY_RUN_{gate_label}_{uuid.uuid5(uuid.NAMESPACE_URL, str(sweep_path)).hex[:12]}"

    return SelectionDryRunResult(
        run_id=run_id,
        source_sweep_path=sweep_path,
        row_count=len(dry_rows),
        pass_count=pass_count,
        reject_count=reject_count,
        hold_count=hold_count,
        reconstruction_pass_count=recon_pass,
        rows=tuple(dry_rows),
    )
