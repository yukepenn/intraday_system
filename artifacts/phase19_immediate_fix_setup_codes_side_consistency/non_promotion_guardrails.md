# Non-Promotion Guardrails (Phase19 Immediate Fix)

The Phase19 Immediate Fix is explicitly **non-promotional**. The following
guardrails must hold at the end of this phase:

- No actual Layer1 economic grid runs (only inspect-only configs).
- No expanded / full grids.
- No candidate YAML created.
- No `select-dry-run` invocations.
- No promotion of any strategy.
- No Layer2 work (router/combiner/management).
- No Layer3 work (frozen validation).
- No WFO or mini-WFO runs.
- No live or paper configs added.
- No economic claims.
- No H2 confirmation.
- No top-row retuning.

Side-aware retrofit work is structural and **inspect-only**:

- Default behavior remains `long_only`.
- Missing `side_mode` behaves like `long_only`.
- Short branches activate only when `side_mode` explicitly permits short.
- New current-10 side-aware grids are explicitly tagged
  `diagnostic_only: true`, `grid_inspect_only: true`,
  `broad_sweep_allowed: false`, `economic_claims_allowed: false`.
- Strategy YAMLs never override execution `allow_short`.
- Execution PnL/R semantics are unchanged.
