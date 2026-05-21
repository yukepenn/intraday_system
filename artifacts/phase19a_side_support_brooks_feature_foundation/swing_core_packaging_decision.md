# Phase19A Swing-Core Packaging Decision

Decision: **Option A - package lightweight `pa_brooks_swing_core` inside `pa_brooks_core_v1.yaml`.**

Rationale:

- Slice F1 only implements basic prior-exclusive / current-confirmed swing facts: leg direction, pullback count/depth, two-leg pullback proxies, and second-entry proxies.
- These facts are small enough to travel with bar/regime core without creating a third Slice F1 config.
- Advanced pivots, MTR, wedge, climax, and nested reversal classifiers remain deferred.

No `pa_brooks_swing_v1.yaml` is created in Phase19A.
