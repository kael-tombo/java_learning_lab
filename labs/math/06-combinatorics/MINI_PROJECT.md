# MINI_PROJECT — Combinatorics: Counting Toolkit & Coverage Planner
> Implement + count + compare. ~3 hours.

## Goal
Build a CLI library for nPr, nCr, stars-and-bars, inclusion–exclusion, and grid paths,
with BigInteger exactness and cross-checks against brute-force enumeration.

## Build Steps
1. `Count.java`: P(n,k), C(n,k) via multiplicative loop (no factorial overflow).
2. `StarsBars.java`: count positive/nonnegative solutions to x₁+…+xₖ=n.
3. `InclusionExclusion.java`: count integers ≤n divisible by none of a,b,c.
4. `GridPaths.java`: C(m+n, m) vs DP table — assert equal.
5. Driver: 15 cases, brute-force enumerate for n≤10, assert formula==enumeration.

## Sample Output
```
C(10,3)=120, brute=120 ✓
paths(3x3)=C(6,3)=20, dp=20 ✓
≤100 divisible by none of 2,3,5: 26
C(5,k) sum=32=2^5 ✓
```

## Benchmark Table (fill)
| n | k | C(n,k) compute ms | brute ms |
|---|---|-------------------|----------|
| 20 | 10 | | |
| 30 | 15 | | |
| 40 | 20 | | |

## Acceptance
- [ ] Formula equals brute force for all small cases.
- [ ] BigInteger path handles n=100.
- [ ] Inclusion–exclusion matches sieve count.

## Extensions
- Catalan table generator C(2n,n)/(n+1).
- Test-coverage estimator: minimum cases to cover pairs.
