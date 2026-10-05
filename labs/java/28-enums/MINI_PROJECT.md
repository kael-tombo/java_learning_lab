# MINI PROJECT — Enums: Order Lifecycle State Machine

## Goal (2 weeks, ~8–10h)
Build an `order-lifecycle` library where `OrderStatus` owns its transition
graph, pricing strategy, and wire mapping — illegal transitions uncompilable
or rejected, unknown codes never crash.

## Requirements
### Functional
1. `OrderStatus { CREATED, PAID, SHIPPED, DELIVERED, CANCELLED, REFUNDED }`
   each with `code`, `terminal` flag, and allowed-next `EnumSet`.
2. `transition(OrderStatus next)` enforcing the table; `IllegalTransition`
   carries from/to + allowed list; exhaustive `switch` for side effects.
3. Strategy: abstract `fee(Order)` / `sla()` overridden per constant
   (express vs standard shipping cost, refund windows).
4. `fromCode(String)` -> `Optional<OrderStatus>` backed by static
   `EnumMap`/hash map built once; `UNKNOWN` fallback for forward-compat.
5. Persistence + JSON: JPA `AttributeConverter` on `code`, Jackson
   `@JsonValue code` / `@JsonCreator fromCode`; never serialize `ordinal()`.
6. CLI demo: drive 10k random transitions, print rejection rate + report.

### Non-functional
- Zero `ordinal()` usage (`grep` gate); `switch` expressions exhaustive.
- 20+ tests: every transition allowed/rejected, every strategy branch,
  unknown-code handling, JSON round-trip, converter mapping.
- JMH or timing: `EnumMap` vs `HashMap` lookup note in README.
- README: transition diagram (ASCII) + code-vs-ordinal policy.

## Phases
### Week 1 — Model + Transitions (4–5h)
- Steps: enum skeleton, transition table, exception type, strategy methods.
- Deliverable: unit-tested state machine, diagram draft.

### Week 2 — IO + Hardening (4–5h)
- Steps: converter + Jackson wiring; fuzz unknown codes; CLI load demo.
- Deliverable: round-trip proof + compat memo.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Transition model | Table-driven, tested all pairs | Core paths | If-chains |
| Strategy design | Per-constant overrides | Switch in places | Logic outside enum |
| Wire mapping | Code-based + UNKNOWN/fallback | valueOf only | ordinal persisted |
| Exhaustiveness | Expression, no silent default | Switch covered | Missing branches |
| Tests + docs | 20+ + diagram + bench note | 12+ tests | Happy-path only |

Pass >= 70. Stretch: event-sourced `OrderEvent -> Status` reducer;
`EnumSet` feature-flag set; ArchUnit rule banning `ordinal()`.
