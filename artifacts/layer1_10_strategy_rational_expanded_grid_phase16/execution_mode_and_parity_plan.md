# Phase16 Execution Mode And Parity Plan

- Execution mode used: `reference` for Phase16 grids.
- Fast path used: no. The existing repo supports fast execution, but Phase16 keeps reference execution as the accounting truth to avoid introducing a second PnL truth during expanded diagnostic runs.
- Parity spot-check approach: not required for reference-only runs. Existing fast/reference parity coverage remains out of scope for this phase unless a later runtime split explicitly opts into fast mode.
- Limitations: reference mode may make the full 20-run expanded grid slower; if runtime blocks completion, Phase16 should hand off with design and inspect artifacts rather than prefix-slicing.
- No second PnL truth: strategies produce signals/intents; execution produces trades, PnL, and R; Phase16 reports aggregate execution outputs only.
