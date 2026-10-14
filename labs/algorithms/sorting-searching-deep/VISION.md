# VISION — Sorting and Searching Deep Track
> Direction: from textbook sorts to structures with stronger guarantees — linear select, external construction, and universe-bounded speed.

## Where this sits
- Selection needs Omega(n) reads; median-of-medians attains O(n) worst case where quickselect only averages it.
- Suffix arrays turn substring search into binary search; doubling builds in O(n log n), linear methods exist past this track.
- Integer keys in bounded universes admit O(log log U) via van Emde Boas thinking; external merge moves sorting past RAM.
- Each method answers a different bottleneck: adversarial pivots, substring queries, memory walls, universe structure.

## 4-week direction
- Week 1: hand-run median-of-medians on 15 elements; reproduce the pivot choice without code.
- Week 2: finish MINI_PROJECT; verify every structure against its naive oracle (sort, TreeSet, in-memory sort).
- Week 3: push one input past RAM (external merge) and one past quickselect comfort (adversarial select); record both.
- Week 4: REAL_WORLD_PROJECT review; whiteboard the O(log log U) recursion idea in 10 minutes.

## Done criteria
- Explain why median-of-medians groups of 5 give linearity (the 30/70 split sketch) without notes.
- Build a suffix array by doubling on a fresh word and verify against naive order.
- Choose naive vs doubling vs linear SA construction for a given (n, alphabet, memory) triple.

## Non-coverage
- This track does not implement linear-time SA (SA-IS), fusion trees, or full y-fast tries; each is named with its trigger and complexity.
- Cache-oblivious algorithms are referenced, not benchmarked.
- No claim that vEB wins outside bounded universes with real constants; TreeSet comparisons stay in the report.

## Pitfalls
- Hiding a simplification (e.g. of vEB) without labeling it; oracles catch lies, labels prevent them.
- Benchmarking select only on random pivots; adversaries are the point of the guarantee.
- Forgetting the memory cap that justifies external merge; without a cap the comparison is theater.

## Adjacent tracks
- Pair with sorting for foundations and 40-string-algorithms-advanced for the substring-query applications.
- Revisit when guarantees matter more than averages: adversaries, memory walls, bounded universes.

## Weekly drills
- Re-run median-of-medians on 15 elements and recompute the 30/70 split sketch.
- Rebuild banana's suffix array by doubling (not naive sort) on paper.
- State the vEB recurrence T(U) = T(sqrt(U)) + O(1) and solve it to O(log log U).

## Anti-roadmap
- Do not present a simplified structure under the full name; label deviations.
- Do not benchmark select on random data only; the killer input is the exam.
