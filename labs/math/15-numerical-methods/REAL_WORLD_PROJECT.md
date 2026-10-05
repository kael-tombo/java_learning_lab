# REAL_WORLD_PROJECT — Numerical Methods in Production: Sensor Calibration Service
> Production use-case: fitting a calibration curve and propagating error.

## 1. Scenario
- Service: factory flashes firmware that converts raw ADC counts to engineering units.
- Constraint: fit must pass a residual check; reported value includes an uncertainty.
- Choice: least-squares line/quad fit + 1.96σ uncertainty band on the prediction.
- Data: `CalPoint{raw, reference}`; 20 points per batch.

## 2. Architecture
```
fixture measurements → fit (normal equations) → residual check → flash params → verify run
```
- Reject batch if max residual > spec; require 1.96σ band inside tolerance.
- All math in double with explicit eps comparisons.

## 3. War-Story (plausible, representative)
- Incident: a bad-fitting sensor shipped; field units ran 4% off.
- Symptom: returns spiked after a firmware update to a new ADC revision.
- Root cause: fit used double where int overflow in naive normal equations corrupted a coefficient.
- Fix: normal equations computed via QR-style stabilized path; residual gate added; benches re-run.
- Lesson: a numeric answer is only as good as the method's error model — verify the residuals.

## 4. Metrics (before → after, 3 months)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| out-of-spec batches shipped | 3 | 0 | −100% |
| field error % median | 1.9% | 0.4% | −79% |
| calibration time/unit | 6.2s | 6.4s | +3% |
| residual-gate skips | 15% | 0% | −100% |

## 5. Prevention Checklist
- [ ] Residual + uncertainty band checked per batch.
- [ ] Fitting via a stabilized method (QR/normal-eq with care).
- [ ] Golden fixture: known line must recover slope±1%.
- [ ] Raw ADC histogram inspected before fit.
- [ ] Version the fitting code against each ADC revision.
- [ ] Store fit params + residual stats + ADC revision per unit.
- [ ] Property test: exact-line data → residual ≈ 0.
- [ ] Dashboard: residual distribution, fit R², batch rejects.

## 6. What "Good" Looks Like
- Field measurements match reference instruments within the quoted uncertainty.

## 7. Stretch
- Graduate to Levenberg–Marquardt for nonlinear calibration models.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Newton's method: https://en.wikipedia.org/wiki/Newton%27s_method
- Runge–Kutta methods: https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods
