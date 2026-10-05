# MINI PROJECT — Pattern Matching: Event Router

## Goal (2 weeks, ~8–10h)
Replace an instanceof-cast ladder with switch/record patterns over sealed events, including guards, null handling, and a dominance-error lesson log.

## Requirements
### Functional
1. `sealed interface Ev permits OrderPlaced, Paid, Shipped, Cancelled` (records with nested `Customer`/`Money` records); untyped JSON-ish `Map` → `parse(Map)` using patterns.
2. `handle(Ev)` switch expression: type + record patterns, one guarded case (`case Paid(var id, var m) when m.cents() > 10_000 -> review`), explicit `case null`.
3. Kill 6+ instanceof-cast sites (before/after diff counted); nested destructure (`OrderPlaced(Customer(var n), var items)`) in at least 2 cases.
4. Dominance lesson: commit one over-broad-first ordering, capture compiler error, fix + document in README.
5. CLI: feed event JSON lines, print actions; malformed → typed `Rejected(reason)` (sealed) not exception.
### Non-functional
- No explicit casts in `handle/parse`; no default on sealed switch; guards don't fake exhaustiveness (total fallback case present).
- 16+ tests: each event, guard boundary (10_000/10_001), null, unknown-kind, nested-pattern totals.
- README: dominance error text + ordering rule; pattern-vs-visitor line-count table.
- Fuzz: 1k random maps, zero ClassCastException (only Rejected).

## Phases
### Week 1 — Types + Parse (4–5h)
- Sealed events, record patterns in parse, null/unknown paths.
- Deliverable: parse demo + 8 tests.
### Week 2 — Handle + Harden (4–5h)
- Guarded handle switch, dominance log, fuzz run.
- Deliverable: router + fuzz report.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Patterns | Nested + guard idioms | Basic switch | Casts remain |
| Exhaustiveness | No default, null explicit | Correct | Default hides |
| Parse safety | Rejected type, no throws | Works | CCE possible |
| Dominance log | Error + rule stated | Mentioned | Missing |
| Tests + fuzz | 16+ tests, 1k fuzz clean | 10+ tests | Happy-path only |

Pass ≥ 70. Stretch: pattern + virtual-thread fan-out of independent events with ordering proof.
