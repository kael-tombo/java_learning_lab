# REAL_WORLD_PROJECT — Greedy in Production: Asset Scheduler + Huffman Cache
> Production use-case: ad-slot scheduling (activity selection) + edge-cache compression (Huffman).

## 1. Scenario
- Publisher fills 10⁵ ad slots/day (max count) + compresses edge manifests (Huffman).
- Constraint: schedule in <1s; compression ratio within 5% of entropy; provable picks.
- Choice: earliest-finish greedy (exchange-proven) + PQ Huffman; DP only for weighted-value variant.
- Output: slot plan + prefix codes + ratio report.

## 2. Architecture
```
slots → sort-by-finish → greedy take → plan
manifests → freq → PQ merges → codes → ship + ratio log
```
- Weighted-value path dispatches to DP (greedy-breaker detector runs both, alerts on gap).
- Prefix-free validator in CI; ratio regression gate (fail if +2% size).

## 3. War-Story
- Incident: ratio-greedy applied to weighted (0/1) slots → revenue −18% for a week.
- Symptom: fill count up, revenue down (cheap slots crowded out premium).
- Root cause: unweighted proof misapplied to weighted; no breaker test.
- Fix: weight-aware dispatch (greedy iff uniform value, else DP) + revenue-canary.
- Lesson: every greedy ships with its proof scope + a breaker that must fail.

## 4. Metrics (daily)
| Metric | Before (wrong greedy) | After | Delta |
|--------|----------------------|-------|-------|
| Revenue | −18% vs plan | +2% | +20pp |
| Fill count | 98% | 91% | honest tradeoff |
| Compress ratio | 0.62 | 0.60 | −3% |
| Schedule p99 | 0.8s | 0.7s | −12% |
| Breaker coverage | 0 | 1 (must-fail) | guard |

## 5. Prevention Checklist
- [ ] Proof-scope comment per greedy (exchange/matroid + limits).
- [ ] Breaker fixture (must show gap).
- [ ] Weighted-dispatch gate (uniform? greedy : DP).
- [ ] Prefix-free validator + ratio gate.
- [ ] Revenue-canary on scheduling changes.
- [ ] PQ/DSU cost comments.
- [ ] Approximation bound quoted where heuristic.
- [ ] Rollback on canary dip.

## 6. What "Good" Looks Like
- Proven picks, guarded dispatch, revenue + ratio both green.

## 7. Stretch
- LPT bound for multi-channel fill; set-cover log-factor note.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- PriorityQueue mechanics for Huffman/Kruskal: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Greedy choice + matroid scope: https://en.wikipedia.org/wiki/Greedy_algorithm
