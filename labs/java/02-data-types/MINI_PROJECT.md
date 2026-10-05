# MINI PROJECT — Data Types: Precise Money Calculator

## Goal (2 weeks, ~8–10h)
Build a `Money` library + CLI that proves numeric discipline: no `double` for money, overflow-safe counts, strict parsing.

## Requirements
### Functional
1. `Money` (BigDecimal amount + Currency): `add/sub/mul/div` with `RoundingMode.HALF_EVEN`; `parse("USD 19.99")`.
2. CLI: `calc "USD 10.00 + USD 2.455"` with scale-2 output; `sum` over CSV column.
3. Overflow demo: `int` factorial vs `long` vs `BigInteger`; document boundary in README.
4. Validation: reject NaN/locale-comma, negative where illegal, with clear messages.
### Non-functional
- 15+ JUnit tests: rounding, scale, currency-mismatch, overflow, parse failures.
- No `float/double` in money path (grep-verifiable); `var` only where type obvious.
- README table: type → use-case (int/long/BigDecimal/BigInteger).

## Phases
### Week 1 — Money Core (4–5h)
- Money + Currency, arithmetic, rounding tests (HALF_EVEN vs HALF_UP demo).
- Deliverable: `mvn test` green on 10 tests.
### Week 2 — CLI + Hardening (4–5h)
- Parser, file sum, overflow report, fuzz with edge inputs (max long, 0.005).
- Deliverable: demo transcript + type-choice doc.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Correctness/rounding | Explicit mode, scale-2 always | Mostly right | double leakage |
| Overflow handling | Documented + tested | Checked happy path | Silent wrap |
| Parsing/validation | Helpful errors, no crash | Basic guard | NumberFormat crash |
| Tests | 15+, boundaries | 8+ | <5 |
| Doc (type table) | Justifies each choice | Present | Missing |

Pass ≥ 70. Stretch: multi-currency conversion with rate map; JShell demo script.
