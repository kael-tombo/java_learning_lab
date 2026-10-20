# Probability Axioms — Theory

## 1. The Probability Space
A probability space is a triple (Ω, F, P): Ω is the set of outcomes, F is a
σ-algebra of events (contains Ω, closed under complements and countable
unions), and P: F → [0, 1] assigns weights to events. For a finite sample
space, which is the setting of every example in this lab, F can simply be
the full power set 2^Ω and every event is a subset listing its favorable
faces.

## 2. Kolmogorov Axioms — Exact Statement
- Axiom 1 (Nonnegativity): P(A) >= 0 for every event A in F.
- Axiom 2 (Normalization): P(Ω) = 1.
- Axiom 3 (Additivity): for any disjoint family A1, A2, ... (need not be
  finite — countable additivity is part of the axiom):
  P(A1 ∪ A2 ∪ ...) = P(A1) + P(A2) + ... .

Everything else in the theory is a theorem, not an extra assumption.
Three worth naming:

- Complement rule: P(A^c) = 1 − P(A). Apply additivity to the disjoint
  pair {A, A^c} and use P(Ω) = 1.
- Monotonicity: A ⊆ B implies P(A) <= P(B); B = A ∪ (B \ A) disjointly.
- Inclusion–exclusion for a pair: P(A ∪ B) = P(A) + P(B) − P(A ∩ B). The
  disjoint pieces are A, B \ A, so P(A ∪ B) = P(A) + P(B) − P(A ∩ B)
  after bounding the overlap back out. For three events the rule grows a
  plus/minus triple-overlap term, and union bound P(∪Ai) <= Σ P(Ai)
  follows by keeping only the positive corrections.

## 3. Conditional Probability
Definition: for an event B with P(B) > 0,
  P(A | B) = P(A ∩ B) / P(B).
It is a new probability measure: total mass 1 on B, since the rescaling
divides every surviving outcome's weight by P(B). On a finite uniform
space, to condition is to delete the faces outside B and recompute
frequencies on the survivors.

Consequences:
- Multiplication rule: P(A ∩ B) = P(B) · P(A | B) = P(A) · P(B | A).
- Within one fixed conditioning, complements behave: P(A | B) +
  P(A^c | B) = 1. But P(A | B) + P(A | B^c) is NOT generally 1 — mixing
  two conditionings is the classic beginner's error.
- Any two of P(A ∩ B), P(A | B), P(B) determine the third.

## 4. Total Probability and Bayes
A partition C1, ..., Cn is a disjoint family covering Ω with each
P(Ci) > 0. The law of total probability: P(A) = Σ_i P(Ci) P(A | Ci) —
split on the partition, average the conditionals. Bayes' theorem then
inverts the conditioning:
  P(Ci | A) = P(Ci) P(A | Ci) / Σ_j P(Cj) P(A | Cj).
The denominator is exactly the total-probability expression; the theorem
turns "evidence given hypothesis" numbers into "hypothesis given
evidence" numbers.

## 5. Independence
Events A, B are independent when P(A ∩ B) = P(A) P(B), which for
P(B) > 0 is the same as P(A | B) = P(A): knowing B teaches nothing about
A. Independence of n events requires the product rule for every subset
of them; pairwise independence alone is strictly weaker. Dependence
created by conditioning is also real: A, B independent does not make
them independent conditional on a third event (and non-independent pairs
can become conditionally independent — the mechanism behind Simpson-type
reversals).

## 6. Why These Axioms And No Others
Each axiom encodes a frequency intuition that any limit of long-run
relative frequencies must obey: frequencies are nonnegative, obey
"whole = sum of disjoint parts", and equal 1 for the certain event. If a
proposed assignment fails any axiom it cannot be a long-run frequency,
so the axioms are the complete story for coherent reasoning about
chance; the rest of this academy builds distributions, limits, and
inference on exactly this substrate.
