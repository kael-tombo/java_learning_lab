# Logic and Proofs — Math Foundation

Numbers below are pasted from the executed runs of CODE_DEEP_DIVE.md;
verification is enumeration, never inspection.

## 1. The Central Sequent, Fully Enumerated

Claim: (p→q) ∧ (q→r) ⊢ p→r. Observed run: the hypotheses (p→q)∧(q→r)
are satisfied at 4 of the 8 valuations, and on all of those the
conclusion p→r is true, so the conditional is a tautology (engine
printed True). The reversed sequent (q→r) ∧ (p→q) ⊢ r→p is not valid:
the run printed False, with counterexample valuation p=false, q=false,
r=true. Enumerating 8 rows is a complete proof in propositional logic —
no proof-search required. ∎

## 2. Negating an Implication the Exact Way

¬(p→q) and p∧¬q agree on all 4 valuations (run printed True, all four
rows shown). The only witness row is p=true, q=false, where both sides
read True. This equivalence is what makes "the theorem failed" mean "the
premise held and the conclusion broke" — the falsifying configuration
has a precise shape, not a vague "something went wrong".

## 3. Contradiction Soundness in Two Counts

- ⊥ = p∧¬p has 0 satisfying assignments (run printed 0 of 8).
- Therefore (p∧¬p)→q is a tautology (run: True): implication with a
  false antecedent is vacuously true on every row.
- Depth form p→(¬p→q): also a tautology (run: True), which is the
  exported version of exactly the same statement.

Contraposition: (¬q→¬p)→(p→q) tautology, run printed True. And the
converse trap: (p→q) vs (¬p→¬q) do NOT agree (run printed False) —
the false converse, checked row-by-row rather than warned about.

## 4. Induction Step as Arithmetic

Target: 1 + 3 + 5 + ... + (2n−1) = n². The step is the identity
n² + (2n+1) = (n+1)², verified on n = 0..999 with zero failures (run:
"failed steps ...: 0"). Full check of the closed form against the
explicit sum matched on all of n = 0..1000 (run: "mismatches: 0").
Sampled witnesses: first 7 odds sum to 49; first 10 to 100; first 100
to 10000. ∎

## 5. Checking Is Not Proving — The Euler Near-Miss

n² − n + 41 is prime for n = 0, 1, 2, ..., 40 — forty consecutive
successes — and the run's counterexample finder prints the first
failure at exactly n = 41, where 41² − 41 + 41 = 1681 = 41², composite. The gap
between "verified 40 cases" and "proved for all n" is not a corner
case; it has a named example. Truth-table projection is the exception:
for propositional formulas, 2ⁿ complete enumeration IS a proof.

## 6. Cost of Complete Verification

Run-printed table: 2¹=2, 2²=4, 2³=8, 2⁵=32, 2¹⁰=1024, 2²⁰=1048576.
Every added variable doubles the table; ten variables is a screenful,
twenty is a multi-megabyte scan. Syllogistic validity for the specific
sequent above needs only n = 3, but unbounded n is what makes SAT
hard in general.
