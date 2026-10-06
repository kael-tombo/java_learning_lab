# Distributed Transactions - MINI PROJECT

## Project: Order Saga with a Transactional Outbox and Real Failure Injection

**Time**: 10-14 hours

**Goal**: Build a cross-service checkout that *survives* being cut in half at
the worst moment — and prove it, with tests that deliberately break things.

### Services in Scope

```
Checkout (orchestrator)
  ├── InventoryService   reserve stock        (compensatable: release)
  ├── PaymentService     charge card          (compensatable: refund)
  └── ShippingService    create label         (compensatable: void label)
      NotificationService email confirmation   (NON-compensatable)
```

### Step 1: Outbox First (2 h)

Implement `OutboxRepository` from `CODE_DEEP_DIVE.md`:

```sql
CREATE TABLE orders (
  id TEXT PRIMARY KEY, total_cents BIGINT NOT NULL, status TEXT NOT NULL);
CREATE TABLE outbox (
  id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  type TEXT NOT NULL,
  payload TEXT NOT NULL,
  dedup_key TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL,
  published_at TIMESTAMPTZ NULL);
```

Write the claim loop with `FOR UPDATE SKIP LOCKED` and **two concurrent
pollers**. Required tests:

- Kill the poller *after* publishing but *before* `markPublished`. Assert the
  event is delivered twice, and that the consumer dedups it. (Duplicates are
  the expected behaviour; losing the event is the bug.)
- Assert that two pollers never claim the same row.
- Assert that a business write with no event and an event with no business
  write are both impossible.

### Step 2: Idempotent Consumer (2 h)

Implement `IdempotencyStore`. Then write the test that catches the classic
bug:

```java
@Test void retryUsesTheSameKeyNotAFreshOne() {
    String key1 = StableDedupKeys.forOrderPlaced("order-42");
    String key2 = StableDedupKeys.forOrderPlaced("order-42");
    assertEquals(key1, key2);              // business identity, not per-attempt UUID
    // Now assert a THIRD attempt still dedups after the TTL window is exceeded:
    // with ttl < brokerRetention this SHOULD fail, and you must notice that.
}
```

Required: assert the dedup TTL is greater than your broker's retention window.
Make that a test so it cannot silently regress.

### Step 3: Saga with Compensation (3 h)

Implement `SagaOrchestrator` with the four steps. Required tests, each of which
must reach a **consistent end state** or escalate loudly:

| Inject | Expected |
|--------|----------|
| Inventory reserve fails | No partial state; nothing to compensate |
| Payment fails after inventory | Inventory released; saga COMPENSATED |
| Shipping fails after payment | Payment refunded, inventory released |
| Notification "succeeds" then shipping fails | Irreversible step done → **FAILED_NEEDS_HUMAN**, alert fired |
| Compensation of payment fails twice | Escalate with both failures listed |
| Process crash mid-compensation | Durable saga log lets recovery finish the compensation |

The last row is the one that matters. Add a `saga_log` table written in the
same transaction as each step's state change, and prove recovery works from
the log alone.

### Step 4: Measure the Cost (1 h)

Instrument the saga and report:

- p50 / p99 saga duration.
- Compensation rate (how often, and which step fails most).
- Irreversible-execution rate — the fraction of sagas that reach the email step.
- Held-lock-seconds per resource, using the arithmetic from
  `MATH_FOUNDATION.md`.

**Checkpoint:** if irreversible-execution rate is high, say so explicitly.
That number is the real argument about whether the saga design is sound.

### Step 5: Retry and Timeout Policy (2 h)

Implement per-step: exponential backoff with jitter, a hard cap on attempts, a
total deadline, and a `Retry-After`-style backpressure signal when the pool is
saturated. Write the test that a step failing with a *transient* error
eventually succeeds and that a *permanent* error fails fast without burning
retries.

### Deliverables

1. Outbox schema, claim loop, and the two-publisher race test.
2. Durable idempotency store with a test proving TTL > broker retention.
3. Saga orchestrator with durable log and crash recovery.
4. Six failure-injection tests, all reaching consistent or loudly-escalated
   states.
5. Metrics dashboard data plus the four numbers from Step 4.
6. A written answer: which step would you remove from this saga to make the
   irreversible class empty, and what would you lose?

### Stretch

- Add a human-approval gate before the irreversible notification step, and
  demonstrate that it converts `FAILED_NEEDS_HUMAN` into a completable saga.
- Add a reconciliation job that scans for sagas stuck in any non-terminal state
  for more than N minutes and pages on them.