# Discrete Mathematics Flashcards

## Logic
| Front | Back |
|-------|------|
| Proposition | Declarative statement with a truth value |
| P → Q | Implication; false only when P true, Q false |
| Contrapositive of P → Q | ¬Q → ¬P |
| Converse of P → Q | Q → P |
| Inverse of P → Q | ¬P → ¬Q |
| ∀ | Universal quantifier ("for all") |
| ∃ | Existential quantifier ("there exists") |
| Tautology | Statement always true |
| Contradiction | Statement always false |
| Proof by contradiction | Assume ¬P, derive false |

## Sets
| Front | Back |
|-------|------|
| A ∪ B | Union: elements in A or B |
| A ∩ B | Intersection: elements in both |
| A \ B | Difference: in A but not B |
| |A| | Cardinality (size) of A |
| P(A) | Power set: all subsets of A |
| A × B | Cartesian product: ordered pairs |
| De Morgan's Law | (A∪B)' = A' ∩ B' |
| Empty set ∅ | Set with no elements |
| Subset A ⊆ B | Every element of A is in B |

## Relations & Functions
| Front | Back |
|-------|------|
| Reflexive | (a,a) ∈ R for all a |
| Symmetric | (a,b) ∈ R ⟹ (b,a) ∈ R |
| Transitive | (a,b),(b,c) ∈ R ⟹ (a,c) ∈ R |
| Equivalence relation | Reflexive + symmetric + transitive |
| Injective function | One-to-one; distinct inputs → distinct outputs |
| Surjective function | Onto; every output has a preimage |
| Bijective function | Both injective and surjective |
| Inverse function | f⁻¹ where f⁻¹(f(x)) = x |

## Combinatorics
| Front | Back |
|-------|------|
| P(n,r) | n!/(n-r)! permutations |
| C(n,r) | n!/(r!(n-r)!) combinations |
| Binomial theorem | (x+y)^n = Σ C(n,k)x^(n-k)y^k |
| Pigeonhole principle | n items, m containers, n>m → some container ≥2 |
| Inclusion-exclusion | |A∪B| = |A|+|B|-|A∩B| |
| Pascal's identity | C(n,k) = C(n-1,k-1) + C(n-1,k) |

## Graph Theory
| Front | Back |
|-------|------|
| Vertex (node) | Fundamental unit of a graph |
| Edge | Connection between two vertices |
| Degree | Number of edges at a vertex |
| Path | Sequence of connected edges |
| Cycle | Path returning to start |
| Tree | Connected acyclic graph |
| Complete graph K_n | All pairs connected; n(n-1)/2 edges |
| Bipartite graph | Vertices split into two independent set |
| Planar graph | Can be drawn without edge crossings |
| Euler's formula | V - E + F = 2 (planar) |

## Number Theory
| Front | Back |
|-------|------|
| gcd(a,b) | Largest integer dividing both |
| Euclidean algorithm | Repeated division to find gcd |
| a ≡ b (mod n) | n divides (a-b) |
| Prime | Integer >1 divisible only by 1 and itself |
| Fermat's Little Theorem | a^(p-1) ≡ 1 (mod p) for prime p |
| lcm(a,b) | ab / gcd(a,b) |
