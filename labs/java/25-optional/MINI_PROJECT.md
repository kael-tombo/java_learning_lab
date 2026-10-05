# MINI PROJECT — Optional: Null-Free Lookup Service

## Goal (2 weeks, ~8–10h)
Convert a null-riddled user/order/coupon lookup into an Optional-chained service with correct layer bridging and a lazy-default benchmark.

## Requirements
### Functional
1. Repos return `Optional<User/Order/Coupon>`; service `priceFor(userId)` chains `findUser.flatMap(findOrder).flatMap(findCoupon)` with `filter(active)` at each step.
2. Terminals: missing user → `orElseThrow(UserNotFound)`, missing coupon → default (lazy `orElseGet(Coupon::standard)`), demo `ifPresentOrElse` audit branch.
3. No `get()`, no `isPresent/get` pairs, no Optional fields/params/collections; `map` vs `flatMap` used correctly (reviewer can point at each).
4. Controller bridge: `toResponse(Optional)` → 200/404 without nulls; stream bridge: `stream().flatMap(Optional::stream)` filtering.
5. Seed data with absent cases (no user, no order, expired coupon, null legacy row via `ofNullable`).
### Non-functional
- ArchUnit-style self-check test: reflect over main code, fail on `Optional` fields/params or `.get()` calls (string-scan acceptable, documented).
- 16+ tests: each absence point, guard filter, lazy-vs-eager (counter proves orElse evaluated always), 404 mapping.
- README: null-ladder vs chain diff + orElse/orElseGet timing table.
- Benchmark: expensive-default path 100k calls, orElse vs orElseGet delta.

## Phases
### Week 1 — Chain (4–5h)
- Repos + flatMap chain + terminals + seeds.
- Deliverable: CLI lookups incl. absent cases + 8 tests.
### Week 2 — Bridge + Proof (4–5h)
- Controller/stream bridges, ban-test, benchmark.
- Deliverable: 404 demo + benchmark table.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Chaining | flatMap/filter idioms | Works | isPresent/get |
| Terminals | Intent-revealing each end | Present | Bare get |
| Boundaries | 404/stream bridges clean | Present | Nulls leak |
| Ban-test | Automated, green | Manual note | Missing |
| Tests+bench | 16+ tests, measured delta | 10+ tests | Happy-path only |

Pass ≥ 70. Stretch: `Optional` → `Result` (Either-lite) for error reasons; primitives (`OptionalInt`) hotspot comparison.
