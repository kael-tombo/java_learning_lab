# Common Mistakes: Logic and Proofs

## 1. Confusing the Converse with the Inverse

Students frequently confuse "If P then Q" with its converse "If Q then P." These are not logically equivalent. "If it rains, the ground is wet" does not imply "If the ground is wet, it rained" (someone could have watered the lawn).

The contrapositive "If not Q then not P" *is* equivalent to the original implication, and this equivalence is the basis of proof by contrapositive.

## 2. Affirming the Consequent

A common invalid inference: "If P then Q. Q is true. Therefore P is true." This is a logical fallacy. From "If x = 2, then x² = 4" and "x² = 4", you cannot conclude x = 2 (x could be −2).

## 3. Denying the Antecedent

Similarly invalid: "If P then Q. P is false. Therefore Q is false." From "If x = 2, then x² = 4" and "x ≠ 2", you cannot conclude x² ≠ 4.

## 4. Misusing Quantifiers

Confusing ∀ (for all) with ∃ (there exists) is a frequent error. "∀x ∃y: y > x" (for every x there exists a larger y) is true over the integers, but "∃y ∀x: y > x" (there exists a y larger than every x) is false. The order of quantifiers matters.

## 5. Proof by Example

Showing that a statement holds for one or a few examples does not prove it universally. To disprove a universal statement, a single counterexample suffices; to prove one, a general argument is required.

## 6. Circular Reasoning

Assuming what you are trying to prove, often in disguised form. "This algorithm is correct because it produces correct results" is circular. Each step in a proof must follow from previously established facts.

## 7. Confusing Necessary and Sufficient Conditions

"P is necessary for Q" means Q → P. "P is sufficient for Q" means P → Q. Being a square is sufficient but not necessary for being a rectangle. Students often reverse these.

## 8. Misapplying De Morgan's Laws to Quantifiers

¬(∀x P(x)) is equivalent to ∃x ¬P(x), not ∀x ¬P(x). "Not all birds can fly" means "there exists a bird that cannot fly," not "all birds cannot fly."
