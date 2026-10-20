# Exercises — Logic and Proofs

Five problems with worked solutions; every figure comes from the
captured runs in CODE_DEEP_DIVE.md. Propositional problems can all be
settled by the 2ⁿ enumeration of lab program 1.

## Problem 1. Validity by Counting

How many valuations of p, q, r satisfy (p→q)∧(q→r)? Is (p→q)∧(q→r) a
satisfiable but not tautological formula?

**Solution**: The run printed 4 of 8. Each valuation with p true and q
false kills it, so survivors are: (p,q,r) with q→r and p→q satisfied —
the 4 rows. Satisfiable (4 > 0) but not a tautology (4 < 8). A formula
being "sometimes true, sometimes false" is exactly the count 0 < k < 2ⁿ.

## Problem 2. The Reversed Chain Fails — Find the Witness

Show (q→r)∧(p→q) ⊢ r→p is not valid and exhibit a falsifying valuation.

**Solution**: The engine printed False with counterexample
p=false, q=false, r=true: both hypotheses hold (q→r is vacuously true
since q is false; p→q is vacuously true since p is false), yet r→p reads
true→false = false. One row defeats an entire candidate proof; validity
must hold on all rows, not most.

## Problem 3. Negate It Correctly

Negate p→q into a 2-variable formula and verify agreement by table.

**Solution**: ¬(p→q) ≡ p∧¬q — the run agreed on all 4 valuations, with
truth visible only at (p true, q false). Read as a diagnosis rule: a
failed implication testifies "the premise held AND the conclusion
failed", never "the premise was weak".

## Problem 4. Why Contradiction Is Legitimate

Prove (p∧¬p)→q is a tautology by counting, and state what this says
about assuming ¬p and deriving absurdity.

**Solution**: The run printed 0 satisfying assignments for p∧¬p, and a
tautology check True for (p∧¬p)→q — an implication with an impossible
antecedent is true on every row (vacuous truth). So assuming ¬p and
reaching ⊥ discharges by negation introduction: the assumption is
unsatisfiable, hence cannot survive in any model of the remaining
premises. Also p→(¬p→q) checked True — same fact, exported form.

## Problem 5. Induction vs Checking, Both Executed

(a) Verify 1+3+...+(2n−1) = n² for n up to 1000 and validate the
induction-step identity. (b) Find the first n where n²−n+41 is
composite, and contrast the two experiments.

**Solution**: (a) The run printed mismatches: 0 on n = 0..1000 and
failed steps: 0 for n²+(2n+1) = (n+1)² on n = 0..999 — base plus step,
executed on witnesses, mirrors the actual proof structure. Sampled
values 49, 100, 10000 match 7², 10², 100². (b) The finder returned 41:
n²−n+41 is prime for n = 0..40 and equals 41² at n = 41. Finite checks
confirm only finitely many instances; the induction step is what lifts
to all n.
