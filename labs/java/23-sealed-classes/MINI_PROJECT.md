# MINI PROJECT — Sealed Classes: Payment + Expression Engine

## Goal (2 weeks, ~8–10h)
Model payments and an expression AST as sealed hierarchies with exhaustive switches, record leaves, and a versioning test proving the compiler guards growth.

## Requirements
### Functional
1. `sealed interface Payment permits Card, BankTransfer, Voucher, Cash` (records); `authorize/capture` via exhaustive `switch` — no default.
2. `sealed interface Expr permits Lit, Add, Mul, Neg`; `eval(Expr)` + `pretty(Expr)` exhaustive; add `Div` mid-project to prove compile-break detection (document files that broke).
3. `non-sealed` demo: one intentional opening (e.g., `interfacePromo extends Voucher` path) with justification comment + test showing extension works there only.
4. JSON with type discriminator (`"kind":"card"`) round-trip; unknown-kind → explicit error, tested.
5. CLI: price a payment file, eval an expr file; invalid variant prints legal list.
### Non-functional
- `javac` proves exhaustiveness (no default on sealed switches); reflection check that permits list matches docs.
- 16+ tests: each variant, Div-break evidence, non-sealed extension, unknown-kind, null payment.
- README: hierarchy diagram + endgame table (final/sealed/non-sealed per leaf + why).
- Mutation: adding apermit without switch update must fail build (CI-check documented).

## Phases
### Week 1 — Payments (4–5h)
- Sealed payments + exhaustive ops + JSON discriminator.
- Deliverable: payment CLI + 8 tests.
### Week 2 — AST + Growth (4–5h)
- Expr engine, Div-break experiment, non-sealed case.
- Deliverable: breakage log + final suite.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Sealing | Tight permits, endgames justified | Correct | non-sealed everywhere |
| Exhaustiveness | No default, break proven | No default | Default swallows |
| Records | Immutable leaves, validated | Used | Mutable |
| JSON/version | Discriminator + unknown test | Works | Untyped |
| Tests | 16+ incl. growth proof | 10+ | Happy-path only |

Pass ≥ 70. Stretch: versioned discriminator (`kind/v`) migration test; ArchUnit "no default on sealed switch" rule sketch.
