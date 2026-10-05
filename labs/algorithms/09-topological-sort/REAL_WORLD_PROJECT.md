# REAL_WORLD_PROJECT — Topological Sort in Production: Monorepo CI Scheduler
> Production use-case: 8k-module build graph ordering + parallel batches.

## 1. Scenario
- CI schedules 8k modules (45k dep edges); minimize wall time via level batches.
- Constraint: cycle PRs blocked with culprit; 99th schedule <3s; deterministic order.
- Choice: Kahn (levels + lexicographic PQ) + DFS cross-check nightly.
- Output: `L0…Lk` batches + critical path + cycle report.

## 2. Architecture
```
PR graph → Kahn levels → worker pool (level barrier) → artifacts + cache
```
- Lexicographic for cache-friendly determinism; FIFO option for speed compare.
- Leftover = cycle core + dependents (reported, not just "cycle").
- Incremental subgraph (PR + dependents) fast path; full on main.

## 3. War-Story
- Incident: cycle merged (Kahn partial ignored — code used partial order anyway).
- Symptom: build deadlock dawn; workers waited on each other; 2h outage.
- Root cause: `size<n` treated as warning, not block; leftover list never surfaced.
- Fix: hard block + leftover-as-culprit + must-fail cycle fixture + critical-path display.
- Lesson: partial order is a verdict, not an ordering — enforce it.

## 4. Metrics (8k modules)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Cycle escapes/qtr | 2 | 0 | −100% |
| Schedule p99 | 12s | 1.8s | −85% |
| Wall (32 workers) | 48min | 21min | −56% |
| Flaky order cache-miss | 18% | 3% | determinism |
| MTTR cycle PR | 4h | 25min | −90% |

## 5. Prevention Checklist
- [ ] `size<n` = BLOCK (never warn-and-continue).
- [ ] Leftover reported (core + dependents).
- [ ] Lexicographic determinism + doc.
- [ ] Forest loop (all modules, not roots).
- [ ] Self-loop = cycle test.
- [ ] Level batches + critical path displayed.
- [ ] Incremental + full dual coverage.
- [ ] Parallel-edge dedupe (indeg guard).

## 6. What "Good" Looks Like
- Sub-2s schedules; cycles blocked with names; wall halved via levels.

## 7. Stretch
- Critical-path DP (durations) for ETA; distributed level execution.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Queue/deque contracts for Kahn levels: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Topological ordering + Kahn's algorithm: https://en.wikipedia.org/wiki/Topological_sorting
