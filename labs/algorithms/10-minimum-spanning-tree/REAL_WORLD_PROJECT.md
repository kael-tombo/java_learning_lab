# REAL_WORLD_PROJECT — MST in Production: Fiber Rollout Planner
> Production use-case: cheapest fiber to 1,200 sites (Kruskal + Prim cross-checked).

## 1. Scenario
- Telco plans 1,200 towns; trenching costs per segment (surveyed, some negative credits).
- Constraint: board-approved total ±2%; explainable per-edge (which cut it won).
- Choice: Kruskal (sparse quotes) + Prim verify; DSU with halving+rank; `long` cents.
- Output: build order + total + savings vs star-from-HQ + per-edge cut note.

## 2. Architecture
```
surveys → edge list → Kruskal (+Prim verify, weight-equal assert) → phased build
```
- Forest handling (islands = separate phases); tie policy documented (any valid).
- Directed-feasibility precheck (MST needs undirected — refuse directed segments).
- Second-best query for "what if segment X blocked" (swap analysis).

## 3. War-Story
- Incident: `int` total overflowed at $21M (cents × segments) → negative total approved deck.
- Symptom: board pack showed −$8M (wrap); build paused 3 weeks for re-audit.
- Root cause: int cents sum + no disconnected check (2 islands silently dropped).
- Fix: `long` + MSF phase report + per-edge cut ledger (auditable).
- Lesson: MST output is money — totals, forests, and cuts are all audited.

## 4. Metrics (1,200 sites, 8k segments)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Total error | −$29M (wrap) | exact | fixed |
| Plan vs star | unknown | −34% ($9.1M saved) | +savings |
| Islands missed | 2 | 0 (phased) | coverage |
| Verify (Kruskal vs Prim) | none | 100% equal | guard |
| Approval cycle | 6 wks | 2 wks | −67% |

## 5. Prevention Checklist
- [ ] `long` money + overflow test.
- [ ] Forest/MSF explicit (no silent drop).
- [ ] Undirected validation (refuse directed).
- [ ] Cut ledger per taken edge (audit).
- [ ] Dual-algorithm verify on release.
- [ ] Tie policy documented.
- [ ] Second-best ready for blocks.
- [ ] Negative-credit handling tested.

## 6. What "Good" Looks Like
- Exact total, phased islands, $9M savings with per-edge proof.

## 7. Stretch
- Degree-constrained (crew limits) heuristic + Steiner note for new towns.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Sort + PQ contracts behind Kruskal/Prim: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- MST cut/cycle properties: https://en.wikipedia.org/wiki/Minimum_spanning_tree
