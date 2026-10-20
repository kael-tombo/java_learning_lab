# Flashcards — Probability Axioms

## Definition Cards

### Card 1
**Front**: State the three Kolmogorov axioms exactly.
**Back**: (1) P(A) >= 0 for every event A; (2) P(Ω) = 1; (3) for any
disjoint countable family, P(A1 ∪ A2 ∪ ...) = P(A1) + P(A2) + ... .

### Card 2
**Front**: Definition of conditional probability P(A | B)?
**Back**: P(A ∩ B)/P(B), valid whenever P(B) > 0; a fresh measure that
rescales surviving outcomes so their whole mass is 1.

### Card 3
**Front**: Bayes' theorem, formula and reading?
**Back**: P(Ci | A) = P(Ci) P(A | Ci) / Σ_j P(Cj) P(A | Cj); inverts
"effect given cause" into "cause given effect" using the total
probability in the denominator.

### Card 4
**Front**: Law of total probability — statement?
**Back**: For a partition C1,...,Cn with positive probabilities:
P(A) = Σ_i P(Ci) P(A | Ci) — price the event through its disjoint
routes.

### Card 5
**Front**: Define independence of two events; what does it say about
conditionals?
**Back**: P(A ∩ B) = P(A) P(B); equivalently P(A | B) = P(A) when
P(B) > 0, i.e., the conditioning teaches nothing.

## Fact and Formula Cards

### Card 6
**Front**: P(A^c) from the axioms?
**Back**: 1 − P(A); the pair {A, A^c} is disjoint and covers Ω.

### Card 7
**Front**: Inclusion–exclusion for P(A ∪ B)?
**Back**: P(A) + P(B) − P(A ∩ B); for three events add the pairwise sum
and subtract the triple intersection.

### Card 8
**Front**: Union bound?
**Back**: P(∪ Ai) <= Σ P(Ai); from inclusion–exclusion by dropping the
negative correction terms.

### Card 9
**Front**: Multiplication rule?
**Back**: P(A ∩ B) = P(B) P(A | B) = P(A) P(B | A); any two of the three
quantities fix the third.

### Card 10
**Front**: Which complement identity holds inside one conditioning, and
which mixed sum fails?
**Back**: P(A | B) + P(A^c | B) = 1 always; P(A | B) + P(A | B^c) is not
generally 1.

## Judge-the-Number Cards

### Card 11
**Front**: On a die with A = evens, B = {1,2,3}: is P(A) P(B) vs P(A∩B)
independent?
**Back**: 1/4 vs 1/6 — unequal, so dependent; conditioning boosts A.

### Card 12
**Front**: Medical test with sensitivity 99/100, FPR 1/50, prior 1/100:
true positive predictive value?
**Back**: P(D | +) = 99/297 = 1/3 exactly — base rates crush the naive
99/101 intuition.
