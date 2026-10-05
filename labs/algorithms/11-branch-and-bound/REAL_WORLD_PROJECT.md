# REAL_WORLD_PROJECT — Branch and Bound in Production: Dispatch Optimizer (TSP/VRP-lite)
> Production use-case: 25-stop courier dispatch with optimality-gap SLA.

## 1. Scenario
- Courier hub: 25 stops/van, minimize drive-minutes; 60s optimizer budget.
- Constraint: gap ≤3% or escalate; exact when possible, bounded-approx otherwise.
- Choice: B&B (assignment-bound + best-first) seeded by Clarke-Wright heuristic.
- Output: route + gap % + nodes/fathoms + timeout-safe incumbent.

## 2. Architecture
```
stops → heuristic seed (best) → B&B (PQ best-first, incremental bounds) → route + gap
```
- Ratio/order presort for knapsack-legs; strong-branching on tight zones.
- Fathom telemetry (bound/leaf/infeasible split); Luby restarts for tails.
- Fallback: DP Held-Karp memo for n≤20 legs; FPTAS note for knapsack-legs.

## 3. War-Story
- Incident: exact-only B&B (no timeout) on snow-day 25-stop → 14min hang, vans idle.
- Symptom: dispatch queue froze; drivers waited; manual dispatch (worse routes).
- Root cause: no time-box, weak initial best (no heuristic seed → no prune early).
- Fix: 60s cap + greedy seed (gap 4% instantly) + gap telemetry + async (poll, don't block).
- Lesson: optimizer SLA is (gap, time), not just optimum — ship the tradeoff.

## 4. Metrics (25 stops)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Dispatch p99 | 14min (hang) | 58s (capped) | −93% |
| Gap at cap | — (no answer) | 1.8% | SLA met |
| Miles vs manual | — | −13% | savings |
| Nodes (seeded) | 4.2M | 310k | −93% |
| Idle van-min/day | 190 | 35 | −82% |

## 5. Prevention Checklist
- [ ] Timeout + incumbent + gap (contract).
- [ ] Heuristic seed before B&B (always).
- [ ] Bound presort (ratio/order) validated.
- [ ] Fathom telemetry + dashboard.
- [ ] Async dispatch (poll pattern).
- [ ] n-guardrail (exact vs approx path).
- [ ] Double-epsilon on bound ties.
- [ ] Replay log (stops → route + gap).

## 6. What "Good" Looks Like
- 58s bounded, 1.8% gap, −13% miles with proof per dispatch.

## 7. Stretch
- Column generation for 100+ stops; traffic-aware re-opt.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- PQ ordering for best-first search: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Branch-and-bound fathoming + bounds: https://en.wikipedia.org/wiki/Branch_and_bound
