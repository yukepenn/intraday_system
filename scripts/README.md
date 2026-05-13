# scripts/

Thin bootstrap helpers. The runtime CLI (`intraday ...`) is the only canonical entrypoint.

Scripts here may:

- bootstrap fresh datasets,
- verify repository invariants,
- generate audit bundles.

They must NOT contain strategy, execution, or router logic.

Phase 0/1A ships:

- `validate_repo.py` — quick structure check (delegates to `intraday.cli.main validate structure`).
- `bootstrap_from_qt.py` — placeholder describing the intentional non-port from QT.
