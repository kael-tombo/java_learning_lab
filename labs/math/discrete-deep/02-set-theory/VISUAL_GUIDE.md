# Visual Guide: Set Theory

## 1. Venn Regions for Two Sets

```
   ┌─────────────────── U ───────────────────┐
   │   ┌──────────┐                          │
   │   │ A only   │   A ∩ B    │  B only     │
   │   │ A − B    │    {4,5}   │   B − A     │
   │   └──────────┘            └─────────────┘
   │              (A ∪ B)ᶜ  =  U outside both │
   └──────────────────────────────────────────┘
```

Every element of U lands in exactly one of four regions: A−B, A∩B, B−A, (A∪B)ᶜ. Region arithmetic is the ground truth for union/intersection/complement identities — if an identity disagrees with a region count, the identity (or your algebra) is wrong.

## 2. Subset Lattice for A = {1, 2, 3}

```
              {1,2,3}
           /     |     \
      {1,2}   {1,3}   {2,3}
         \     |     /   \
        {1}  {2}  {3}     ── (drawn compactly: 3 singletons)
              |
             ∅
```

Levels by size: level 0 → 1 set, level 1 → 3, level 2 → 3, level 3 → 1. Moving *up* one edge adds one element — each set has exactly |A| − |S| edges above it. Complement maps level k to level n − k.

## 3. Cantor's Diagonal (Why ℝ Is Uncountable)

Suppose a list of reals in [0,1) exists:

```
r₁ = 0.3 1 7 ...
r₂ = 0.8 4 2 ...
r₃ = 0.1 9 6 ...
        ↑  ↑  ↑   diagonal digits d₁=1, d₂=4, d₃=6
```

Build d by taking diagonal digit i and choosing dᵢ different from it (say dᵢ + 1 mod 10): d = 0.2 5 7 …. The resulting real differs from rᵢ in digit i, so it is not on the list — contradiction. No enumeration covers ℝ; hence |ℝ| > |ℕ|.

## 4. Characteristic-Vector Table (Universe = {1..6})

```
element:   1  2  3  4  5  6
A = {1,2,3,4,5}:   1  1  1  1  1  0
B = {4,5,6,7}∩U:   0  0  0  1  1  1
A ∪ B (OR):        1  1  1  1  1  1
A ∩ B (AND):       0  0  0  1  1  0
A − B (A & !B):    1  1  1  0  0  0
(A ∩ B)ᶜ (NOT):    1  1  1  0  0  1
```

Read columns top to bottom: each column is one element's "membership story."

## 5. Inclusion–Exclusion Overlap Bars

```
|A| = 5   █████████████████████████
|B| = 4            ███████████████████
 overlap = 2        ████████
|A ∪ B| = 5 + 4 − 2 = 7
```

The overlap strip is counted once in each bar; subtracting it leaves each covered unit counted exactly once.

## 6. Cantor Set Construction (Visual of "Nowhere Dense")

Start [0,1]; remove the open middle third (1/3, 2/3). From the two remaining intervals remove their middle thirds (1/9, 2/9) and (7/9, 8/9). Repeat forever: after k stages there are 2ᵏ intervals of length 3^−k. What survives has measure 0 yet is uncountable — the picture that shows "size of the set" and "length covered" are different notions.
