# REAL_WORLD_PROJECT — DP Basics in Production: Fare Estimator (Stair-Cost Pattern)
> Production use-case: ride-fare estimator (stops × surge tiers) on linear DP.

## 1. Scenario
- Fare service: multi-leg quotes (per-leg cost + transfer minima) for 10k routes/s.
- Constraint: p99 8ms; exact cents (`long`); bases audited (empty-trip = 0, one-leg = base).
- Choice: tabulated linear DP (two-var) + mod-free exact; memo variant in admin replay.
- Output: quote + leg-breakdown + base-case audit id.

## 2. Architecture
```
legs → tab DP (O(stops), O(1) space) → quote + parent pointers (breakdown)
```
- Base-case table in config (reviewed); overflow test (max legs × max surge).
- Depth-safe (no recursion on hot path); replay uses memo for explanation.
- Identity test (`ways==fib+1` analog on tiered model) in CI.

## 3. War-Story
- Incident: `cost[0]=0` base mis-set (should be "empty way = 1 way, 0 cost") → all multi-leg off by one tier.
- Symptom: 6% quotes 1 tier low; support tickets "cheaper then charged".
- Root cause: base-case edit without induction check; tests started at n=2 (missed 0/1).
- Fix: 0/1 golden fixtures + induction comment + config-review rule for bases.
- Lesson: DP bases are money — pin 0/1 with goldens and review them like schema.

## 4. Metrics (10k QPS)
| Metric | Before (base bug) | After | Delta |
|--------|-------------------|-------|-------|
| Misquotes | 6.1% | 0.0% | −100% |
| p99 quote | 6ms | 2ms (tab) | −67% |
| Overflow incidents | 1 (int) | 0 (long) | fixed |
| Dispute tickets/wk | 44 | 2 | −95% |
| Replay explain | none | 100% | parent ptrs |

## 5. Prevention Checklist
- [ ] 0/1 golden fixtures (block deploy on change).
- [ ] `long` cents + overflow test.
- [ ] Iterative hot path (no recursion depth).
- [ ] State-order comment (deps-first).
- [ ] Sentinel review (no −1 collision).
- [ ] Mod policy (exact here; mod elsewhere explicit).
- [ ] Breakdown (parents) for disputes.
- [ ] Cliff note (naive never in prod).

## 6. What "Good" Looks Like
- 2ms p99 exact quotes; bases pinned; every quote explainable.

## 7. Stretch
- Fast-doubling for 10⁶-leg freight quotes (mod); tiered-discount DP.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Tabulation collections + numeric handling: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- DP recurrence + induction structure: https://en.wikipedia.org/wiki/Dynamic_programming
