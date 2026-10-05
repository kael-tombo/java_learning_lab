# REAL_WORLD_PROJECT — Graph Theory in Production: Build-System Dependency Graph
> Production use-case: ordering builds and detecting circular dependencies.

## 1. Scenario
- Service: monorepo build tool schedules module compilation across 400 modules.
- Constraint: builds must respect dep order; cycles must fail the build fast.
- Choice: DAG + Kahn topo sort; parallel waves per level.
- Data: `Module{name, deps[]}` from build manifests.

## 2. Architecture
```
manifests → graph build → cycle check → topo levels → worker pool per level → cache artifacts
```
- Level k modules compile in parallel; a failure cancels downstream waves.
- Graph cached; rebuilt only on manifest hash change.

## 3. War-Story (plausible, representative)
- Incident: a cyclic dep (a→b→a via a "test-util" leak) appeared; nightly build hung.
- Symptom: build timed out at 2h; devs assumed infra issues.
- Root cause: cycle detection ran only in a linter that was disabled for speed.
- Fix: cycle check moved into the build critical path; the linter became redundant.
- Lesson: the correctness check belongs in the path that ships, not the one that's skipped.

## 4. Metrics (before → after, 2 sprints)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| full build | 95 min | 38 min | −60% (parallel waves) |
| cycle escapes to nightly | 2 | 0 | −100% |
| median time-to-first-error | 41 min | 3 min | −93% |
| wasted compiles before cycle caught | ~200 | ~10 | −95% |

## 5. Prevention Checklist
- [ ] Cycle detection mandatory before scheduling.
- [ ] Manifest schema versioned; dep changes need review.
- [ ] Parallel waves bounded by worker count.
- [ ] Failing module's reverse-dep list shown in the error.
- [ ] Cache invalidation keyed on manifest hash.
- [ ] Regression fixture: the historical cyclic manifest.
- [ ] Dashboard: build duration by wave, cache hit rate, failures by module.
- [ ] Document the DAG invariant for new module authors.

## 6. What "Good" Looks Like
- Build engineers trust the scheduler: fast, explainable, and cycles never ship.

## 7. Stretch
- Graduate to incremental builds via affected-subgraph extraction (see INTERNALS in 07-graph-theory).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Topological sorting: https://en.wikipedia.org/wiki/Topological_sorting
- Directed acyclic graph: https://en.wikipedia.org/wiki/Directed_acyclic_graph
