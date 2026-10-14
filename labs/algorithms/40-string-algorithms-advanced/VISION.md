# VISION — Advanced String Algorithms
> Direction: from one-pattern search to one-pass multi-pattern scanning plus suffix structures for substring questions.

## Where this sits
- KMP gives O(n+m) single-pattern search via the border (prefix) function; the fallback chain is the whole idea.
- Aho-Corasick lifts KMP to many patterns in O(n+m+z) with failure links and output inheritance; the standard multi-literal engine.
- Suffix arrays (+LCP), suffix automata (<=2n states), and Ukkonen's linear-time SA construction answer substring/enumeration questions around them.

## 4-week direction
- Week 1: hand-build pi for ababaca and the trie+fail links for {he,she,his}; reproduce all lab outputs on paper.
- Week 2: finish MINI_PROJECT; complete the 50-pair cross-check against naive search.
- Week 3: sort banana's suffixes by hand and derive each LCP entry; then run the log scan.
- Week 4: REAL_WORLD_PROJECT review; whiteboard the Aho scan loop with output inheritance in 10 minutes.

## Done criteria
- Derive pi[i] from borders and run the KMP search loop from memory.
- Explain failure links as longest-suffix-that-is-a-trie-prefix with the she/he example.
- Choose KMP vs Aho vs suffix array for a given (patterns, text size, query type) triple.

## Non-coverage
- This lab does not build regex engines, approximate matchers, or compressed indexes (FM-index named only).
- Linear-time SA construction (SA-IS) and Ukkonen's algorithm are conceptual references, not implementations here.
- Suffix automaton construction is described, not built; its state bound is quoted exactly.

## Pitfalls
- Dropping overlapping matches; the ushers case exists to prevent exactly this.
- Rescanning text characters on mismatch; the fallback links are the fix, use them.
- Ignoring chunk seams in streaming scans; boundaries need explicit overlap.

## Adjacent labs
- Pair with 27-suffix-array for deeper suffix structures and 36-bloom-filter-variants for pre-filtering match candidates.
- Revisit when a scanner slows down; the fallback-link and seam checklists come first.

## Weekly drills
- Rebuild pi for ababaca from borders in under 3 minutes.
- Rebuild the {he,she,his} failure links and re-derive she@1 he@2.
- Sort banana's suffixes and recompute each LCP entry by hand.

## Anti-roadmap
- Do not ship a scanner that drops overlapping matches; ushers is the regression test.
- Do not ignore chunk seams; size the overlap from the longest pattern.
