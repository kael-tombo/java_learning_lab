# Common Mistakes: Combinatorics

## 1. Permutations Where Combinations Belong (or Vice Versa)

"How many ways to choose 2 of {A, B, C}?" → C(3,2) = 3 ({AB, AC, BC}). "How many ways to *seat* 2 of {A, B, C}?" → P(3,2) = 6 (AB and BA differ). Ask literally: does order change the outcome? Teams chosen but then not ranked → combination; a PIN with repeated digits allowed → permutation with repetition 10⁴ = 10000, not P(10,4) = 5040.

## 2. Using n! When Repetition Is Allowed

Distinct arrangements of *n* distinct items = n!. Arrangements of length k from n distinct items with repetition = nᵏ. Arrangements without repetition = n!/(n−k)!. Choosing a 4-digit lock code: 10⁴ (repeats allowed) not 10·9·8·7.

## 3. Inclusion–Exclusion Sign Errors

For "at least one property holds": |A ∪ B ∪ C| = Σ singles − Σ pairs + triple. The sign is (−1)^(r+1) for r-wise intersections — it alternates, ending positive for an odd number of sets and negative for even. Typical slip: stopping after subtracting pairwise terms and forgetting to add back |A ∩ B ∩ C|, which was subtracted three times minus... (it was counted 3× in singles, removed 3× in pairs, so it sits at 0 and must be added).

## 4. Counting Cases That Are the Same Object

Distributing 5 identical coins into 3 pockets: the outcomes {5,0,0} and {0,5,0} differ by pocket, but two pennies are indistinguishable — you must not multiply by 5!. Whether objects are *labeled* (pockets, distinct people) or *unlabeled* (identical stars) changes the answer from nᵏ or C(n+k−1, k) dramatically. Stars and bars: identical balls into k labeled boxes = C(n+k−1, k−1), not kⁿ.

## 5. Ignoring the Complement on "At Least One"

"At least one match among n people" is 1 − (no matches), where no-matches counts cleanly. Computing "at least one" directly forces you through every nonempty subset — exponentially many terms. For n = 4 with 3 properties: |A∪B∪C| directly needs 7 cases; the complement needs 1 product (|Aᶜ||Bᶜ|... only if independent).

## 6. Off-by-One in Catalan and Fibonacci Indexing

C₀ = 1, C₁ = 1, C₂ = 2, C₃ = 5, C₄ = 14. Dyck paths of *semilength* n, triangulations of an (n+2)-gon, and binary trees with n internal nodes are all Cₙ — mixing "n factors" with "n nodes" shifts you one place. Similarly aₙ = aₙ₋₁ + aₙ₋₂ needs *two* base cases; supplying one invites a wrong seed into the whole table.

## 7. Dividing by k! Too Early or Too Late

Dividing by the symmetry factor is valid only when you have already counted *ordered* arrangements of *indistinguishable* items. Counting arrangements of the letters of "BOOK" as 4! and then dividing by 2! for the O's gives 12 — correct — but dividing twice (once because O's repeat, once again "to be safe") gives 6, wrong.

## 8. Assuming Terms Are Independent in Probability

P(A and B) = P(A)P(B) only when independent. Drawing two cards: the second draw's space shrinks (dependent). The classic wrong answer to the shared-birthday question uses 365ⁿ as if each draw were with replacement and then divides as if independent — the correct count of *no*-collision tuples is 365·364·…·(365−n+1)/365ⁿ.
