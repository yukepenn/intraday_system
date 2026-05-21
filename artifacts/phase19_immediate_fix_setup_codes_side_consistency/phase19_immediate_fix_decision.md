# Phase19 Immediate Fix — Decision

Decision label: **PHASE19_IMMEDIATE_FIX_COMPLETE**

## Why this label

All five hard gates of the immediate fix pass:

1. **Setup-code registry + Phase19B repair (Gate 1)** — created
   `src/intraday/strategies/setup_codes.py`, repaired 7 Phase19B
   strategies (11-17) to the accepted namespace (7101-7107 / 7201-7207),
   and updated all metadata YAMLs + artifacts to match. Static and
   runtime tests assert the new values and reject the wrong codes.

2. **Boolean coercion repair (Gate 2)** — added `brooks_bool` helper,
   replaced every `bool(sig.get(...))` and `bool(config.get(...))`
   pattern in Phase19B strategy modules, and added a static-scan test
   so the pattern cannot reappear.

3. **Metadata / inspect authority (Gate 3)** — extended `StrategyDef`
   with `setup_code_long`, `setup_code_short`, `allowed_side_modes`,
   `default_side_mode`, `required_feature_columns`; updated the CLI
   `strategies inspect` command to surface these alongside an audit
   cross-check against metadata YAMLs.

4. **Generic side-aware helper (Gate 4)** — added `compute_short_stop`
   and `build_side_aware_signal_matrix` in `common.py`, plus
   `validate_side_aware_strategy_base` and `CURRENT10_SIDE_MODES` in
   `config_validation.py`.

5. **Current-10 short retrofit (Gate 5)** — all 10 current strategies
   now have a structurally supported short branch behind
   `signal.side_mode`. Default behavior is unchanged (`long_only`).
   New side-aware controlled-small grid skeletons and Layer1
   grid-inspect-only configs are in place, but no economic Layer1 grid
   was run.

## Provisional next step (Cursor recommendation, not authoritative)

A natural next step is to open a Codex review on this immediate fix
before any Phase19C or Layer2 work. The roadmap decision belongs to
ChatGPT Pro + the user after Codex review.
