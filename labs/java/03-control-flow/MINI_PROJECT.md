# MINI PROJECT — Control Flow: Order State Machine

## Goal (2 weeks, ~8–10h)
Implement an e-commerce order lifecycle driven by exhaustive switches + guard clauses — zero deep nesting.

## Requirements
### Functional
1. States: `CREATED→PAID→SHIPPED→DELIVERED`, plus `CANCELLED/RETURNED`; events: pay/ship/deliver/cancel/return.
2. Transition via switch expression returning new state; illegal transitions → `IllegalStateException` with message.
3. Guard clauses: e.g., cancel only before SHIPPED; return only within 30 days (inject `Clock`).
4. CLI/demo: feed event log file, print state trace + rejected events report.
### Non-functional
- Nesting depth ≤ 2 (checkstyle/eyeball); switch exhaustive, no abusive `default: throw` hiding.
- 20+ tests: every transition legal + illegal; parameterized.
- Complexity per method ≤ 8.

## Phases
### Week 1 — Machine (4–5h)
- Enum states/events, transition function, guard helpers.
- Deliverable: state diagram (ASCII) + passing happy-path tests.
### Week 2 — Harness + Rules (4–5h)
- File driver, Clock injection, 30-day rule, rejected-report.
- Deliverable: sample logs (valid + adversarial) with expected outputs.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Exhaustiveness | Compiler-checked, no fall-through | Complete with default | Missing cases |
| Guards/readability | Flat, named predicates | Mostly flat | Nested soup |
| Time rule | Clock-injected, tested | Hardcoded but tested | Untested |
| Tests | All pairs incl. illegal | Happy + some illegal | Happy only |
| Driver/report | Clear trace + counts | Basic output | None |

Pass ≥ 70. Stretch: pattern-matching switch on sealed event records; Graphviz diagram.
