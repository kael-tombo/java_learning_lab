# EXERCISES — DP Basics
> Implement + trace + edge cases. Java templates included.

## Level 1 — Mechanics
### E1 Three Fib forms (25 min)
```java
public static long fibNaive(int n) { /*TODO direct recurrence*/ return 0; }
public static long fibMemo(int n) { return dfs(n, new long[n+1]); /*TODO*/ }
public static long fibTab(int n) { /*TODO two vars*/ return 0; }
```
- Trace `n=5` call tree (naive 15 nodes) vs memo 6 states.
- Time `n=40`: naive hangs, memo/tab instant — record ms.

### E2 Climbing stairs (15 min)
```java
public static long ways(int n) { /*TODO dp[0]=1,dp[1]=1*/ return 0; }
```
- Table `n=0..4 → 1,1,2,3,5`. Explain why `ways(0)=1` (empty way).

### E3 Min-cost variant (15 min)
- `cost[i]` stairs: `dp[i]=cost[i]+min(dp[i-1],dp[i-2])`. Trace `[10,15,20]` → 15.

## Level 2 — Edge Cases
### E4 Bases + negatives
- `n=0,1` exact; `n<0` → throw `IllegalArgumentException`. Document.

### E5 Overflow / mod
- `fib(47)` overflows int → use long; `fib(100)` needs mod `1e9+7` or BigInteger. Show both.

### E6 Depth risk
- Memo recursion at `n=10⁴` → `StackOverflowError`; rewrite iterative. Note limit.

## Level 3 — Trace Tables
| n | dp[n] (ways) | deps used |
|---|--------------|-----------|
| 0 | 1 | base |
| 1 | 1 | base |
| 2 | 2 | 1+1 |
| 3 | 3 | 2+1 |
| 4 | 5 | 3+2 |
- Extend to 6; verify with code.

## Level 4 — Property Tests
- P1: memo==tab for `n=0..30`.
- P2: `ways(n)==fib(n+1)` identity check.
- P3: mod variant: `(a+b)%M` applied per step, no overflow.

## Level 5 — Stretch
- S1 Fast doubling `O(log n)` fib; compare at `n=10⁶` (mod).
- S2 House-robber DP (same skeleton, new recurrence).
- S3 Visualize call DAG (see MINI_PROJECT): count saved recomputations.

## Submission Checklist
- [ ] Three forms + timings.
- [ ] Base/overflow/depth tests.
- [ ] Identity + mod properties.
- [ ] `O(n)`/`O(1)` space notes.
