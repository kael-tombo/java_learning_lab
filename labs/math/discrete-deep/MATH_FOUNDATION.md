# Discrete Mathematics Foundation

## 1. Axiomatic Systems
Discrete math rests on axioms — statements accepted without proof. From axioms, we derive theorems via rules of inference.

**Peano Axioms (for ℕ):**
1. 0 is a natural number
2. Every natural number has a successor
3. 0 is not the successor of any natural number
4. Different numbers have different successors
5. **Axiom of Induction:** If a set contains 0 and the successor of every element, it contains all natural numbers

## 2. Proof Techniques — Formal Structure

**Direct Proof (P → Q):**
1. Assume P
2. Apply definitions, axioms, previously proven theorems
3. Derive Q through valid inference steps

**Proof by Contrapositive (¬Q → ¬P):**
Logically equivalent to P → Q. Useful when ¬Q gives more to work with.

**Proof by Contradiction:**
1. Assume ¬P
2. Derive a statement R ∧ ¬R (contradiction)
3. Conclude P must be true

**Mathematical Induction:**
1. **Base case:** Prove P(0) or P(1)
2. **Inductive hypothesis:** Assume P(k) for arbitrary k
3. **Inductive step:** Prove P(k) → P(k+1)
4. **Conclusion:** P(n) holds for all n ≥ base

**Strong Induction:**
Assume P(0) ∧ P(1) ∧ ... ∧ P(k) to prove P(k+1).

## 3. Set Theory Axioms
**Zermelo-Fraenkel (ZF) axioms** formalize sets:
- **Extensionality:** Sets with same elements are equal
- **Pairing:** For any a, b, there exists {a, b}
- **Union:** For any set of sets, their union exists
- **Power set:** For any set, its power set exists
- **Infinity:** An infinite set exists
- **Specification:** Defining subsets via properties

## 4. Countable and Uncountable Sets
**Countable:** A set is countable if it is finite or has the same cardinality as ℕ (can be listed as a sequence).

**Theorem:** ℚ is countable (Cantor's diagonal enumeration).

**Theorem (Cantor):** ℝ is uncountable. Proof by diagonalization: assume a list of all reals, construct a real differing from the nth entry in the nth decimal place.

## 5. Graph Theory Theorems
**Handshaking Lemma:** Σ deg(v) = 2|E|. Proof: each edge contributes 2 to the total degree count.

**Tree Characterization:** For a graph G with n vertices, any two of the following imply the third:
- G is connected
- G is acyclic
- G has n-1 edges

**Euler's Formula:** For a connected planar graph, V - E + F = 2. Proof by induction on edges.

**Kuratowski's Theorem:** A graph is planar iff it contains no subdivision of K_5 or K_(3,3).

## 6. Number Theory Theorems
**Division Algorithm:** For a, b ∈ ℤ, b > 0, ∃ unique q, r with a = bq + r, 0 ≤ r < b.

**Bézout's Identity:** gcd(a,b) = ax + by for some integers x, y. Proof via Euclidean algorithm.

**Fundamental Theorem of Arithmetic:** Every integer > 1 factors uniquely into primes (up to ordering).

**Chinese Remainder Theorem:** If gcd(m,n) = 1, the system x ≡ a (mod m), x ≡ b (mod n) has a unique solution modulo mn.

## 7. Combinatorial Identities
**Binomial Theorem:** (1+x)^n = Σ C(n,k)x^k. Proof by induction or combinatorial counting.

**Vandermonde's Identity:** C(m+n,r) = Σ C(m,k)C(n,r-k).

**Catalan Numbers:** C_n = C(2n,n)/(n+1) counts valid parenthesis sequences, binary trees, and Dyck paths.
