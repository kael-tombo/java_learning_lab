# EXERCISES — High-CPU ReDoS incident

## 1. Reproduce the hang (beginner)
Compile the vulnerable `(a|aa|aaa|aaaa)+b` against `"a"×30 + "c"` with a
stopwatch. Record time. Halve the a-count twice; confirm superlinear
collapse. *Reflection: at what n does it cross your 100 ms budget?*

## 2. Read the flame (beginner)
Profile exercise 1 with async-profiler (`-e cpu`). Identify the top-3
`Pattern$*` frames and their percentages. Match them to the incident's
85% figure (ROOT_CAUSE.md lines 12–21). What would a GC storm look like
instead?

## 3. Fix three ways (intermediate)
Rewrite with (a) atomic group, (b) possessive quantifier, (c) RE2/J-style
linear engine if available. Time all three on the attack input. Verify
identical accept/reject behavior on a 20-case corpus (the fix must not
change the language, only the search).

## 4. Timeout harness (intermediate)
Implement `TimeoutPattern` per SOLUTION.md (watchdog-interrupt style),
then the pool variant. Compare: thread cost, behavior on timeout
(exception vs abandoned worker), and what happens when 50 concurrent
evaluations race. Which would you ship, and why?

## 5. CI gate + canary (advanced)
Build the `ReDoSScanner` into a pre-merge check over the 2,147-pattern
corpus format (generate 200 synthetic patterns, 5 vulnerable). Then write
the canary rollout table (10% → 50% → 100% with CPU/P99 gates from
SOLUTION.md's deployment table) and define the automatic rollback
trigger values.
