# Reflection: Fork-Join Pool

## Check your model

1. Without looking: which deque end does the owner use, which does the thief
   use, and what does each choice optimize?
2. Why does fork-left/compute-right/join need only one fork? What does the
   second fork in the naive version cost?
3. A teammate says "`join()` waits." What is the precise correction, and why
   does it prevent the naive deadlock?
4. Your pool reports size 3, parallelism 2 during a blocking phase. Leak or
   compensation? What call produced the +1?
5. When is FJ the *wrong* tool? Name all three workload shapes and the
   replacement for each.

## Connect to your code

1. Find one parallel stream. Is its pipeline CPU-bound? If any stage blocks,
   which pool must it move to?
2. Find one recursive aggregation (tree walk, chunked sum). Does its threshold
   put leaves in the 1–10µs band? Compute `2n/t` and tasks-per-worker.
3. Find one ad-hoc `new ForkJoinPool` or `newFixedThreadPool` used for
   recursion. Could try-with-resources own its lifecycle (Java 19+)?

## Predict, then verify

1. Predict common-pool parallelism on this machine (`CPUs − 1`), then print
   `commonPool().getParallelism()` and the plain-ctor value. Record both.
2. Predict the faster threshold for 1M elements: 100 vs 10K. Run the sweep and
   compare task counts against `2n/t`.
3. Predict `getPoolSize()` during a `ManagedBlocker.sleep(500)` in a pool of
   2. Run the EXERCISES.md probe and confirm 2→3.

## One-paragraph write-up

Explain work-stealing to a junior using deque ends, helping joins, and one
threshold number from your sweep. Method names (`fork`/`join`/`invoke`,
`managedBlocker`) and measured counts only — no "cutting-edge" adjectives.
