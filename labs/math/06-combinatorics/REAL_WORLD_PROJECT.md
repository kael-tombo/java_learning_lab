# REAL_WORLD_PROJECT — Combinatorics in Production: Test Coverage & Capacity Planner
> Production use-case: ensuring pairwise test coverage without combinatorial explosion.

## 1. Scenario
- Service: QA team configures browsers × OS × roles × locale for an admin app.
- Constraint: 4×3×5×6 = 360 cells is too many to run each release.
- Choice: pairwise (2-way) covering array instead of full cross product.
- Data: `Factor{name, levels}`; coverage tracked per pair.

## 2. Architecture
```
factor matrix → greedy pairwise generator → coverage report → CI gate → run subset
```
- Every pair of (factor,level) co-occurs in ≥1 chosen test.
- Report shows uncovered pairs; empty set = gate passes.

## 3. War-Story (plausible, representative)
- Incident: release ran the "locale × role" submatrix only; a CJK-admin layout bug shipped.
- Symptom: users in ja locale with admin role saw broken dates for a week.
- Root cause: "we tested the important combos" — pair coverage not measured.
- Fix: pairwise generator in CI; a locale×role pair with zero coverage blocks deploy.
- Lesson: combinatorics tells you the floor on what you must run — and that floor is small.

## 4. Metrics (before → after, two releases)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| test cells run | 360 | 38 | −89% |
| pairwise coverage | ~55% | 100% | +45pp |
| pair-related escaped bugs | 3 | 0 | −100% |
| release QA time | 6h | 1.5h | −75% |

## 5. Prevention Checklist
- [ ] Pairwise coverage gate in CI; uncovered pairs listed.
- [ ] When a new factor level appears, regenerate and diff.
- [ ] Document why 2-way (not 3-way); revisit if risk rises.
- [ ] Keep a mapping from pair → test case for bug triage.
- [ ] Randomized pairwise vs greedy comparison quarterly.
- [ ] Track escaped pair-bugs; escalate to 3-way if >0.
- [ ] Bound factor counts in the UI to avoid silent explosion.
- [ ] Dashboard: coverage %, cells run, escape count.

## 6. What "Good" Looks Like
- Release runs ~10% of full matrix with 100% pairwise coverage and no pair escapes.

## 7. Stretch
- Graduate to combinatorial design theory / IPO (in-parameter-order) algorithms.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Covering arrays: https://en.wikipedia.org/wiki/Covering_array
- Combinatorics overview: https://en.wikipedia.org/wiki/Combinatorics
