# MINI_PROJECT — Derivatives & Rules: Symbolic Differentiator (Light)
> Implement + derive + verify. ~2 hours.

## Goal
Build a CLI that differentiates polynomials and simple compositions via an AST,
prints step-by-step rule applications, and verifies numerically at several points.

## Build Steps
1. `Ast.java`: nodes for + − * / pow, sin, cos, exp, log.
2. `Diff.java`: recursive rules: sum/product/quotient/chain.
3. `Simplify.java`: light cleanup (0*x→0, 1*x→x, x⁰→1).
4. Driver: differentiate 8 expressions, evaluate original/derivative numerically, assert match.

## Acceptance
- [ ] Every rule step logged.
- [ ] Numeric check within 1e-5 at 3 random points.
- [ ] Chain-of-chains handled (sin(exp(x²))).

## Extensions
- Implicit differentiation for circles.
