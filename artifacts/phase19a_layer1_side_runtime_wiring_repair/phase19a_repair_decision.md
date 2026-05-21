# Phase19A Repair Decision

Final decision label: **`PHASE19A_LAYER1_SIDE_RUNTIME_WIRING_REPAIR_COMPLETE`**.

Layer1 side-runtime wiring is complete for the repaired scope:

- smoke path passes `reference_close=bars.close`;
- controlled-grid path passes `reference_close=bars.close`;
- smoke path passes side-mode-derived `allowed_sides`;
- controlled-grid path passes side-mode-derived `allowed_sides`.

Current-10 behavior remains unchanged: missing `signal.side_mode` defaults to `long_only`, default execution remains `allow_short=false`, and no current-10 short retrofit was performed.

Phase19B strategies 11-17 implementation is provisionally allowed next only after Codex review, ChatGPT Pro review, and user approval.

Candidate YAML, promotion, select-dry-run, actual Layer1 economic grids, Layer2/3, WFO, live, and paper remain blocked because this phase produced no strategy 11-17 runtime implementation, no candidate pool, and no economic evidence.
