# Performance: Logic and Proofs

## Truth Table Complexity

A truth table for a formula with n atomic propositions has 2^n rows. Evaluating each row takes O(n) time, giving O(n · 2^n) total time. This is exponential and becomes infeasible beyond ~20 variables. For example, a formula with 30 variables requires over a billion rows.

## SAT Solving

The Boolean satisfiability problem (SAT) asks whether a formula has a satisfying assignment. SAT is NP-complete (Cook-Levin theorem, 1971), so no polynomial-time algorithm is known. However, modern SAT solvers (CDCL-based, e.g., MiniSat, Glucose) use:
- **Unit propagation**: If a clause has one unassigned literal, assign it to satisfy the clause.
- **Conflict-driven clause learning (CDCL)**: Analyze conflicts to learn new clauses and prune the search space.
- **Restarts**: Periodically restart the search with learned clauses.

These heuristics solve industrial instances with millions of variables in seconds, though worst-case complexity remains exponential.

## Resolution Theorem Proving

Resolution-based theorem proving converts formulas to CNF and applies the resolution rule. The number of clauses can grow exponentially during CNF conversion (e.g., distributive law applications). Tseitin transformation avoids this by introducing auxiliary variables, keeping CNF size linear in the original formula size.

## Proof Checking vs. Proof Search

- **Proof checking**: Given a proof, verify each step. This is polynomial in the proof length.
- **Proof search**: Find a proof from scratch. This is undecidable in general for first-order logic (Church-Turing theorem, 1936) and NP-complete for propositional logic.

## Model Checking

Model checking verifies whether a finite-state system satisfies a temporal logic formula. The state space can be exponential in the number of variables (state explosion problem). Symbolic model checking uses binary decision diagrams (BDDs) to represent state sets compactly, but BDD size can still blow up for some systems.

## Practical Implications

When encoding problems as SAT:
- Use Tseitin transformation to avoid exponential CNF blowup.
- Prefer unit clauses and binary clauses—they enable efficient propagation.
- For counting problems, use #SAT solvers (e.g., sharpSAT), which are exponentially slower than SAT solvers in the worst case.
