# REAL_WORLD_PROJECT — DFS in Production: Dependency Cycle Outage
> Production use-case: monorepo import graph (400k files) cycle detection in CI.

## 1. Scenario
- CI must block circular imports; graph 400k nodes / 1.2M edges, budget 60s.
- Need: cycle verdict + culprit path for the PR author.
- Choice: iterative 3-color DFS (forest) + back-edge path via stack; Kahn cross-check.
- Output: `BLOCKED: a→b→c→a` + suggested break (edge with min dependents).

## 2. Architecture
```
PR → incremental subgraph (changed + dependents) → iterative DFS → verdict + path
```
- Full nightly DFS (3-color, explicit stack — no recursion at depth).
- PR-scoped subgraph for speed; fallback full on demand.
- Color-state metric (gray-depth histogram) for perf triage.

## 3. War-Story
- Incident: single-`visited` (no gray) checker passed a real cycle (cross vs back conflated).
- Symptom: cycle merged to main; build deadlock at 3am; rollback of 40 PRs.
- Root cause: no on-stack distinction + single-source start (missed forest component).
- Fix: GRAY set + forest loop + culprit-path output + negative fixture (known cycle must fail).
- Lesson: cycle detection without gray is just traversal — test the negative.

## 4. Metrics (400k-node graph)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Cycle escape | 1/quarter | 0/4 quarters | −100% |
| PR check p99 | 48s (recursive, flaky overflow) | 9s | −81% |
| Overflow crashes | 3/mo | 0 | iterative |
| Culprit path present | 0% | 100% | fix time −70% |
| False positives | 12/mo | 1/mo | parent-skip fix |

## 5. Prevention Checklist
- [ ] 3-color/onStack mandatory (lint for DFS).
- [ ] Forest loop (no single-source).
- [ ] Known-cycle must-fail fixture.
- [ ] Iterative (depth-proof) + overflow test.
- [ ] Culprit path in verdict (not just boolean).
- [ ] Undirected parent-skip where applicable.
- [ ] Pre/post distinction documented for topo reuse.
- [ ] Incremental + full dual paths.

## 6. What "Good" Looks Like
- Sub-10s PR verdicts with actionable cycle paths; zero escapes.

## 7. Stretch
- SCC (Tarjan) grouping for multi-cycle reports.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Graph traversal contracts (collections used for stacks/queues): https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- DFS colors + back-edge cycle theorem: https://en.wikipedia.org/wiki/Depth-first_search
