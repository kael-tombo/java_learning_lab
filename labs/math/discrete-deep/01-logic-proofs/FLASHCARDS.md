# Logic and Proofs — Flashcards (Verified Numbers)

Numbers below are quoted from the captured runs in CODE_DEEP_DIVE.md.

### Card 1
**Front**: How many valuations does n propositional variables have?
**Back**: Exactly 2ⁿ: 8 for three variables, 1024 for ten, 1048576 for
twenty (printed in the run's cost table). Double, never add.

### Card 2
**Front**: ((p→q)∧(q→r)) → (p→r): valid?
**Back**: Yes — tautology check True on all 8 valuations; hypotheses
hold on exactly 4 of them, and p→r on all 4 survivors.

### Card 3
**Front**: Does the chain work backwards — (q→r)∧(p→q) ⊢ r→p?
**Back**: No: check returned False; falsifying valuation p=false,
q=false, r=true, where both implications are vacuously true and r→p is
not. One row is a complete counterexample.

### Card 4
**Front**: State the negation of p→q exactly.
**Back**: ¬(p→q) ≡ p∧¬q: agreed on all 4 valuations in the run. The
falsifying row is the unique witness "p true, q false".

### Card 5
**Front**: What does truth tell you about (p∧¬p)→q?
**Back**: Tautology, True in the run, because p∧¬p has 0 satisfying
assignments of 8 — an implication with an impossible antecedent is
vacuously true. This is why reductio discharges ⊥.

### Card 6
**Front**: The exported contradiction template?
**Back**: p → (¬p→q), tautology — run printed True. Assume ¬p inside a
proof of p, derive ⊥, and conclude p by negation elimination.

### Card 7
**Front**: Inference vs equivalence: p→q rewritten two ways?
**Back**: p→q equals ¬p∨q (agreement run: True) and
contraposition (¬q→¬p)→(p→q) is a tautology (run: True). But (p→q) does
NOT equal (¬p→¬q) — the agreement check printed False.

### Card 8
**Front**: Weak induction step for odds-sum stated as arithmetic?
**Back**: n² + (2n+1) = (n+1)², an identity the run verified for all n
in 0..999 with zero failed steps; base n=0 reads 0 = 0.

### Card 9
**Front**: Sum of the first n odd numbers?
**Back**: n²: verified on the whole range n = 0..1000 with 0
mismatches; sampled 49 = 7², 100 = 10², 10000 = 100².

### Card 10
**Front**: The classic "checking is not proving" polynomial?
**Back**: n²−n+41: prime for every n = 0..40 (forty straight hits) and
first composite exactly at n = 41, where it equals 41² = 1681
(finder output). Samples never replace the step.

### Card 11
**Front**: Soundness and completeness, one line each?
**Back**: Soundness: each rule preserves truth at every valuation, so
derivability implies validity (induction on derivations).
Completeness: validity implies derivability — every tautology has a
proof, over classical logic.

### Card 12
**Front**: Which logic is decidable and which is only semi-decidable?
**Back**: Propositional (SAT over finite variable sets) is decidable by
the 2ⁿ table; first-order validity is semi-decidable — validities
enumerable, invalidity not — the Church–Turing boundary.
