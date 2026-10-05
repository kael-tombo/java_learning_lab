# REAL_WORLD_PROJECT — Calculus in Production: Rate Monitoring & Capacity Forecast
> Production use-case: turning traffic counters into rate-of-change alerts.

## 1. Scenario
- Service: observability alerts when request rate changes faster than a threshold.
- Constraint: noisy 1-min counters; derivative estimate must not page at every jitter.
- Choice: central-difference on smoothed window + hysteresis on the rate.
- Data: `Metric{ts, requests}`; 5-min smoothing window.

## 2. Architecture
```
metrics → windowed smoothing → numeric derivative → threshold (with hysteresis) → alert
```
- Alert only when |d(rate)/dt| exceeds X for 3 consecutive windows.
- Raw and smoothed series stored for audit.

## 3. War-Story (plausible, representative)
- Incident: pages at 3 a.m. — "derivative spike" — actually a counter reset to 0.
- Symptom: magnitude-1e9 derivative tripped the threshold.
- Root cause: no guard for counter resets/wrap; derivative treated 0 as real.
- Fix: counter-reset guard (treat as gap), plus smoothing; hysteresis added.
- Lesson: numeric calculus assumes smooth data — enforce it before you differentiate.

## 4. Metrics (before → after, 30 days)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| pages/week | 22 | 3 | −86% |
| true incidents caught | 4 | 4 | same |
| median page latency | 6 min | 6 min | same |
| false positives from resets | 17 | 0 | −100% |

## 5. Prevention Checklist
- [ ] Counter resets treated as gaps, not drops.
- [ ] Smoothing window documented and tested.
- [ ] Threshold + hysteresis reviewed quarterly.
- [ ] Regression fixture: counter-reset series produces no alert.
- [ ] Log smoothed rate and derivative used in the decision.
- [ ] Property test: constant rate → derivative ≈ 0.
- [ ] Cap derivative magnitude to flag data outages explicitly.
- [ ] Dashboard: rate, derivative, pages, MTTA.

## 6. What "Good" Looks Like
- On-call sleeps; real rate changes page within one window.

## 7. Stretch
- Graduate to Kalman-filtered derivative estimates.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Derivative: https://en.wikipedia.org/wiki/Derivative
- Numerical differentiation: https://en.wikipedia.org/wiki/Numerical_differentiation
