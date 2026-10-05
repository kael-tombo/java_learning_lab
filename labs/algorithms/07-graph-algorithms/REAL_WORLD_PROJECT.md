# REAL_WORLD_PROJECT — Graph Algorithms in Production: Fraud-Ring Detection
> Production use-case: money-mule ring discovery (BFS hops + DFS structure + Dijkstra amounts).

## 1. Scenario
- Ledger graph 10M accounts / 80M transfers; daily ring scan + realtime hop check.
- Need: k-hop fanout (BFS), cycle/SCC structure (DFS), min-cost mule path (Dijkstra).
- Constraint: nightly full <2h; realtime hop <300ms; explainable cases.
- Choice: dispatch by question (hops/structure/cost) — one platform, three engines.

## 2. Architecture
```
ledger → snapshot → BFS fanout | DFS/SCC rings | Dijkstra cost-paths → case queue
```
- Adj-list + CSR for cache; forest loops everywhere; weighted guard (amount≥0 for Dijkstra).
- Negative-adjustment (fee rebates) routed to BF sidecar, never Dijkstra.
- Case explainer: hop map + cycle path + cheapest-path triple.

## 3. War-Story
- Incident: BFS used for cheapest-path (hops ≠ dollars) → big ring missed (3 hops, low split).
- Symptom: recall dip 12%; analysts saw "short" paths that weren't cheap.
- Root cause: wrong-tool dispatch (no weight check); DFS-only cycle pass missed cross-shard rings.
- Fix: dispatch gate (weighted?→Dijkstra, structure?→DFS/SCC) + cross-shard union step.
- Lesson: graph platform needs a router, not a favorite algorithm.

## 4. Metrics (nightly + realtime)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Ring recall | 76% | 93% | +17pp |
| Realtime hop p99 | 900ms | 180ms | −80% |
| Full scan | 3.4h | 1.1h | −68% |
| False cases | 22% | 9% | −13pp |
| Cost-path error | 31% | 0.4% | dispatch fix |

## 5. Prevention Checklist
- [ ] Dispatch flowchart in code (`weighted? negative? pairs? DAG?`).
- [ ] Wrong-tool differential tests (BFS-vs-cost gap demo).
- [ ] Forest + mark-on-enqueue standards.
- [ ] SCC for rings (not just DFS boolean).
- [ ] Snapshot + shard-union for cross-partition.
- [ ] `long` amounts + overflow tests.
- [ ] Explainer triple per case (hop/cycle/cost).
- [ ] Recall/precision tracked per release.

## 6. What "Good" Looks Like
- 93% recall, sub-300ms hops, every case has a map + path + cost.

## 7. Stretch
- Max-flow for cut-off (which edge freezes ring); community detection note.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Graph collections + traversal building blocks: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Graph traversal families (BFS/DFS roles): https://en.wikipedia.org/wiki/Graph_traversal
