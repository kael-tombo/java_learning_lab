# REAL_WORLD_PROJECT — Complexity Analysis in Production: Checkout Capacity Plan
> Production use-case: Big-Sale checkout (QPS × algo-cost → hosts + SLO defense).

## 1. Scenario
- Checkout: 40k QPS peak; pipeline (auth O(1), cart scan O(k), promo sort O(p log p), fraud BFS O(V+E)).
- Constraint: p99 250ms; host budget fixed; no "just add boxes" without math.
- Choice: per-stage Big-O + doubling-validated constants → host model + load-shed order.
- Output: capacity sheet + shed priority + scale triggers.

## 2. Architecture
```
QPS model → Σ stage-cost(n) → hosts = peak×cost×headroom / per-host → autoscale + shed
```
- Harness (warmup + best-of) per stage; ratios confirm O-claims quarterly.
- Amortized paths (doubling buffers, DSU) quoted amortized + worst (both).
- Pseudo-poly trap flagged (promo-budget `nW` refuses huge W → FPTAS path).

## 3. War-Story
- Incident: promo sort assumed O(n) (was O(n log n) + quadratic fallback on ties) → 3× CPU at peak.
- Symptom: p99 250ms → 1.9s; autoscale lagged (model said "fine"); shed fired late.
- Root cause: unvalidated O-claim + no doubling test; tie-heavy catalog hit fallback.
- Fix: validated model + 3-way/timely fallback + shed by stage-cost (promo first) + pre-scale trigger.
- Lesson: capacity without measured constants is fiction — ratios or it didn't happen.

## 4. Metrics (peak 40k QPS)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| p99 checkout | 1.9s | 210ms | −89% |
| Hosts (peak) | 320 (panic) | 190 (modeled) | −41% |
| Shed correctness | late/random | cost-ordered | SLO kept |
| Model error | 3.1× | 1.1× | validated |
| Promo sort p99 | 400ms | 22ms | fallback fix |

## 5. Prevention Checklist
- [ ] Per-stage O + measured constant (sheet).
- [ ] Doubling ratios in CI (classify log/linear/quadratic).
- [ ] Amortized + worst both quoted.
- [ ] Pseudo-poly guardrail (W-size refuse).
- [ ] Shed order = cost-desc (documented).
- [ ] Warmup/reps/DCE in harness method.
- [ ] Pre-scale trigger (not reactive).
- [ ] Post-mortem model-error tracked.

## 6. What "Good" Looks Like
- 210ms p99 at peak; 190 hosts modeled; shed never touches auth.

## 7. Stretch
- Queueing + Little's law overlay; JMH publication-grade for hot stages.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Performance measurement utilities (nanoTime, collections): https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Time complexity classes + analysis method: https://en.wikipedia.org/wiki/Time_complexity
