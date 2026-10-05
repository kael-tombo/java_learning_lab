# REAL_WORLD_PROJECT — BFS in Production: Outage Blast-Radius Map
> Production use-case: dependency-hop impact analysis during incidents (unweighted hops).

## 1. Scenario
- Incident tool maps service deps (unweighted) from failing root; need all within k hops.
- Constraint: 200k nodes / 2M edges; answer in <2s; levels + paths required.
- Choice: BFS with level batches + parent pointers; bidirectional for far targets.
- Output: per-hop lists + affected-team fanout.

## 2. Architecture
```
alert → snapshot graph → BFS levels (ArrayDeque, BitSet visited) → hop map + page
```
- Mark-on-enqueue (dup-storm guard); forest not needed (single blast source).
- Early stop at k+1 (don't flood whole graph); parent back-chain for sample paths.
- Bidirectional when target team known (meet-in-middle).

## 3. War-Story
- Incident: mark-on-dequeue variant deployed; hub service (50k deps) re-enqueued 40×.
- Symptom: 2s query → 90s timeout during real outage; queue OOM on 2 coordinators.
- Root cause: dequeue-marking + missing level cap; frontier exploded.
- Fix: enqueue-marking + k-cap + BitSet + bidirectional for targeted queries.
- Lesson: BFS correctness includes *when* you mark — load-test on hub nodes.

## 4. Metrics (200k-node graph)
| Metric | Before (dequeue-mark) | After | Delta |
|--------|-----------------------|-------|-------|
| p99 k=3 query | 90s (timeout) | 1.1s | −99% |
| Enqueues | 8.4M (dups) | 210k | −97% |
| Memory/query | 1.8GB | 90MB | −95% |
| Targeted (bi) | — | 0.3s | 3.7× vs BFS |
| Correct paths | 92% | 100% | parent fix |

## 5. Prevention Checklist
- [ ] Mark-on-enqueue lint + hub-node perf test.
- [ ] k-cap + early-exit standard.
- [ ] Level-batch API (not just dist[]) for paging.
- [ ] Weighted-edge guard (refuse → Dijkstra).
- [ ] Snapshot isolation (graph version per query).
- [ ] Queue/memory budget + timeout.
- [ ] Bidirectional for single-target far queries.
- [ ] Blast map cached per incident id.

## 6. What "Good" Looks Like
- Sub-2s hop maps; pages include hop + path; no OOM on hubs.

## 7. Stretch
- 0-1 BFS for degraded (weight 0/1) links; animated frontier in UI.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Queue (ArrayDeque) FIFO contract used for levels: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- BFS level/shortest-hop guarantees: https://en.wikipedia.org/wiki/Breadth-first_search
