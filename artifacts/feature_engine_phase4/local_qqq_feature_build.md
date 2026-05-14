# Local QQQ 2024H1 feature build

- **Ran:** yes (curated `QQQ` present under `data/curated/bars_1m_rth`)
- **Rows:** 48360
- **Feature columns:** 22
- **feature_hash:** `facb93387b6460a7f79bfd08a23b71560539d284f5ca2f0e1b565cb224a15498`
- **data_hash (bars):** `b00d2b8cf0bc183bcbc792a75a3eea3a44c254bd656df672a267c3b39a40050d`
- **Cache:** `--no-cache` → FeatureStore not used; no cache files written for this smoke
- **NaN highlights:** ORB columns 1736 NaNs (expected incomplete first minutes per session); `trend_slope_like_20` 2480 NaNs (warm-up / session starts)
