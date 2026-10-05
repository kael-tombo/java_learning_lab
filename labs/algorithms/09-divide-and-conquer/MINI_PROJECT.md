# MINI_PROJECT — Divide and Conquer: Inversion Lab + Parallel
> Implement + benchmark + visualize. ~3 hours.

## Goal
Count inversions (merge-based) with split/combine diagram, cross-check vs brute force,
and parallelize halves with ForkJoin measuring speedup + span.

## Build Steps
1. `InvLab.java`: buffer-once count + brute `O(n²)` oracle.
2. Visualize: recursion tree with `[lo,mid,hi] cross=+k` annotations (n=8).
3. Benchmark: n=10⁴..10⁵ merge vs brute (brute only to 10⁴); ratios ~2.1.
4. Parallel: ForkJoin halves; report speedup on 4–8 cores + span note.
5. Fuzz: 200 random arrays value-match vs brute.

## Benchmark Table (fill)
| n | merge ms | brute ms | parallel ms | speedup |
|---|----------|----------|-------------|---------|
| 10k | | | | |
| 40k | | | | |
| 80k | | | | |

## Visualize
```
[0,8] cross=5 ├[0,4] cross=2 └[4,8] cross=1 …
```

## Acceptance
- [ ] 200/200 fuzz match. [ ] Tree diagram included.
- [ ] Speedup + span interpretation (not just wall ms).

## Extensions
- Quickselect median (avg O(n)) added with same harness.
