# REAL_WORLD_PROJECT — Limits & Continuity in Production: Sensor Threshold Alarms
> Production use-case: alerting only when a signal truly crosses a threshold.

## 1. Scenario
- Service: alerting on temperature/pressure crossing a setpoint.
- Constraint: don't page on a 1-sample blip; verify crossing with left/right behavior.
- Choice: require the crossing to persist for k samples and match one-sided agreement.
- Data: `Sample{ts, value}`.

## 2. Architecture
```
stream → smoothing → one-sided crossing check → persistence rule → alert
```

## 3. War-Story (plausible, representative)
- Incident: a single NaN sample was treated as a "crossing" and paged on-call.
- Fix: NaN/gap guard + persistence rule; pages dropped 90%.
- Lesson: a limit-like value must agree from both sides and from persistence.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| false pages/day | 14 | 1 |
| p99 alert latency | 12s | 13s |

## 5. Prevention Checklist
- [ ] NaN/gap guard before threshold logic.
- [ ] Persistence rule documented and tested.
- [ ] Golden fixtures: blip, step, oscillation.
- [ ] Log smoothed value + crossing evidence.
- [ ] Dashboard: alerts, latency, suppressed blips.

## 6. What "Good" Looks Like
- Pages correspond to real, persistent crossings.

## 7. Stretch
- Hysteresis bands on both sides of the threshold.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Limit of a function: https://en.wikipedia.org/wiki/Limit_of_a_function
- Intermediate value theorem: https://en.wikipedia.org/wiki/Intermediate_value_theorem
