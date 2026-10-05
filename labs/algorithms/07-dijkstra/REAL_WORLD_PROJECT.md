# REAL_WORLD_PROJECT — Dijkstra in Production: ETA Service (Maps)
> Production use-case: city-scale ETA + route for ride-hail (non-negative weights).

## 1. Scenario
- 2M nodes / 5M edges (time-weights); 5k QPS; p99 120ms; single-target queries.
- Constraint: no negatives (traffic multipliers ≥0); stale-closure handling.
- Choice: binary-heap Dijkstra + early exit + bidirectional for long routes.
- Output: path + ETA + confidence (congestion variance).

## 2. Architecture
```
request → graph snapshot (versioned) → Dijkstra (PQ, long, stale-skip) → polyline + ETA
```
- Contraction-hierarchy overlay for inter-district (Dijkstra on core + local).
- `long` ms weights; INF/4; closure = edge removal per version.
- A/B: heap vs naive on dense downtown tile (documented choice).

## 3. War-Story
- Incident: construction API sent −5min "bonus" edge; Dijkstra returned negative-detour loop as fastest.
- Symptom: 0.8% ETAs impossibly low; drivers routed through closed tunnel.
- Root cause: negative weight violated settle-final; no w≥0 assertion.
- Fix: assert + quarantine negatives → Bellman-Ford sidecar (alert) + schema clamp ≥0.
- Lesson: weight contract is a runtime assertion, not a comment.

## 4. Metrics (5k QPS)
| Metric | Before (neg leak) | After | Delta |
|--------|-------------------|-------|-------|
| Impossible ETAs | 0.8% | 0.0% | −100% |
| p99 ETA | 210ms | 88ms | −58% |
| Stale pops | uncounted | 18% skipped | visibility |
| Wrong-tunnel routes | 40/day | 0 | quarantine |
| Early-exit saving | — | 41% | latency win |

## 5. Prevention Checklist
- [ ] `w≥0` assert per snapshot load.
- [ ] Stale-skip + counter (no decrease-key).
- [ ] `long` + INF/4 (overflow review).
- [ ] Early-exit for single-target (measured).
- [ ] Negative quarantine + alert (BF sidecar).
- [ ] Versioned graph (closure consistency).
- [ ] Dense-tile heap-vs-naive note.
- [ ] ETA confidence band (variance).

## 6. What "Good" Looks Like
- Sub-100ms p99, zero impossible ETAs, every detour explainable by weights.

## 7. Stretch
- A* landmark heuristic; live-traffic re-weight pipeline.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- PriorityQueue ordering used by Dijkstra: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Dijkstra invariant + non-negative precondition: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
