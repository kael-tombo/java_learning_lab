# MINI_PROJECT — Topological Sort: Build Scheduler
> Implement + benchmark + visualize. ~3 hours.

## Goal
Schedule a mock monorepo build (modules + deps) with Kahn levels (parallel batches),
lexicographic variant, and cycle report pointing at the culprit edge set.

## Build Steps
1. `Scheduler.java`: Kahn + DFS-topo + validator `edgesForward()`.
2. Fixture: 12 modules (api, auth, db, …) with DAG edges; print batches `L0:[…] L1:[…]`.
3. Visualize: ASCII DAG + level timeline (`L0 ███ L1 ██ …`).
4. Cycle: inject `web→api→web`; assert partial output + leftover list.
5. Benchmark: chain 10⁵ + random DAG 10⁴; FIFO vs PQ-Kahn timings.

## Benchmark Table (fill)
| graph | Kahn ms | DFS ms | PQ-Kahn ms | levels |
|-------|---------|--------|------------|--------|
| chain 10⁵ | | | | 10⁵ |
| random 10⁴ | | | | ~ |

## Visualize
```
L0: [db, auth] L1: [api] L2: [web]  critical path = db→api→web
```

## Acceptance
- [ ] Batches + critical-path length printed. [ ] Cycle leftover correct.
- [ ] Validator green on both implementations.

## Extensions
- Parallel-build simulation (workers=4) with level-barrier timing.
