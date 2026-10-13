# Mini Project: Chunked Counter
> Two tiny parallel programs that prove their own exactness.

## Background
- Disjoint chunks need no synchronization; shared counters need atomics.
- Join is the correctness primitive: no thread's work counts before it is joined.
- Fixed inputs make parallel results exactly reproducible for testing.
## Goal
Write a chunked parallel sum and an atomic shared counter, each verified exact.
Record timings for 1, 2, 4 threads on a fixed 10M-element array.
## Tasks
1. Fill an int array of size 10M with values 1..10M in order (known total).
2. Sum it with p chunks over disjoint ranges and join-then-add the partials.
3. Assert the parallel total equals n*(n+1)/2 exactly for p = 1, 2, 4.
4. Write the atomic-counter version with 4 threads times 100k increments.
5. Assert the atomic total equals 400000 on every run.
6. Time both versions per thread count and note where speedup flattens.
## Acceptance criteria
- Parallel sums match the closed form for all three thread counts.
- Atomic counter hits 400000 on 5 consecutive runs.
- Timing table shows sublinear scaling with the bottleneck step named.
- Chunk boundaries are asserted disjoint and covering before threads start.
- No shared mutable state exists in the chunked version (state it in the README).
## Pitfalls
- Sharing one accumulator across threads without synchronization.
- Cutting chunks by count instead of by index and dropping the remainder.
- Timing without warmup and reporting JIT noise as speedup.
- Using thread count far above core count and blaming the algorithm.
## Stretch
- Parallel histogram with per-thread maps merged after join.
- False-sharing demo: adjacent vs padded counters with timings.
## Timebox
One afternoon session, roughly 2 hours with timings and write-up.
