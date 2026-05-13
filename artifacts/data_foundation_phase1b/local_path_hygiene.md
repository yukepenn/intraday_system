# Local path hygiene

Committed artifacts avoid absolute machine roots where possible; raw inventory exports use `<repo-root>/...` for `resolved_path` when the repo base matches.
