# Doc Contract Refresh Summary

The normative docs were refreshed narrowly for Phase19 polish:

- `signal.side_mode` is canonical; legacy `signal.side` is compatibility-only.
- Setup-code registry and `StrategyDef`/metadata alignment are documented.
- Layer1 validates side-aware stop geometry with `reference_close=bars.close`.
- The adapter and execution boundary are separated: side mode gates intent
  eligibility, execution `allow_short` gates fills.
- Config-key migration may change cache/signal hashes even when behavior is
  equivalent.
- No economic grid, candidate, Layer2/3, WFO, live, paper, or promotion policy
  changed.
