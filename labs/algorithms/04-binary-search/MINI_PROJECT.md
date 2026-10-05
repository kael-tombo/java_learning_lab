# MINI_PROJECT — Binary Search: Boundary Hunter
> Implement + benchmark + visualize. ~3 hours.

## Goal
Build lower/upper-bound toolkit + search-on-answer demo (min feasible `x`);
benchmark vs linear; visualize halving tape.

## Build Steps
1. `Bounds.java`: `anyHit`, `lowerBound`, `upperBound` (half-open, `>>>1`).
2. Apps: first-bad-version (monotonic predicate), `sqrt` via search-on-answer.
3. Visualize: tape with `[lo,hi)` window per probe.
4. Benchmark: n=10⁵..10⁷ probes counted (≤30) vs linear 10⁵ probes.
5. Fuzz: 10⁴ random arrays, cross-check vs linear + `Arrays.binarySearch`.

## Benchmark Table (fill)
| n | binary probes | linear probes | binary ms | linear ms |
|---|---------------|---------------|-----------|-----------|
| 10⁵ | ~17 | 5·10⁴ | | |
| 10⁶ | ~20 | 5·10⁵ | | |
| 10⁷ | ~24 | 5·10⁶ | | |

## Visualize
```
[■■■■□□□□] lo=0 hi=8 mid=4 → [□□□□■■■■] …
```

## Acceptance
- [ ] Probes ≤ ⌊log₂n⌋+1 always (assert). [ ] Fuzz 10⁴ green.
- [ ] Search-on-answer solved (sqrt/first-bad) with predicate count.

## Extensions
- Rotated-array + 2-D matrix search via same invariant.
- Branchless probe experiment (note only).
