# REAL_WORLD_PROJECT — Integral Fundmentals in Production: Billing by Usage Metering
> Production use-case: billing customers on area under a usage curve.

## 1. Scenario
- Service: API gateway bills by area-under-the-curve of concurrent connections.
- Constraint: the meter must integrate noisy samples; gaps must not silently zero the area.
- Choice: trapezoid over contiguous windows; long gaps flagged, not integrated as zero.
- Data: `Sample{ts, concurrent}`.

## 2. Architecture
```
samples → gap detect → trapezoid per window → sum → invoice line → audit
```

## 3. War-Story (plausible, representative)
- Incident: a 2-hour telemetry gap was integrated as zero, underbilling a customer the big one.
- Root cause: gap not detected; trapezoid silently assumed zero.
- Fix: gap threshold; windows with gaps billed by interpolation or flagged for manual review.
- Lesson: an integral presumes contiguity — detect the gaps.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| underbilling incidents/mo | 3 | 0 |
| audit disputes/mo | 7 | 1 |

## 5. Prevention Checklist
- [ ] Gap threshold enforced; flagged windows listed.
- [ ] Golden fixture: known trapezoid area.
- [ ] Both endpoints sampled exactly on window close.
- [ ] Meter value logged per window.

## 6. What "Good" Looks Like
- Customer invoice lines reproduce from raw samples deterministically.

## 7. Stretch
- Move to exact integration of a smoothing spline.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Riemann integral: https://en.wikipedia.org/wiki/Riemann_integral
- Trapezoidal rule: https://en.wikipedia.org/wiki/Trapezoidal_rule
