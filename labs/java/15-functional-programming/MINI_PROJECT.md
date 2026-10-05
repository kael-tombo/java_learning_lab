# MINI PROJECT — Functional Programming: Pure Pricing Engine

## Goal (2 weeks, ~8–10h)
Rebuild a tangled discount/tax calculator as a pure functional core with immutable models, composable rules, and property tests proving equivalence.

## Requirements
### Functional
1. Immutable `Cart(LineItem...)`, `PriceRule = Function<Cart,Cart>`; rules: bulk-10%, coupon-fixed, member-5%, tax-by-region — composed via `andThen`.
2. Error-as-value: `Result<T>` sealed (`Ok/Fail`) for invalid coupon, negative qty; no nulls, no thrown domain exceptions.
3. `Optional` for nullable promo code; `Stream` fold for totals; `foldLeft`-style reducer (no mutable accumulator).
4. Memoized `taxRate(region)` with `ConcurrentHashMap` cache; pure lookup extracted from I/O loader.
5. CLI: apply rule chains from args; print itemized breakdown (subtotal, discounts, tax, total).
### Non-functional
- Pure core has zero I/O, zero mutation, zero static mutable state; impure shell does file/console only.
- 16+ tests incl. 3 property tests (jqwik or hand-rolled 200-seed random): composition order laws, idempotence where claimed, golden equivalence vs legacy impl.
- README: functional-core/imperative-shell diagram + purity table (which fn is pure/why).
- Mutation coverage: all branches of coupon/tax rules covered.

## Phases
### Week 1 — Pure Core (4–5h)
- Immutable models, 4 rules, Result/Optional plumbing.
- Deliverable: CLI totals on 5 fixtures + 8 tests.
### Week 2 — Laws + Shell (4–5h)
- Property tests, memoization, impure shell split, golden diff.
- Deliverable: 200-seed property run green + equivalence report.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Purity/immutability | Provably pure core | Mostly pure | Hidden mutation |
| Composition | Generic combinators reused | andThen used | Copy-paste rules |
| Error-as-value | Total fns, Result everywhere | Optional used | Nulls/throws |
| Property tests | 3+ laws, seeds logged | 1 basic | Example-only |
| Shell split | Clean boundary | Present | I/O in core |

Pass ≥ 70. Stretch: lazy `Supplier` price feed; parallel-safe proof (run rules on parallel stream, identical totals).
