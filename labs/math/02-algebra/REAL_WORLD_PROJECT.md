# REAL_WORLD_PROJECT — Algebra in Production: Pricing & Break-Even Engine
> Production use-case: solving pricing/cost equations behind an ops dashboard.

## 1. Scenario
- Service: finance dashboard answers "what price hits our target margin?" and "when do we break even?".
- Constraint: answers must be explainable (steps shown), inputs validated, units handled.
- Choice: linear model `profit = p*q - (fixed + var*q)`; solve symbolically then evaluate.
- Data: `Product{fixedCost, variableCost, price, volume}`.

## 2. Architecture
```
input form → validate → build equations → solve (linear/quadratic) → explain → persist scenario
```
- Solver module returns solution + steps + sensitivity (dprofit/dp).
- Unit guard: all money in cents, volume in units; mismatches rejected early.
- Feature flag to switch solver backend.

## 3. War-Story (plausible, representative)
- Incident: dashboard showed break-even at negative volume after a unit mix-up.
- Symptom: "profitable at -200 units/mo" ticket from a confused PM.
- Root cause: variable cost entered in dollars, volume in thousands; equation mixed units.
- Fix: explicit unit types, validation that both sides carry the same unit; negative-volume results flagged.
- Lesson: algebra is only as honest as its units.

## 4. Metrics (before → after, pilot quarter)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| invalid scenarios shipped | 6 | 0 | −100% |
| time to answer "new price?" | 45 min | 2 min | −96% |
| explanation included | no | yes (steps) | new |
| unit-mismatch defects | 3/qtr | 0 | −100% |

## 5. Prevention Checklist
- [ ] Every equation carries units; solver checks dimensional consistency.
- [ ] Steps logged for every answer (auditable).
- [ ] Negative or zero denominators produce friendly errors.
- [ ] Golden scenarios in CI (known break-evens).
- [ ] Sensitivity readout next to every answer.
- [ ] Rate-limit the scenario API to keep bounds on ad-hoc solves.
- [ ] Cache last N scenarios for instant revisit.
- [ ] Dashboard: scenarios run/day, error rate, latency p99.

## 6. What "Good" Looks Like
- PMs self-serve break-even what-ifs; finance signs off because steps are reproducible.

## 7. Stretch
- Graduate to linear programming solves (see 13-mathematical-optimization).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Linear algebra vs algebra refresher: https://en.wikipedia.org/wiki/Algebra
- Dimensional analysis: https://en.wikipedia.org/wiki/Dimensional_analysis
