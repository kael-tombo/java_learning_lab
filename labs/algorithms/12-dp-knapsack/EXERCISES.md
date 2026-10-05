# EXERCISES — 0/1 Knapsack
> Implement + trace + edge cases. Java templates included.

## Level 1 — Mechanics
### E1 2-D DP (25 min)
```java
public static int knap2D(int[] w, int[] v, int W) {
    // TODO: dp[n+1][W+1]; dp[i][cap]=max(skip, take); return dp[n][W]
    return 0;
}
```
- Trace `(w=[2,3,4],v=[3,4,5],W=5)`: fill 4×6 table, answer 7.

### E2 1-D optimized (20 min)
```java
public static int knap1D(int[] w, int[] v, int W) {
    // TODO: dp[W+1]; for each item: for cap=W..w[i]: dp[cap]=max(...)
    return 0;
}
```
- Show descending trace equals last row of 2-D. Then demo ascending bug (over-take).

### E3 Reconstruction (15 min)
```java
public static List<Integer> chosen(int[] w, int[] v, int W) {
    // TODO: walk full table back; take iff dp[i][c]!=dp[i-1][c]
    return null;
}
```
- Expect `[0,1]` on trace above; test tie (either valid, validator checks value+weight).

## Level 2 — Edge Cases
### E4 Zero/edge capacities
- `W=0` → 0; empty items → 0; item `wᵢ>W` skipped; `wᵢ==0,vᵢ>0` → always take (guard loop).

### E5 Fractional trap
- Instance where greedy-by-ratio fails 0/1: craft `(W=50: (10,60),(20,100),(30,120))` greedy vs optimal. Record gap.

### E6 Big W
- `W=10⁹` toy → OOM/timeout demo; note need for meet-in-middle/FPTAS (MATH_FOUNDATION).

## Level 3 — Trace Tables
| i\cap | 0 | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1(2,3)| 0 | 0 | 3 | 3 | 3 | 3 |
| 2(3,4)| … | … | … | … | … | … |
- Complete rows; circle taken cells.

## Level 4 — Property Tests
- P1: 1-D == 2-D value on 50 random small instances.
- P2: validator: `Σw≤W` and `Σv==reported`; brute `2ⁿ` for `n≤20`.
- P3: ascending-1D ≥ correct (demonstrates over-count = unbounded).

## Level 5 — Stretch
- S1 Unbounded variant (ascending, correct there); compare answers.
- S2 Meet-in-middle `n=34` sketch.
- S3 Cargo packer (see MINI_PROJECT): pack mock manifest, print utilization %.

## Submission Checklist
- [ ] 2-D + 1-D + reconstruction.
- [ ] Ascending-bug demo + fractional trap.
- [ ] Random vs brute-force validation.
- [ ] `O(nW)` pseudo-poly note.
