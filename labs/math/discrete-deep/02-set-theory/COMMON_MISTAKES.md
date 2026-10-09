# Common Mistakes: Set Theory

## 1. Confusing ∈ with ⊆

`x ∈ A` means x is one element of A. `A ⊆ B` means every element of A is an element of B. Writing `3 ∈ {1, 2, 3}` is correct; writing `{3} ∈ {1, 2, 3}` is not — `{3}` is not an element of that set, though `{3} ⊆ {1, 2, 3}` is true. A related trap: `∅ ∈ {∅}` is true and `∅ ⊆ {∅}` is also true, but `∅ ∈ ∅` and `∅ ⊆ ∅` differ — only the second is true (everything is a subset of itself; nothing is an element of the empty set).

## 2. Assuming A − B = B − A

Set difference is not commutative. With A = {1, 2, 3} and B = {3, 4}: A − B = {1, 2} while B − A = {4}. They are equal only when A = B. The commutative operation on two sets is the *symmetric difference* A Δ B = (A − B) ∪ (B − A). If your code asserts `aMinusB.equals(bMinusA)` outside of A.equals(B), the assertion is wrong.

## 3. De Morgan Errors

De Morgan's laws apply to the *complement*, not to difference: (A − B)ᶜ = Aᶜ ∪ B. Students frequently write (A − B)ᶜ = Aᶜ − Bᶜ, which is false. The correct duals:

- (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
- (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ

A common coding bug negates only one disjunct: to express "not (underage or citizen)" a developer writes `age >= 18 && citizen`, which is wrong. Apply De Morgan first: ¬(age < 18 ∨ citizen) = (age ≥ 18) ∧ ¬citizen. Flip both disjuncts and swap ∨ for ∧; flipping the operator without flipping the operands is the classic half-done negation.

## 4. Mixing Up ∅ and {∅}

The empty set has 0 elements. {∅} has exactly 1 element, namely ∅. P(∅) = {∅} (one subset), while P({∅}) = {∅, {∅}} (two subsets). Confusing these flips base cases in recursive constructions.

## 5. Forgetting the Power-Set Size Formula

|P(A)| = 2^|A|, not |A|² or |A|^|A|. For A = {1,2,3} the eight subsets are ∅, three singletons, three pairs, and A itself.

## 6. Treating Union/Intersection as "Add and Multiply"

|A ∪ B| = |A| + |B| − |A ∩ B| (inclusion–exclusion). |A ∩ B| is not |A|·|B| unless A and B are independent in a probabilistic sense, which is not a property of sets at all. Always subtract the overlap when counting a union.

## 7. Assuming Intersection Is Never Empty

The empty set is a perfectly good subset of every set. A ∩ B = ∅ says nothing is wrong; your code must branch on the empty case rather than assume at least one common element exists.

## 8. Cartesian Product Non-Commutativity

A × B ≠ B × A unless A = B or one is empty. The ordered pair (a, b) records position; {{a, b}, {a}} (Kuratowski) still distinguishes a from b because the outer structure differs.
