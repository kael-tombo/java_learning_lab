# VISION — Caching Algorithms (LRU / LFU / Belady)
> Mastery path. Lab `21-caching-algorithms`.

## Where this sits
- Caching Algorithms (LRU / LFU / Belady) is one tool in the algorithms arsenal: eviction policies under capacity constraints.
- Master it and neighboring labs get 2× easier (shared invariants + proof templates).

## Novice → Practitioner → Expert
- Novice (this week): trace by hand; code skeleton with hints; O(1) hit/miss for LRU/LFU; competitive ratios (LRU k-competitive) memorized.
- Practitioner (this month): bug-free in 20 min; fuzz vs brute force; benchmark plot.
- Expert (this quarter): teach proof; pick optimal variant under constraints; ship production use (CDNs, CPU caches, DB buffer pools).

## 4-week plan
- Wk1: THEORY + E1–E3 daily 30 min; flashcards 10/day.
- Wk2: E4–E5 + QUIZ; benchmark n=1k→1M; write decision rule.
- Wk3: MINI_PROJECT end-to-end; peer review; blog the invariant.
- Wk4: REAL_WORLD_PROJECT design doc + mock interview (30 min whiteboard).

## How to know you are done
- Explain capacity invariant + recency/frequency order invariant without notes; derive O(1) hit/miss for LRU/LFU; competitive ratios (LRU k-competitive) on demand.
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
