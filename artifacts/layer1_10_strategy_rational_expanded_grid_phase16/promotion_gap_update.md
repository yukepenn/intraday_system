# Phase16 Promotion Gap Update

Phase16 reports are not sufficient for promotion. They support diagnostic review only.

Remaining gaps before any future promotion:

- Risk distribution: partially available only if future summaries can derive it from execution outputs; current committed grid CSVs do not persist per-trade risk rows.
- Cost-to-risk distribution: reporting gap unless execution outputs expose per-trade risk and costs without recomputing PnL.
- Full resolved config capture: config hashes and params are available; full resolved config archival remains a future gate.
- Data-quality gates: H1/H2 validation is diagnostic; H2 warning remains open.
- Fresh holdout: not introduced in Phase16.
- Candidate schema: no candidate YAML generated in Phase16.
- Selection gates: select-dry-run intentionally not run.
