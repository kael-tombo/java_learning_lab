# VISION — Computational Geometry
> Mastery path. Lab `18-computational-geometry`.

## Where this sits
- Computational Geometry is one tool in the algorithms arsenal: sweeps, orientation predicates, convex hulls.
- Master it and neighboring labs get 2× easier (shared invariants + proof templates).

## Novice → Practitioner → Expert
- Novice (this week): trace by hand; code skeleton with hints; Graham O(n log n), line-sweep intersections O((n+k) log n) memorized.
- Practitioner (this month): bug-free in 20 min; fuzz vs brute force; benchmark plot.
- Expert (this quarter): teach proof; pick optimal variant under constraints; ship production use (GIS, graphics, collision detection).

## 4-week plan
- Wk1: THEORY + E1–E3 daily 30 min; flashcards 10/day.
- Wk2: E4–E5 + QUIZ; benchmark n=1k→1M; write decision rule.
- Wk3: MINI_PROJECT end-to-end; peer review; blog the invariant.
- Wk4: REAL_WORLD_PROJECT design doc + mock interview (30 min whiteboard).

## How to know you are done
- Explain sweep-line order + event queue correctness without notes; derive Graham O(n log n), line-sweep intersections O((n+k) log n) on demand.
- Solve unseen variant in 25 min with tests.
- Name 3 pitfalls + regressions before running code.

## Adjacent labs
- Pair with complexity-analysis, recursion, and one related lab from INDEX.md.
- Revisit after 30/90 days (spaced repetition via FLASHCARDS.md).

## Career signal
- Interviewers listen for invariant-first explanation + complexity proof.
- Portfolio: link MINI_PROJECT benchmark chart + REAL_WORLD_PROJECT metrics.

## Anti-roadmap (what NOT to do)
- Do not memorize code without the invariant; it fails on variants.
- Do not skip benchmarks; asymptotics hide constants that matter in prod.
- Do not jump to advanced variants before the base case is automatic.

## Weekly drills (20 min each)
- Day 1: rewrite core from memory + 3 edge tests.
- Day 2: 10 flashcards + 5 quiz questions out loud.
- Day 3: one proof (Master case or amortized sketch) on paper.
- Day 4: benchmark one size; explain one anomaly.
- Day 5: read one production incident; map to prevention table.

## Milestones and exit interview prep
- M1: whiteboard trace in 8 min with invariant stated first.
- M2: live-code solution with tests in 20 min.
- M3: design-doc review: metrics, rollout, rollback in 10 min.
- Keep a one-page cheat sheet; rewrite it monthly from memory.
