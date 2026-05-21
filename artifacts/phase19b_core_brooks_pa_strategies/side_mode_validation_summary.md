# Side Mode Validation Summary

Current-10 validators now reject `signal.side_mode: short_only` and `both`; missing side mode and `long_only` preserve current long-only behavior. Phase19B Brooks validators explicitly accept `long_only`, `short_only`, and `both`.
