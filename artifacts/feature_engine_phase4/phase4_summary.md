# Phase 4 summary

Phase **4** delivers the centralized **feature engine MVP**: `BarMatrix` + YAML (`pa_core_v1`) + optional `FeatureStore` → deterministic `FeatureMatrix` (`float64`, `feature_hash`), reference kernels only (`mode="fast"` rejected).

Deliverables: `docs/FEATURE_CONTRACT.md`, `src/intraday/features/**` (engine, registry, specs, store, kernels), `configs/features/pa_core_v1.yaml`, `features` CLI, unit + smoke tests, `artifacts/feature_engine_phase4/` review tables.

**Decision:** `FEATURE_ENGINE_MVP_COMPLETE`  
**Next:** `IMPLEMENT_PA_STRATEGY_MVP`
