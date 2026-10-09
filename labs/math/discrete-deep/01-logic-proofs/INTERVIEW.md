# Interview: Logic and Proofs

## Question 1: Prove or Disprove — "If n² is divisible by 3, then n is divisible by 3"

**Answer:** True. Prove the contrapositive: if n is not divisible by 3, then n² is not divisible by 3. If n ≡ 1 (mod 3), then n² ≡ 1 (mod 3). If n ≡ 2 (mod 3), then n² ≡ 4 ≡ 1 (mod 3). In both cases, n² is not divisible by 3. Therefore, if n² is divisible by 3, n must be divisible by 3.

## Question 2: What Is the Difference Between ∀x ∃y and ∃y ∀x?

**Answer:** ∀x ∃y P(x,y) means "for every x, there exists a y (possibly depending on x) such that P(x,y) holds." ∃y ∀x P(x,y) means "there exists a single y such that for every x, P(x,y) holds." The second is stronger. Example: over the natural numbers, ∀x ∃y (y > x) is true (take y = x+1), but ∃y ∀x (y > x) is false (no natural number is larger than all natural numbers).

## Question 3: How Would You Verify That a Logical Formula Is a Tautology?

**Answer:** For small formulas, construct a truth table and check that the final column is all true. For larger formulas, use a SAT solver: negate the formula and ask the solver if the negation is satisfiable. If unsatisfiable, the original is a tautology. For first-order logic, use a theorem prover (e.g., Vampire, E) or a proof assistant (e.g., Isabelle, Coq).

## Question 4: Explain the Pigeonhole Principle and Give an Application

**Answer:** If n items are placed into m containers and n > m, then at least one container contains more than one item. Application: in any group of 13 people, at least two share a birth month (13 people, 12 months). Another application: if a hash function maps 1000 keys to 100 buckets, at least one bucket contains at least 10 keys.

## Question 5: What Is the Halting Problem and Why Is It Undecidable?

**Answer:** The halting problem asks whether a given program halts on a given input. Turing proved (1936) that no algorithm solves it for all program-input pairs. Proof by contradiction: assume a halts(P, I) function exists. Construct a program D that, given input P, runs halts(P, P) and loops forever if it returns "halts," and halts if it returns "loops." Then D(D) halts if and only if D(D) loops—a contradiction. Therefore, halts cannot exist.
