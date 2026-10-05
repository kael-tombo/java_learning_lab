# MINI PROJECT — Lambdas: Event Router

## Goal (2 weeks, ~8–10h)
Replace an anonymous-class-heavy notification dispatcher with lambdas + method refs, adding composition, exception adapters, and a benchmark proving parity.

## Requirements
### Functional
1. `Event(type, payload, timestamp)` router: `Map<String, List<Consumer<Event>>>` with `on(type, handler)` registration via lambdas.
2. Handler library with all four shapes: `Predicate<Event>` filter, `Function<Event,String>` formatter, `Consumer<Event>` sender, `Supplier<Event>` heartbeat generator.
3. Composition: `filter.and(other)`, `formatter.andThen(...)`, chained `Comparator<Event>` for priority queue (`comparing(...).thenComparing(...)`).
4. `ThrowingConsumer<T>` adapter: wrap checked `IOException` senders into unchecked; router never leaks checked exceptions.
5. Method refs: at least one static (`Filters::isUrgent`), bound (`this::audit`), unbound (`String::toUpperCase`), constructor (`Alert::new` via `Function<String,Alert>`).
### Non-functional
- Zero anonymous inner classes; effectively-final capture only; no mutable captured state.
- 16+ tests: dispatch order, filter composition truth table, exception-wrap path, comparator chain, heartbeat supplier.
- `README`: before/after line counts + `javap -c` note showing `invokedynamic` vs old `$1` classes.
- JMH or hand-rolled nano benchmark: lambda vs method-ref vs anonymous (5 runs avg).

## Phases
### Week 1 — Router + Shapes (4–5h)
- Event model, router, 6 handlers, composition utilities.
- Deliverable: working router demo on 3 event types + 8 tests.
### Week 2 — Hardening + Proof (4–5h)
- Throwing-adapter, full ref coverage, benchmark, exception tests.
- Deliverable: benchmark table + refactor memo.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| SAM/lambda use | Idiomatic shapes + composition | Correct basics | Anonymous leftovers |
| Method refs | All 4 kinds, justified | 2 kinds | None |
| Exception adapter | Clean generic, tested | Works untested | try/catch soup in lambda |
| Capture discipline | Effectively-final, no mutation | Mostly | Compile hacks / arrays-as-box |
| Tests + bench | 16+ tests, 5-run avg | 10+ tests, timed once | Happy-path only |

Pass ≥ 70. Stretch: serializable-lambda audit (`SerializedLambda` risk note); generic `sneakyThrow` utility with warning doc.
