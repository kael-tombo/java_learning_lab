# MINI PROJECT — Best Practices: Harden a Sloppy Orders Module

## Goal (2 weeks, ~8–10h)
Take a provided "sloppy" `orders` module (god class, leaking
resources, mutable DTOs, raw types, swallowed exceptions) and harden
it to an Effective-Java baseline with automated gates proving it.

## Requirements
### Functional
1. Replace 3+ telescoping constructors with builders (or static
   factories with intention-revealing names); validate in compact
   form / `Objects.requireNonNull` with messages.
2. Make `Order`, `LineItem`, `Money` immutable: final class/fields,
   defensive copies of lists/dates, unmodifiable views.
3. Fix resource handling: every `Connection/Stream/Reader` path uses
   try-with-resources; remove finalizer; add Cleaner only if justified.
4. Exception overhaul: checked `OrderRepositoryException` for
   recoverable I/O, unchecked for programming errors; never swallow —
   chain causes; add `Optional<Discount>` return (no Optional params).
5. Generics cleanup: zero raw types, correct `PECS` on one bulk API
   (`copy(List<? extends Line> src, List<? super Line> dst)` demo).
6. equals/hashCode/toString on all value types; one enum with behavior
   (`OrderStatus.canTransitionTo`) replacing int flags.

### Non-functional
- 20+ tests: immutability (mutate-after-construct fails), builder
  validation, exception chaining, equals contract (EqualsVerifier ok),
  resource-close via mock/fake.
- Gates green: ArchUnit (no public fields in domain, no
  `Thread.sleep` in prod code), Error Prone or SpotBugs zero HIGH,
  Checkstyle/Formatter clean.
- README: violation-to-fix table (rule → before → after → Item #).
- JaCoCo line coverage ≥ 80% on `domain/` package.

## Starter Layout
```
src/main/java/com/lab40/orders/{Order,LineItem,Money,OrderStatus,
  OrderService,OrderRepository}.java  (sloppy starter provided)
src/test/java/.../{ImmutabilityTest,BuilderTest,ExceptionsTest}.java
archunit/ApiRulesTest.java
```

## Phases
### Week 1 — Correctness Core (4–5h)
- Immutables + builders + equals/hashCode + exception taxonomy.
- Deliverable: sloppy test suite + new contract tests green.
### Week 2 — Gates + Proof (4–5h)
- ArchUnit + Error Prone + coverage; cleanup sprint on one more class.
- Deliverable: hardening report with warning counts before/after.

## Test Plan
- Mutation check: remove defensive copy → test fails.
- Null-pass tests for every public factory/ctor.
- Concurrency smoke: share immutable Order across 8 threads, no drift.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Immutability | Copies + unmod views proven | Final fields | Mutable leaks |
| Builders/factories | Validated, named | Used | Telescoping kept |
| Exceptions/resources | Taxonomy + TWR everywhere | Partial | Swallowed/close leaks |
| Generics/equals | PECS + contract tested | Compiles clean | Raw types remain |
| Gates + tests | 20+ tests, gates green, ≥80% | 12+ tests | No gates/proof |

Pass ≥ 70. Stretch: Refactor one inheritance hierarchy to
composition + sealed interface; add NullAway annotations.

## Demo Checklist
- [ ] `mvn verify` green (tests + ArchUnit + SpotBugs)
- [ ] Before/after diff of god-class split (LOC per method ≤ 20)
- [ ] Coverage report + violation table in README
- [ ] 5-min review: "which rule prevented which bug class"

## Common Traps
Optional as parameter, builder without validation, equals without
hashCode, checked exception for programming errors — all auto-fail.
