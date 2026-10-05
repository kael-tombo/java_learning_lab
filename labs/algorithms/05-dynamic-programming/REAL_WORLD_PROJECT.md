# REAL_WORLD_PROJECT — Dynamic Programming in Production: Capacity Planner
> Production use-case: quarterly resource allocation (teams × projects under headcount).

## 1. Scenario
- Planning tool allocates headcount/budget across 60 initiatives (value, cost, deps).
- Constraint: interactive (<500ms) for W=200 headcount units; explainable picks.
- Choice: knapsack-style DP core (states×transition) + topo-ordered dep handling.
- Output: chosen set + utilization + "why not X" (swap analysis).

## 2. Architecture
```
initiatives → dep-topo filter → DP table (1-D + take flags) → pack + explain
```
- W-guardrail: W>50k refuses with FPTAS/meet-middle suggestion (pseudo-poly wall).
- Direction-comment + validator (`Σcost≤W`) in CI; deterministic tie-break.
- Scenario fork: fractional toggle shows greedy-vs-optimal gap for teaching.

## 3. War-Story
- Incident: ascending 1-D loop shipped (unbounded semantics) → same hire counted 6×.
- Symptom: plan proposed 140 heads of value with 40-head budget (impossible).
- Root cause: loop-direction bug; tests lacked ascending-vs-descending differential.
- Fix: descending + direction test + validator + 2-D audit table on demand.
- Lesson: DP bugs are silent over-counts — validators + differentials are mandatory.

## 4. Metrics (60 initiatives, W=200)
| Metric | Before (ascending bug) | After | Delta |
|--------|------------------------|-------|-------|
| Feasible plans | 0% (over-budget) | 100% | fixed |
| p99 plan | 40ms | 35ms | −12% |
| Utilization | 350% (fake) | 96% | honest |
| Explain queries/s | timeout | 120ms | fixed |
| Planning cycle | 3 weeks | 4 days | −81% |

## 5. Prevention Checklist
- [ ] Loop-direction test (asc vs desc differ correctly).
- [ ] Validator (weight + value) on every plan.
- [ ] W-size guardrail + alternative path.
- [ ] State-count comment (states × t).
- [ ] Tie-break deterministic + logged.
- [ ] Fractional-gap demo in docs.
- [ ] Reconstruction from flags (never 1-D alone).
- [ ] Overflow/mod policy for values.

## 6. What "Good" Looks Like
- Sub-500ms honest plans; every exclusion explainable via swap delta.

## 7. Stretch
- Multi-constraint (headcount + budget) 2-D DP + FPTAS slider.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- DP table patterns + map contracts: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Dynamic programming state design: https://en.wikipedia.org/wiki/Dynamic_programming
