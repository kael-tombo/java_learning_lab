# MINI PROJECT — Testing: Harden the Billing Service

## Goal (2 weeks, ~8–10h)
Take an under-tested `billing-service` (invoices, proration, Stripe-like port)
to a green, mutation-strong suite with Testcontainers Postgres and contract
tests on the payment port.

## Requirements
### Functional
1. Unit ring: proration math, tax/vat rules, invoice state machine —
   `@ParameterizedTest` edges (leap dates, timezones, zero-qty, refunds).
2. Doubles: stub `PaymentGateway` (success/decline/timeout), fake
   `Clock` (no `now()` in logic), captor-verify single-charge rule.
3. Slice: `@DataJpaTest` invoice persistence + Flyway migration round-trip;
   `@WebMvcTest` error contract (400/404/422 shapes) via AssertJ JSON.
4. Integration: Testcontainers Postgres full-repo test; WireMock gateway
   (timeouts/500s/retries) with `Awaitility` for async webhook path.
5. Quality gates: JaCoCo + PIT (mutation >= 85% on `billing/`), ArchUnit
   (no `Instant.now` in domain, ports only via interfaces).

### Non-functional
- Fast ring (`unit+slice`) < 90s; `@Tag("slow")` containers separate.
- Zero flaky: fixed seeds, no wall-clock sleeps, container reuse.
- README: pyramid diagram + what-mocks-what table + flake policy.

## Phases
### Week 1 — Unit + Slices (4–5h)
- Steps: parametrize proration, fake clock, stub gateway, slice tests.
- Deliverable: fast ring green, mutation baseline.

### Week 2 — Integration + Gates (4–5h)
- Steps: Testcontainers + WireMock paths, PIT gate, flake hunt (50 runs).
- Deliverable: CI-split config + mutation report + demo.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Unit depth | Parametrized edges, one-behavior tests | Decent cover | Happy only |
| Double design | Ports mocked, logic real | Mixed | Mocks internals |
| Slice/integration | Real DB + wire faults | Basic IT | H2-only |
| Mutation | >= 85%, survived-killers fixed | Run once | Skipped |
| Speed/flake | Fast ring + 50x stable | Stable | Flaky/slow |

Pass >= 70. Stretch: contract tests (Spring Cloud Contract); chaos on
webhook consumer; parallel-execution tuning with JFR thread dump check.
