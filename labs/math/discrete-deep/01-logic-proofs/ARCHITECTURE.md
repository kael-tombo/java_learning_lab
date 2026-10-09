# Architecture: Logic and Proofs

## Where Logic Fits in the Stack

Logic is the foundation layer of the entire computing stack:

```
┌─────────────────────────────────────┐
│  Applications (AI, verification)    │
├─────────────────────────────────────┤
│  Programming languages (type systems)│
├─────────────────────────────────────┤
│  Formal methods (model checking)    │
├─────────────────────────────────────┤
│  Logic (propositional, predicate)   │
├─────────────────────────────────────┤
│  Set theory (foundations)           │
└─────────────────────────────────────┘
```

## Logic in Programming Languages

- **Type systems**: The Curry-Howard correspondence maps types to propositions and programs to proofs. A function of type `A → B` is a proof of "A implies B."
- **Haskell/ML**: Parametric polymorphism corresponds to universal quantification (∀). A function `∀a. a → a` is the identity function.
- **Rust**: Ownership types encode linear logic, ensuring memory safety without garbage collection.

## Logic in Hardware Design

- **Boolean algebra** (Boole, 1854) directly models digital circuits. AND, OR, NOT gates implement logical connectives.
- **Hardware description languages** (Verilog, VHDL) compile to logic gate networks.
- **Formal equivalence checking** uses SAT solvers to verify that two circuit designs implement the same Boolean function.

## Logic in Databases

- **SQL** is based on relational algebra, which is a form of first-order logic. A query like `SELECT * FROM Employees WHERE Salary > 50000` corresponds to ∃x (Employee(x) ∧ Salary(x) > 50000).
- **Datalog** is a logic programming language used for deductive databases. Rules like `ancestor(X,Y) :- parent(X,Y).` are logical implications.

## Logic in Artificial Intelligence

- **Knowledge representation**: First-order logic represents facts and rules. Inference engines derive new facts.
- **Automated reasoning**: SAT solvers and theorem provers verify AI system properties.
- **Description logics** (used in OWL, the Web Ontology Language) are decidable fragments of first-order logic for representing ontologies.

## Logic in Verification

- **Model checking** verifies finite-state systems against temporal logic specifications (LTL, CTL).
- **Theorem proving** (Isabelle, Coq, Lean) verifies infinite-state systems and mathematical proofs.
- **SMT solvers** (Z3, CVC5) combine SAT solving with theory solvers for arithmetic, arrays, and bit-vectors.

## Interconnections

Logic connects to:
- **Set theory**: The semantics of first-order logic is defined in terms of sets.
- **Combinatorics**: Counting satisfying assignments (#SAT) is a combinatorial problem.
- **Graph theory**: Resolution proofs can be represented as directed acyclic graphs.
- **Number theory**: Gödel's incompleteness theorems use number theory (Gödel numbering) to encode logic within arithmetic.
