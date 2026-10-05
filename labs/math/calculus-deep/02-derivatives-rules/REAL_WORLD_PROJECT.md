# REAL_WORLD_PROJECT — Derivatives & Rules in Production: Rate-of-Change Telemetry
> Production use-case: computing first/second derivatives of business KPIs.

## 1. Scenario
- Service: dashboard computes "growth rate of growth rate" for signups.
- Constraint: noisy daily data; avoid reporting fake accelerations from weekend effects.
- Choice: first-difference with 3-day smoothing; second derivative gated by a minimum magnitude.
- Data: `Metric{date, signups}`.

## 2. Architecture
```
series → gap/reset guard → smoothing → Δ and ΔΔ → magnitude gate → annotate dashboard
```

## 3. War-Story (plausible, representative)
- Incident: Monday spike labeled "acceleration" paged the growth team.
- Root cause: unsmoothed ΔΔ treated weekend dip+Monday recovery as signal.
- Fix: smoothing + minimum magnitude gate; pages fell 80%.
- Lesson: derivatives amplify noise — filter before you differentiate.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| spurious acceleration pages/wk | 9 | 1 |
| decision turnaround | 2 days | 2 days |

## 5. Prevention Checklist
- [ ] Smoothing window documented.
- [ ] Reset/NaN guard on the series.
- [ ] Magnitude gate on the reported rate.
- [ ] Golden fixtures: flat, linear, spike, weekend cycle.
- [ ] Log raw + smoothed + Δ + ΔΔ for audit.

## 6. What "Good" Looks Like
- Reported accelerations reproduce on re-analysis of the same data.

## 7. Stretch
- Kalman-filtered derivative estimate.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Chain rule: https://en.wikipedia.org/wiki/Chain_rule
- Numerical differentiation: https://en.wikipedia.org/wiki/Numerical_differentiation
