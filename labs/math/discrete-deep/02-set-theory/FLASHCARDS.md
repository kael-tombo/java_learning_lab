# Set Theory — Flashcards (Verified Numbers)

Every figure on these cards was printed by a run captured in CODE_DEEP_DIVE.md.

### Card 1
**Front**: How many subsets does an n-element set have?
**Back**: 2ⁿ. Observed at n = 0..4 and 10: 1, 2, 4, 8, 16, 1024. Each
element chooses in/out independently.

### Card 2
**Front**: The finite P({1,2,3}) bijection and its certificate?
**Back**: Subset ↦ membership bits ↦ integer: {1,3} ↦ 101 ↦ 5. The run
decoded all 8 subsets into exactly {0,...,7} and recovered every subset
by round-trip — a two-sided bijection, machine-checked.

### Card 3
**Front**: State both De Morgan laws.
**Back**: (A∪B)ᶜ = Aᶜ∩Bᶜ and (A∩B)ᶜ = Aᶜ∪Bᶜ. Verified over all 64
subset pairs of U = {1,2,3} with 0 failures on either law.

### Card 4
**Front**: Two-set inclusion–exclusion, with the run's witness?
**Back**: |A∪B| = |A| + |B| − |A∩B|; e.g. A = {1,2}, B = {2,3} gives
2 + 2 − 1 = 3, the shared element 2 counted once.

### Card 5
**Front**: Run the three-set census on A={1,2,3,4}, B={3,4,5}, C={4,5,6}.
**Back**: |A∪B∪C| = 6 = 4+5+3 − 1−2−2 + 1. The triple overlap {4}
counts three times, cancels three times, refunds once.

### Card 6
**Front**: What does "countable" require of a set?
**Back**: A surjection from N onto it. N×N qualifies via Cantor pairing
π(i,j) = (i+j)(i+j+1)/2 + j, whose diagonal t = i+j carries t+1 pairs.

### Card 7
**Front**: Values of the Cantor pairing on the walk order?
**Back**: π(0,0)=0, π(1,0)=1, π(0,1)=2, π(2,0)=3, π(1,1)=4, π(0,2)=5,
π(3,0)=6, π(2,1)=7 — all observed. Diagonals 0..5 hold 21 = 1+⋯+6
pairs; the shell i+j ≤ 6 holds 28.

### Card 8
**Front**: Count Q⁺ over numerator ≤ 3, denominator ≤ 4.
**Back**: 9 fractions: 1/1, 1/2, 1/3, 1/4, 2/1, 2/3, 3/1, 3/2, 3/4.
The 12-cell grid loses 3 cells to reduction (2/2, 2/4, 3/3); gcd
filtering is the deduplication that makes Q honest.

### Card 9
**Front**: The exact statement Cantor diagonalization destroys?
**Back**: "There is a surjection N → {0,1}^∞." From any list build d
with d[i] = 1 − sᵢ[i]; d differs from row i at position i for every i,
so the list is incomplete. On the finite mirror the machine produced
11111111 from the 8-row list and confirmed it absent.

### Card 10
**Front**: Why is the diagonal construction per-row immune?
**Back**: Position i of d reads ONLY row i's own i-th entry — no other
row can compensate, since d differs from sᵢ exactly at index i. Any
proposed list, finite or infinite, is refuted on its own terms.

### Card 11
**Front**: Schröder–Bernstein in one line, applied to Q?
**Back**: Injections both ways give a bijection. Q injects into N×N
(reduced pairs), N injects into Q by n ↦ n; hence |Q| = ℵ₀ without
constructing the pairing explicitly.

### Card 12
**Front**: Which is bigger, |N| or |P(N)|, and why?
**Back**: |P(N)| = 2^ℵ₀ > ℵ₀: the diagonal argument rejects any
enumeration of infinite bit strings, and P(N) is in bijection with those
strings — the same doubling that gave 8 = 2³ on finite witnesses.
