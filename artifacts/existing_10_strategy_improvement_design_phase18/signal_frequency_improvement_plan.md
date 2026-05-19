# Phase18 Signal-Frequency Improvement Plan

## Scope

Signal-frequency review targets low-sample and zero/near-zero-trade risks without simply loosening thresholds.

## Low-Sample Strategies

Primary signal-frequency attention: gap_acceptance_failure, vwap_reclaim_reject, prior_day_level_trap.

Phase17 classified gap acceptance failure, VWAP reclaim/reject, and prior-day level trap as low sample. VWAP pullback and failed ORB also have marginal or weak evidence that requires context review before any future run.

## Design Questions

- Is the trigger logically too rare, or is the current market window unsuitable?
- Are existing feature facts sufficient to explain rejected or missing signals?
- Does the trigger depend on session-open, gap, VWAP, or prior-level state that should be audited before implementation?

## Guardrail

The future answer cannot be "lower the threshold because a top row looked good." Any implementation must include zero-signal diagnostics and tests proving no lookahead and session-safe behavior.
