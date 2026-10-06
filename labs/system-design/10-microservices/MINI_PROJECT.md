# Microservices - MINI PROJECT

## Project: Decomposed Order System That Survives Dependency Failure

**Time**: 14-18 hours

**Goal**: Build a small service set with real isolation properties, then kill
dependencies and prove the failures stay bounded.

### Services

```
gateway -> order-service -> inventory-service   (sync)
                   |            |
                   |            +-> pricing-service  (sync, optional)
                   +-> payment-service               (sync, required)
                   +-> (event) notification-service (async)
```

Each service owns its own database. No shared tables — this is the rule you are
demonstrating.

### Step 1: Data Ownership Enforcement (2 h)

Define the schemas:
- `order-service`: orders, order_items
- `inventory-service`: inventory, reservations
- `payment-service`: payments, refunds
- `notification-service`: (read-only) customer_email copy

Required tests:
- `order-service` must not read `inventory`. Instead: it calls the inventory API
  and gets an answer, OR receives stock state via an event projection. Prove
  there is no direct cross-database read.
- `order-service` needs the customer's email for the notification event. It
  copies it into a **projection table in notification-service** via an event.
  Test: change the email in the customer source, run the projection, and assert
  the copy updates within the staleness bound.
- Write a test that asserts the *staleness bound is documented* and measured.

This step is the whole lab's thesis. Do it properly.

### Step 2: The Saga (3 h)

Implement `SagaOrchestrator` with a durable log for place-order:

```
step 1: reserve inventory      compensate: release reservation
step 2: charge payment         compensate: refund
step 3: create shipment        compensate: void label
step 4: send email             IRREVERSIBLE -> approval gate
```

Required tests (each must reach a consistent or loudly-escalated state):

| Injection | Expected |
|-----------|----------|
| Reserve fails | No partial state |
| Payment fails after reserve | Inventory released; saga compensated |
| Shipment fails after payment | Refunded + released |
| Email "succeeds", shipment fails | `NEEDS_HUMAN`, alert fired |
| Compensation of payment fails twice | Escalated with both failures listed |
| **Process crash mid-compensation** | Recovery reads the durable log and finishes |

The last row is the one that matters. Without a durable log, recovery cannot
even decide what to undo.

### Step 3: Idempotency and the Outbox (2 h)

- Each step has an idempotency key derived from **stable business identity**
  (`orderId:stepName`), not a per-attempt UUID.
- Transactional outbox per service.
- Required tests:
  - Kill between the business write and the event publish -> neither exists.
  - Crash after publish, before `markPublished` -> duplicate event, deduped by
    the consumer.
  - Two pollers concurrently -> `SKIP LOCKED` prevents double-claim.
  - **The key test:** fire the same place-order request 50 times concurrently
    and assert exactly one order, one inventory reservation, one payment.

### Step 4: Isolation — Bulkheads, Breakers, Deadlines (3 h)

Size each bulkhead with Little's Law from your own load test, not a guess.

| Dependency | rps | p50 | permits (calc) |
|------------|-----|-----|----------------|
| inventory | 200 | 80 ms | ~16 -> use 24 |
| payment | 100 | 120 ms | ~12 -> use 18 |
| pricing (optional) | 300 | 5 ms | ~2 -> use 8 |

Required tests:

1. **Payment slow (3 s, no errors).** Verify the breaker does NOT open, the
   payment bulkhead fills, and only payment-path requests fail — while
   inventory-only requests still succeed. Assert healthy-path success rate > 80%.
2. **Payment down (instant errors).** Verify the breaker opens, requests fail
   fast, and inventory reservations are released (saga compensation runs).
3. **Pricing down.** Verify the request succeeds with a cached price. No failure
   at all — this is the graceful-degradation test.
4. **Deadline propagation.** Client timeout 1,000 ms across 4 hops. Sum every
   simulated service's sleep and assert the total never exceeds 1,000 ms.
5. **Bulkhead rejection is metered.** Assert a `bulkhead_rejected_total`
   metric increments and that it is not silently swallowed.

### Step 5: Service Discovery with Fallback (1 h)

Implement `ServiceDiscovery` with cache -> registry -> static fallback.
Required test: registry throws for every call; assert resolution still succeeds
via static fallback and that a metric records `discovery_fallback_used`.

### Step 6: Observability (2 h)

- Propagate a trace ID on every call; build a trace view showing the span
  timeline for one order.
- Per-service RED metrics, plus **per-dependency** latency and error rate.
- Metrics: saga state distribution, `NEEDS_HUMAN` count, bulkhead in-flight and
  rejected, breaker state per dependency, outbox drain lag, projection lag.

**Required:** create a scenario where the *aggregate* p99 looks acceptable but
one dependency is broken. Verify the per-dependency panel catches it. Then
verify an aggregate-only dashboard does not. That contrast is the deliverable.

### Step 7: Chaos (1 h)

Run 15 minutes of chaos: random 0-3 s delays, 5% errors, and forced breaker
trips on each dependency in turn. Record for each scenario:

- Which requests failed (by class: required vs optional dependency).
- Whether any **partial state** was left behind.
- Whether any saga ended in `NEEDS_HUMAN`.
- Time to full recovery.

**Checkpoint:** the required property is that no optional dependency can cause a
checkout failure, and no dependency can leave partial state. If either fails,
fix the design rather than the test.

### Deliverables

1. Four services with exclusive data ownership, proven by tests.
2. Saga with durable log, durable recovery from a mid-compensation crash, and
   the approval gate before the irreversible step.
3. Outbox with the four required tests, plus the 50-way concurrent idempotency
   test.
4. Bulkheads sized from measured load, with the slow-but-not-failing and
   optional-dependency tests.
5. Deadline propagation verified across four hops.
6. Discovery fallback with the registry-down test.
7. Per-dependency observability with the aggregate-vs-breakdown contrast.
8. Chaos report with per-scenario failure classes, partial state, and recovery
   times.

### Stretch

- Add consumer-driven contract tests between gateway and order-service, and
  break the interface deliberately to prove the test catches it.
- Extract `order-service` from a small monolith you write first, using the full
  Strangler Fig sequence with a continuous verification diff.