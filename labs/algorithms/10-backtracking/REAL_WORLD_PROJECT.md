# REAL_WORLD_PROJECT — Backtracking in Production: Crew Rostering Assistant
> Production use-case: nurse/crew rostering with hard constraints + timeout guardrails.

## 1. Scenario
- Hospital unit: 40 shifts, 25 staff, coverage + rest + skill constraints.
- Constraint: 30s interactive; best-so-far + gap shown; never hang the UI.
- Choice: backtracking + propagation (forward check) + MRV ordering + memo (subset DP).
- Output: feasible roster + violations (if none) + gap %.

## 2. Architecture
```
demand → propagate → order (MRV) → DFS place/undo → incumbent + timeout → roster
```
- O(1) place/remove (bitsets); copy only at solution; Luby restarts for heavy tails.
- B&B bound (uncovered-shifts lower bound) prunes; DP-memo for repeated sub-masks.
- Timeout → return incumbent + gap (production contract).

## 3. War-Story
- Incident: unbounded search on holiday week (tight constraints) hung UI 11min.
- Symptom: spinner of death; nurses couldn't publish; retry storm doubled load.
- Root cause: no timeout, no incumbent, naive variable order (branching 25 → 2M nodes/min, no prune).
- Fix: 30s cap + MRV + propagation + best-so-far + async worker (UI polls).
- Lesson: search in prod is anytime (good answer fast, better if time) — never exact-or-hang.

## 4. Metrics (40-shift week)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Publish p99 | 11min (hang) | 28s (capped) | −96% |
| Feasible found | 60% (timeout=fail) | 98% | +38pp |
| Nodes/s | 33k (copy-heavy) | 410k (undo) | 12× |
| Rest violations | 4/mo | 0 | propagation |
| Retry storm | 3× load | 0 | async poll |

## 5. Prevention Checklist
- [ ] Timeout + incumbent + gap (always).
- [ ] Undo O(1) (no copy-per-node).
- [ ] MRV/ordering + propagation.
- [ ] Tree-size estimate logged before search.
- [ ] Symmetry breaking where valid.
- [ ] Async (no request-thread search).
- [ ] Must-solve + must-fail fixtures.
- [ ] Violation explainer (which constraint).

## 6. What "Good" Looks Like
- 28s capped, 98% feasible, every roster has a gap + explanation.

## 7. Stretch
- B&B lower-bound tightening; OR-Tools comparison note.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Search/collections scaffolding in Java: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Backtracking + pruning structure: https://en.wikipedia.org/wiki/Backtracking
