# Discrete Mathematics Theory

## 1. Logic and Proofs
**Propositions** are declarative statements with a truth value (true/false).

**Logical connectives:**
- Conjunction (AND, ∧): true iff both operands true
- Disjunction (OR, ∨): true iff at least one operand true
- Negation (NOT, ¬): flips truth value
- Implication (→): P→Q false only when P true, Q false
- Biconditional (↔): true iff both sides share truth value

**Quantifiers:**
- Universal (∀): "for all" — must hold for every element
- Existential (∃): "there exists" — must hold for at least one

**Proof techniques:**
- **Direct proof:** Assume P, derive Q through logical steps
- **Contrapositive:** Prove ¬Q → ¬P instead of P → Q
- **Contradiction:** Assume ¬P, derive a contradiction
- **Induction:** Prove base case, then P(k) → P(k+1)
- **Counterexample:** Disprove ∀ by finding one exception

## 2. Set Theory
A **set** is a collection of distinct objects (elements).

**Operations:**
- Union: A ∪ B = {x : x ∈ A or x ∈ B}
- Intersection: A ∩ B = {x : x ∈ A and x ∈ B}
- Difference: A \ B = {x : x ∈ A and x ∉ B}
- Complement: A' = U \ A (relative to universal set U)
- Cartesian product: A × B = {(a,b) : a ∈ A, b ∈ B}

**Power set:** P(A) = set of all subsets of A; |P(A)| = 2^|A|

**De Morgan's Laws:**
- (A ∪ B)' = A' ∩ B'
- (A ∩ B)' = A' ∪ B'

## 3. Relations and Functions
**Relation:** A ⊆ A × B; relates elements of A to elements of B.

**Properties:**
- Reflexive: ∀a, (a,a) ∈ R
- Symmetric: (a,b) ∈ R ⟹ (b,a) ∈ R
- Transitive: (a,b) ∈ R ∧ (b,c) ∈ R ⟹ (a,c) ∈ R
- Equivalence relation: all three properties; partitions set into equivalence classes

**Function f: A → B:**
- Injective (one-to-one): f(a₁) = f(a₂) ⟹ a₁ = a₂
- Surjective (onto): ∀b ∈ B, ∃a ∈ A with f(a) = b
- Bijective: both injective and surjective; has inverse

## 4. Combinatorics
**Counting principles:**
- Sum rule: |A ∪ B| = |A| + |B| (disjoint sets)
- Product rule: |A × B| = |A| · |B|
- Inclusion-exclusion: |A ∪ B| = |A| + |B| - |A ∩ B|

**Permutations:** Ordered arrangements; P(n,r) = n!/(n-r)!
**Combinations:** Unordered selections; C(n,r) = n!/(r!(n-r)!)

**Binomial theorem:** (x+y)^n = Σ C(n,k) x^(n-k) y^k

**Pigeonhole principle:** If n items go into m containers with n > m, some container holds ≥ 2 items.

## 5. Graph Theory
A **graph** G = (V, E) consists of vertices V and edges E.

**Types:**
- Undirected: edges are unordered pairs
- Directed (digraph): edges are ordered pairs
- Weighted: edges carry numeric labels
- Simple: no loops or multiple edges

**Key concepts:**
- Degree: number of edges incident to a vertex
- Path: sequence of edges connecting vertices
- Cycle: path that starts and ends at same vertex
- Connected: path exists between every pair of vertices
- Tree: connected acyclic graph; |E| = |V| - 1
- Complete graph K_n: every pair connected; |E| = n(n-1)/2
- Bipartite: vertices partition into two sets with edges only between sets

**Euler's formula (planar graphs):** V - E + F = 2

## 6. Number Theory Basics
**Division algorithm:** For integers a, b (b > 0), ∃ unique q, r with a = bq + r, 0 ≤ r < b.

**GCD:** Greatest common divisor; computable via Euclidean algorithm.
**LCM:** Least common multiple; lcm(a,b) = ab/gcd(a,b).

**Modular arithmetic:** a ≡ b (mod n) iff n | (a - b).
- Addition, subtraction, multiplication preserve congruence
- Division requires multiplicative inverse (exists iff gcd(a,n) = 1)

**Fermat's Little Theorem:** If p is prime and p ∤ a, then a^(p-1) ≡ 1 (mod p).

## 7. Recurrence Relations
Define sequences recursively.

**Linear homogeneous with constant coefficients:**
a_n = c₁a_(n-1) + c₂a_(n-2) + ... + c_k a_(n-k)

**Solution method:** Find roots of characteristic polynomial r^k = c₁r^(k-1) + ... + c_k.

**Fibonacci:** F_n = F_(n-1) + F_(n-2), F_0 = 0, F_1 = 1.
Closed form: F_n = (φ^n - ψ^n)/√5 where φ = (1+√5)/2, ψ = (1-√5)/2.
