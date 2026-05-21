# configs/data/

Dataset, session, symbol, and root YAMLs are runtime config truth for Layer 0.
Raw and curated parquet remain local-only and must not be committed.

Strategy side support does not affect data configs: strategies consume
`BarMatrix`, not parquet paths directly.
