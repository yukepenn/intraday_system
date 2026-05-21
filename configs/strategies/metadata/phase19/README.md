# configs/strategies/metadata/phase19/

Metadata for Brooks PA strategies 11-17 only. Strategies 18-20 are reserved in
the setup-code registry but are not implemented.

For 11-17, `diagnostic_only: false` because they are core strategies,
`grid_inspect_only: true`, and `economic_claims_allowed: false`. Metadata
mirrors runtime registry/`StrategyDef`; it is not runtime truth.
