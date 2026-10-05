# REAL_WORLD_PROJECT — Differential Equations in Production: Capacity Decay Forecaster
> Production use-case: forecasting battery capacity from observed decay rates.

## 1. Scenario
- Service: battery telemetry models remaining capacity as exponential decay.
- Constraint: forecast must state uncertainty; divergence fails the model.
- Choice: fit dy/dt = −ky to capacity samples; forecast with confidence band.
- Data: `Reading{ts, capacity}`.

## 2. Architecture
```
readings → rate estimate → fit k → analytic decay forecast → band → report
```

## 3. War-Story (plausible, representative)
- Incident: a unit with a dead sensor reported k<0 (capacity growing).
- Root cause: no sanity check on the fitted sign; forecast showed rising capacity.
- Fix: k must be ≥0; negatives flagged as sensor fault.
- Lesson: an ODE model's parameters live in a physical domain — enforce it.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| forecast error (median) | 8% | 3% |
| sensor-fault escapes | 2 | 0 |

## 5. Prevention Checklist
- [ ] Parameter domain checks (k≥0).
- [ ] Confidence band on the forecast.
- [ ] Golden fixtures: flat, decaying, sensor-fault.
- [ ] Forecast never extends past data confidence.

## 6. What "Good" Looks Like
- Capacity forecasts match lab measurements within the band.

## 7. Stretch
- Logistic capacity model for end-of-life cliff.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Exponential decay: https://en.wikipedia.org/wiki/Exponential_decay
- Initial value problem: https://en.wikipedia.org/wiki/Initial_value_problem
