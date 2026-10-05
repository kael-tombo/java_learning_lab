# MINI PROJECT — Records: Immutable Order Book

## Goal (2 weeks, ~8–10h)
Model a trading/order domain entirely with records (validated, defensively copied), with JSON persistence and a record-pattern pricer.

## Requirements
### Functional
1. `record Money(long cents, String ccy)`, `LineItem`, `Order(id, customer, List<LineItem>, Instant placed)` — compact-ctor validation (non-null, qty>0, currency set, list copied via `List.copyOf`).
2. Derived accessors: `Order.totalCents()`, `Money.add(...)` returning new record; with-methods (`withStatus`) returning copies.
3. Jackson round-trip: serialize/deserialize 5 fixtures (canonical ctor); unknown-field and missing-field behavior documented + tested.
4. Record patterns in pricer: `switch (payment)` and `if (o instanceof Order(var id, var c, var items, var t))` destructuring — no getter chains.
5. CLI: load orders JSON, price all, write priced JSON; reject invalid with clear messages.
### Non-functional
- Zero mutable domain state; no setters; no public array/list aliasing (mutation test proves copy).
- 16+ tests: validation each rule, aliasing attempt fails, JSON round-trip, pattern branches, totals math.
- README: POJO-vs-record line-count table + shallow-immutability note.
- Compat: record round-trip pinned to Jackson version in pom/gradle.

## Phases
### Week 1 — Domain (4–5h)
- Records + validation + copies + totals.
- Deliverable: in-memory pricing demo + 8 tests.
### Week 2 — IO + Patterns (4–5h)
- Jackson IO, pattern pricer, CLI, aliasing proof.
- Deliverable: JSON-in/JSON-out + full suite.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Validation | All invariants, clear msgs | Basic | Missing |
| Immutability | CopyOf + alias test | Copied | Aliased |
| JSON | Round-trip suite pinned | Works | Untested version |
| Patterns | Destructured, no chains | Used | Getters only |
| Tests | 16+ | 10+ | Happy-path only |

Pass ≥ 70. Stretch: sealed record event log (`OrderPlaced/Cancelled`) + compact-serialization benchmark vs POJO.
