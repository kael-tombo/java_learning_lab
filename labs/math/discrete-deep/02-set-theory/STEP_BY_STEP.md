# Step-by-Step: Set Operations by Hand

Universe U = {1, 2, 3, 4, 5, 6, 7, 8}
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7}

## 1. Union A ∪ B

Scan A, then add anything in B not already present: {1,2,3,4,5} ∪ {6,7} = {1, 2, 3, 4, 5, 6, 7}.
Count check: |A| + |B| − |A ∩ B| = 5 + 4 − 2 = 7. ✓

## 2. Intersection A ∩ B

Walk the smaller set and keep only members of the other: 4 ∈ A? yes, keep. 5 ∈ A? yes. 6 ∈ A? no. 7 ∈ A? no. → {4, 5}. Size 2. ✓

## 3. Difference A − B

Remove from A every element of B: {1,2,3,4,5} − {4,5} = {1, 2, 3}. Note B − A = {6, 7} ≠ A − B — subtraction of sets is not commutative.

## 4. Complement (A ∪ B)ᶜ

A ∪ B = {1,…,7}, so (A ∪ B)ᶜ = U − {1,…,7} = {8}. Size 1 = 8 − 7. ✓

## 5. Verify De Morgan: (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ

- Aᶜ = {6, 7, 8}, Bᶜ = {1, 2, 3, 8}. Aᶜ ∪ Bᶜ = {1, 2, 3, 6, 7, 8}.
- A ∩ B = {4, 5}, so (A ∩ B)ᶜ = U − {4, 5} = {1, 2, 3, 6, 7, 8}.
- Both sides = {1, 2, 3, 6, 7, 8}. ✓

## 6. Symmetric Difference A Δ B

(A − B) ∪ (B − A) = {1, 3} ∪ {6, 7} = {1, 3, 6, 7}. Equivalent check: (A ∪ B) − (A ∩ B) = {1,…,7} − {4,5} = same. Size 7 − 2 = 5 = |A| + |B| − 2|A ∩ B|.

## 7. Enumerate P({a, b, c}) by Binary Masks

Masks 0…7, bit i set means element i is in the subset (elements ordered a, b, c):

| mask | binary | subset |
|---|---|---|
| 0 | 000 | ∅ |
| 1 | 001 | {a} |
| 2 | 010 | {b} |
| 3 | 011 | {a, b} |
| 4 | 100 | {c} |
| 5 | 101 | {a, c} |
| 6 | 110 | {b, c} |
| 7 | 111 | {a, b, c} |

Eight subsets = 2³. ✓

## 8. Count With Inclusion–Exclusion (Three Sets)

Let |A|=5, |B|=4, |C|=6, |A∩B|=2, |A∩C|=3, |B∩C|=2, |A∩B∩C|=1.
|A ∪ B ∪ C| = (5+4+6) − (2+3+2) + 1 = 15 − 7 + 1 = 9. Always finish with the (+) triple term; forgetting it is the most common sign slip.

## 9. Subset Ladder Check

List A's subsets in size order: 1 of size 0, 5 of size 1, 10 of size 2, 10 of size 3, 5 of size 4, 1 of size 5. Sum: 1+5+10+10+5+1 = 32 = 2⁵. The row of Pascal's triangle at n = 5 must sum to 2ⁿ — a fast self-check on any power-set enumeration.
