# Math Foundation: Work, Span, and Amdahl
> Parallel cost model: work/span definitions, speedup bounds, Amdahl's law with numbers.

## Definitions
- Work W: total primitive operations across all threads (sequential-equivalent cost).
- Span S: longest dependency chain (time with unbounded processors).
- Parallelism P = W / S: the maximum useful processor count, roughly.
- Speedup on p cores: T1 / Tp, where T1 is the sequential time.

## Counting argument
- Brent-style bound: Tp <= W/p + S (p-way split plus the critical path).
- Speedup <= p always (work conservation) and <= W/S (span limit).
- Overhead (threading, merging) adds to W; contention stretches S.
- Chunked sum: W = Theta(n), S = Theta(n/p + log p) with a tree combine.

## Recurrence
- Parallel divide-and-conquer: W(n) = a*W(n/b) + f(n); S(n) = S(n/b) + g(n).
- Parallel mergesort: W = Theta(n log n), S = Theta(log^2 n)-class with parallel merge.
- Parallel sum: W(n) = 2W(n/2) + O(1) = Theta(n); S(n) = S(n/2) + O(1) = Theta(log n).
- Master theorem still governs W; span follows the critical-path recurrence.

## Derivation of the bound
- Amdahl: fraction s sequential gives speedup <= 1 / (s + (1-s)/p).
- Example: s = 0.1, p = 16 gives at most 1 / (0.1 + 0.05625) = 6.4x.
- Limit p -> infinity: speedup caps at 1/s regardless of cores.
- Lesson: shrink the sequential fraction before buying cores.

## Worked mini-proofs
- Proof 1: speedup <= p from Tp >= W/p (p processors do W work). (3 lines)
- Proof 2: Amdahl bound by splitting time into sequential and parallel parts. (4 lines)
- Proof 3: chunked-sum span from chunk scan plus log-depth combine. (4 lines)

## Exercises with answers
- 1. s = 0.05, p = 8: max speedup? Answer: 1/(0.05+0.11875) = 5.9x.
- 2. W = 10^9, S = 10^6: parallelism? Answer: 1000.
- 3. Why does p = 64 help little when S dominates? Answer: Tp floor is S.

## Pitfalls
- Reporting speedup vs a slow baseline instead of the best sequential code.
- Ignoring merge/combine work in W while counting only the parallel phase.
- Assuming span shrinks with p; span is machine-independent structure.

## Checklist
- Compute W, S, and parallelism for a chunked loop cold.
- Apply Amdahl to a measured sequential fraction with the arithmetic shown.
