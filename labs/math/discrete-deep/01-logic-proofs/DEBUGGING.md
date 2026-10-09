# Debugging: Logic and Proofs

## Verifying Truth Tables

When a truth table produces an unexpected result, check:
- **Row count**: For n variables, there must be exactly 2^n rows. Missing rows mean incomplete case analysis.
- **Column order**: Evaluate subexpressions left-to-right, respecting parentheses. A common error is evaluating P → Q before computing ¬P.
- **Implication truth values**: P → Q is false *only* when P is true and Q is false. Students often mark it false when P is false.

## Checking Proofs Step by Step

For each line in a proof, verify:
1. **Justification**: Does the stated rule actually apply? "Modus ponens" requires both P → Q and P to be established.
2. **Variable capture**: In quantifier rules, ensure no free variable becomes accidentally bound. Renaming bound variables (alpha-conversion) prevents this.
3. **Scope of assumptions**: In natural deduction, track which assumptions are active. Discharging an assumption too early or too late invalidates the proof.

## Finding Counterexamples

To disprove a statement:
1. **Identify the structure**: Is it a universal claim (∀), an implication (→), or an equivalence (↔)?
2. **Construct minimal counterexamples**: For "all graphs with property P have property Q," try the smallest graph with P. Often a graph with 3–4 vertices suffices.
3. **Check boundary cases**: Empty sets, single-element sets, and degenerate cases (n = 0, n = 1) are frequent sources of counterexamples.

## Testing Quantifier Scope

When a formula has nested quantifiers, test with small finite domains:
- For ∀x ∃y R(x,y), check that for each x you can find a y (y may depend on x).
- For ∃y ∀x R(x,y), check that a single y works for all x.
- A 2-element domain {a, b} is often enough to distinguish these.

## Debugging Induction Proofs

Common induction failures:
- **Weak base case**: Proving P(0) but the inductive step requires P(0) and P(1) to prove P(2).
- **Circular inductive step**: Assuming P(k+1) to prove P(k+1). The inductive hypothesis must be P(k) only.
- **Off-by-one in the step**: Proving P(k) → P(k+2) when you need P(k) → P(k+1). This leaves gaps in the proof.

## Using Truth Trees (Semantic Tableaux)

When a truth table is too large (many variables), use a truth tree:
1. Start with the negation of the statement you want to prove.
2. Apply decomposition rules to break down connectives.
3. If all branches close (contain a contradiction), the original statement is valid.
4. If a branch remains open, it provides a counterexample.
