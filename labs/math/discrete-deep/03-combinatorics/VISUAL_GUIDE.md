# Visual Guide: Combinatorics

## 1. Pascal's Triangle With Combinator Labels

```
n=0                1
n=1              1   1
n=2            1   2   1
n=3          1   3   3   1
n=4        1   4   6   4   1
n=5      1   5  10  10   5   1
            =C(n,0) ... C(n,k) ... C(n,n)
```

Row sums: 1, 2, 4, 8, 16, 32 = 2ⁿ (every subset of an n-set counted once).
Alternating sums: 1 − 3 + 3 − 1 = 0 (count subsets of odd size minus even size).
Hockey stick: 1 + 3 + 6 = 10 = entry two rows below the last (sum of a diagonal = the "handle" tip).
Each interior entry = sum of the two above: 6 = 3 + 3, 10 = 4 + 6.

## 2. Dyck Paths (Catalan C₃ = 5)

Paths from (0,0) to (2n,0) with steps U = (1,1) and D = (1,−1) that never go below height 0. For n = 3 the five are:

```
1) U U U D D D      2) U U D U D D      3) U U D D U D
4) U D U U D D      5) U D U D U D
```

Check path 4's prefix "U D U U" — heights 1, 0, 1, 2, never negative. A candidate like U D D U U is rejected at height −1 (the D after "U D"). Number them by the *first return to height 0*: after the initial U-step, the path splits into a Dyck path of size i−1 and one of size n−i — this split *is* the recurrence Cₙ = Σ Cᵢ₋₁Cₙ₋ᵢ.

## 3. Stars and Bars (5 identical coins into 3 pockets = C(5+3−1, 3−1) = C(7,2) = 21)

Two bars divide five stars into three pockets; the positions of the bars among the 7 slots determine the distribution:

```
* * | * * | * *      = (2, 2, 1)
* * * * * | |        = (5, 0, 0)
| | * * * * *        = (0, 0, 5)
```

Every arrangement of 5 stars and 2 bars is one distribution: choose which 2 of the 7 positions hold bars → C(7, 2) = 21 total.

## 4. Inclusion–Exclusion, Three Sets (Venn Regions)

```
        ┌─────────────────────────────────┐
        │   A\B\C  │  A∩B\C  │   B\A\C   │
        │          ├─────────┤           │
        │  A∩C\B   │ A∩B∩C   │  B∩C\A    │
        │          ├─────────┤           │
        │   C\A\B  │  C∩A\B  │  C∩B\A    │
        └─────────────────────────────────┘
```

To count the union: add the three "single" blobs (each triple-region counted 3×, pair-regions 2×), subtract the three pairwise overlaps (triple now counted 0×... 3 − 3 = 0? recount: triple counted 3 in singles, removed 3 times in pairs → 0), add the center once → each region exactly 1×.

## 5. Lattice Path Counting

Number of monotone paths from (0,0) to (m,n) using steps right/up = C(m+n, m): choose which m of the m+n steps are "right." For (3,3): C(6,3) = 20 paths — draw the 3×3 grid and verify by enumeration if patient; the diagram makes "choose the horizontal steps" literal.

## 6. Growth Comparison (log scale, n = 10)

```
n! = 3,628,800      ███████████████████  (log₁₀ ≈ 6.56)
2ⁿ = 1,024          ████                (log₁₀ ≈ 3.01)
n³ = 1,000          ████                (log₁₀ = 3.00)
n² = 100            █                   (log₁₀ = 2)
```

The visual point: enumeration counts (n!, 2ⁿ) tower over polynomial counts, which is why "count it" and "list it" are different questions in every algorithm you meet later.
