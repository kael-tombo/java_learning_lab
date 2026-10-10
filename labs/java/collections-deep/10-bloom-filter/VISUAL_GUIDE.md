# Visual Guide: Bits, Curves, Unions

## Toy state (m=16, k=2; apple {3,9}, pear {9,14})

```
bit:  0 1 2 3 4 5 6 7 8 9 a b c d e f
      . . . █ . . . . . █ . . . . █ .
              ↑apple      ↑shared       ↑pear
fig {9,e} → both █ → FALSE POSITIVE
melon {5,..} → bit 5 empty → ABSENT (one zero suffices)
```

## FPR vs k at canonical load (n=10000, m=95851)

```
p
10%│× k=1
 2%│    × k=3
 1%│        × k=5  ★ k=7 (min)  × k=10 (rises: saturation)
    └──────────────────────────────── k →
     1   3   5   7   10
```

The U-shape: too few checks (left) vs too many bits set per add (right).

## Half-full at optimum

```
At k=(m/n)·ln2: fraction of zeros = e^(−kn/m) = 1/2
[████████░░░░░░░░]  ~50% set — the information-theoretic sweet spot
p = (1/2)^k: each extra hash halves FPR (k=7 → ~0.8–1%)
```

## Union = OR

```
A:  █ . █ . . .      B:  . █ █ . . .
OR: █ █ █ . . .  =  filter(apple ∪ pear) exactly
```

Requirement: identical (m, k, hash). OR-ing mismatched filters is garbage
with the shape of an answer — check parameters first (Guava does).
