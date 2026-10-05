# REAL_WORLD_PROJECT — Derivative Applications in Production: Pricing Sensitivity Engine
> Production use-case: converting derivative outputs into pricing guardrails.

## 1. Scenario
- Service: pricing tool reports "elasticity of revenue to price change".
- Constraint: elasticity sign/magnitude must be sanity-checked; extremes trigger review.
- Choice: compute dR/dp from a fitted demand curve; gate |elasticity| to a sane band.
- Data: `Sale{price, qty}` history.

## 2. Architecture
```
fits → dR/dp → elasticity → band check → guardrail alert → analyst review
```

## 3. War-Story (plausible, representative)
- Incident: an elasticity of +12x was reported after a promo dip.
- Root cause: fit was done on the promo window only; derivative on an extrapolated segment.
- Fix: extrapolation guard; elasticity outside ±3 flagged, not displayed.
- Lesson: a derivative is only valid where the model fits — guard the domain.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| absurd elasticity reports/wk | 5 | 0 |
| review turnaround | 4 days | 1 day |

## 5. Prevention Checklist
- [ ] Domain guard on every reported derivative.
- [ ] Sanity band on elasticity.
- [ ] Golden fixtures: elastic, inelastic, unit.
- [ ] Fit window and sample size logged.
- [ ] Extrapolation never displayed as fact.

## 6. What "Good" Looks Like
- Pricing decisions cite elasticity with a defensible domain.

## 7. Stretch
- Automatic refit with confidence intervals.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Elasticity (economics): https://en.wikipedia.org/wiki/Elasticity_(economics)
- L'Hôpital's rule: https://en.wikipedia.org/wiki/L%27H%C3%B4pital%27s_rule
