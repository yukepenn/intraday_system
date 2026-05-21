# Hash Policy Correction

Phase19 Immediate Fix artifacts previously claimed long-only signal hashes were
unchanged after migrating current-10 canonical configs from `signal.side` to
`signal.side_mode`.

That claim is no longer made. `compute_signal_hash(...)` includes
`hash_config(resolved_strategy_config)`, so key spelling and explicit/default
config identity can legitimately change `strategy_config_hash` and
`signal_hash`.

Accepted compatibility policy:

- canonical `signal.side_mode: long_only` validates,
- legacy `signal.side: long_only` validates where intended,
- missing `side_mode` behaves as `long_only`,
- generated SignalMatrix arrays are behaviorally equivalent on representative
  fixtures,
- raw signal hash identity is not required unless identical config identity is
  explicitly proven.
