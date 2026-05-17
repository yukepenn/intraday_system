"""Phase 7 selection gate evaluator tests."""

from __future__ import annotations

from intraday.layer1.selection import (
    DECISION_HOLD,
    DECISION_REJECT,
    GATE_LABEL_PA_L1_SELECTION_DESIGN_V1,
    evaluate_selection_gates,
)


def _passing_row() -> dict:
    return {
        "combo_id": "combo_0003",
        "config_hash": "abc",
        "accepted_trades": 124,
        "rejected_trades": 0,
        "total_r": 6.5,
        "profit_factor_r": 1.14,
        "max_drawdown_r": 5.7,
        "params_json": '{"risk":{"stop_mode":"rolling_low","target_r":1.0}}',
        "config_reconstruction_safe": True,
        "signal_entries": 4380,
        "skip_reason_counts_json": '{"max_trades_per_session": 3598}',
    }


def test_row_passes_hard_gates() -> None:
    d = evaluate_selection_gates(_passing_row())
    assert d.hard_gate_pass is True
    assert d.gate_label == GATE_LABEL_PA_L1_SELECTION_DESIGN_V1
    assert d.promotion_allowed_now is False


def test_row_fails_insufficient_trades() -> None:
    row = {**_passing_row(), "accepted_trades": 50}
    d = evaluate_selection_gates(row)
    assert d.decision == DECISION_REJECT
    assert "insufficient_trades" in d.reject_reasons


def test_row_fails_negative_total_r() -> None:
    row = {**_passing_row(), "total_r": -1.0}
    d = evaluate_selection_gates(row)
    assert "negative_total_r" in d.reject_reasons


def test_row_fails_weak_pf() -> None:
    row = {**_passing_row(), "profit_factor_r": 1.0}
    d = evaluate_selection_gates(row)
    assert "weak_profit_factor" in d.reject_reasons


def test_row_fails_excessive_drawdown() -> None:
    row = {**_passing_row(), "max_drawdown_r": 15.0}
    d = evaluate_selection_gates(row)
    assert "excessive_drawdown" in d.reject_reasons


def test_row_holds_single_window_warning() -> None:
    d = evaluate_selection_gates(_passing_row())
    assert d.decision == DECISION_HOLD
    assert "needs_multi_window_validation" in d.warning_flags
    assert "single_window_only" in d.warning_flags


def test_reject_reasons_deterministic() -> None:
    row = {**_passing_row(), "accepted_trades": 10, "total_r": -5.0, "profit_factor_r": 0.5}
    d1 = evaluate_selection_gates(row)
    d2 = evaluate_selection_gates(row)
    assert d1.reject_reasons == d2.reject_reasons
    assert d1.reject_reasons_json() == d2.reject_reasons_json()


def test_promotion_allowed_now_always_false() -> None:
    d = evaluate_selection_gates(_passing_row())
    assert d.promotion_allowed_now is False


def test_config_reconstruction_failed_rejects() -> None:
    row = {**_passing_row(), "config_reconstruction_safe": False}
    d = evaluate_selection_gates(row)
    assert "config_reconstruction_failed" in d.reject_reasons
