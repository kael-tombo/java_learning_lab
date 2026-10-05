# REAL_WORLD_PROJECT — Bellman-Ford + Floyd in Production: FX Arbitrage Guard
> Production use-case: FX/latency routing with negative (rebate) edges + all-pairs tables.

## 1. Scenario
- Treasury router: 200 currencies, rebate edges (negative costs), needs cycle + all-pairs.
- Constraint: precompute all-pairs nightly (FW 200³ = 8M, trivial); realtime single-source BF.
- Choice: FW tables + BF detection sidecar; Dijkstra refused on negatives.
- Output: route + negative-cycle (arbitrage) alert with loop path.

## 2. Architecture
```
rates → −log weights → FW nightly (k-outer) + BF realtime → routes + arb alerts
```
- `long` scaled micros + INF/4; k-snapshots for audit (which k improved cell).
- Undirected-negative guard (2-cycle instant) at ingest.
- Dijkstra only on non-negative filtered snapshot (documented split).

## 3. War-Story
- Incident: FW deployed with i-outer loop → 4% routes suboptimal, one arb loop missed ($40k exposure).
- Symptom: nightly diff vs BF oracle drifted; k-audit showed impossible improvement order.
- Root cause: loop-order semantics (k must be outer); tests too small to expose (n=5 passed).
- Fix: k-outer + oracle differential (n=50 random vs BF-per-source) + exposure cap.
- Lesson: DP loop order is semantics; differential oracles catch what unit tests miss.

## 4. Metrics (200 currencies)
| Metric | Before (i-outer) | After | Delta |
|--------|------------------|-------|-------|
| Suboptimal routes | 4.1% | 0.0% | −100% |
| Missed arb loops | 1 (exposure) | 0 + cap | contained |
| FW nightly | 9s | 7s | −22% |
| Oracle diff (5k pairs) | 204 | 0 | −100% |
| False-cycle alerts | 6/wk | 0 | INF-guard fix |

## 5. Prevention Checklist
- [ ] k-outer comment + order test (crafted fail on i-outer).
- [ ] BF-per-source oracle differential in CI.
- [ ] V−1 + detection always (no early-exit skip).
- [ ] INF/4 + `!=INF` guards.
- [ ] Undirected-negative ingest guard.
- [ ] Exposure cap + arb-alert runbook.
- [ ] k-snapshot audit for disputed routes.
- [ ] Dijkstra-refusal on negatives (assert).

## 6. What "Good" Looks Like
- Zero-diff vs oracle; every arb alert has loop + P&L bound.

## 7. Stretch
- Johnson for 10k-asset sparse; intraday incremental FW.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- All-pairs / numeric table handling in Java: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Bellman–Ford passes + negative-cycle detection: https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm
