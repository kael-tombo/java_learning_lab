# Payment System - MINI PROJECT

## Project: A Ledger That Balances Under Adversarial Failure Injection

**Time**: 14-18 hours

**Goal**: Build a payment service whose books balance *always*, verified
continuously, and prove it by killing the service at the worst possible
moments.

### Scope

```
Ledger            immutable entries, derived balance, invariant verifier
SplitCalculator   exact remainder handling, fee identity
PaymentStateMachine  explicit states, no illegal transitions
IdempotencyLayer  fingerprint + dedup across four layers
ReconciliationClassifier  conservative classification
Outbox            business write + event atomically
```

### Step 1: Ledger and the Invariant (2 h)

Implement `Ledger` with integer minor units and per-currency exponents.
Required tests:

- 100k random appends across 1,000 accounts. After **every** append, run
  `verifyInvariant()`. Assert it never throws.
- Wipe the projection entirely and rebuild from entries alone. Assert the
  rebuilt balances are byte-identical to the pre-wipe values. This is the
  property that makes audit possible.
- `balanceAt(pastInstant)` reconstructs a historical balance. Assert against
  hand-computed expected values for 100 known points in time.
- JPY (exp 0) and BHD (exp 3) round-trip correctly. Assert a system assuming
  two decimals everywhere fails these.

### Step 2: Money Arithmetic (2 h)

Implement `SplitCalculator`. Required tests:

- `split(10000, 3 participants)` returns `[3334, 3333, 3333]`. Assert the sum
  is exactly 10000.
- Property test: 1M random `(total, n)` pairs. Assert
  `sum(split(total, n)) == total` **every time**. The cent that disappears in
  production lives in the tail, not in the example.
- Fee identity: 1M random `(gross, rate)` pairs. Assert `net + fee == gross`.
- Negative and zero totals rejected explicitly, not silently coerced.

### Step 3: The State Machine (2 h)

Implement `PaymentStateMachine`. Required tests:

- Every legal transition succeeds; **every illegal transition is refused**.
  Generate the full cross product of (state, target) and assert the outcome
  matches `ALLOWED` exactly. This catches an accidentally widened map.
- `CAPTURED -> CAPTURE_PENDING` is refused. **This is the duplicate-capture
  prevention mechanism** — assert it directly and comment it.
- Concurrent `claim()` calls for the same payment: assert exactly one succeeds.
- `needsHuman()` fires for a payment pending beyond 24 h and not before.

### Step 4: Layered Idempotency (2 h)

Implement `IdempotencyLayer` plus the four enforcement points. Required tests:

- **50 concurrent requests, same key, same body**: assert exactly one executes
  and all 50 receive the *identical* result body. Not merely the same status.
- **Same key, different amount**: assert `CONFLICT` and that nothing executes.
  Write a comment naming the incident this prevents.
- **Retry after a simulated restart**: with an in-memory store, assert this
  **fails** (duplicate). Then swap in a persistent store and assert it passes.
  This test is the argument for a durable dedup layer.
- Assert the dedup TTL exceeds the reconciliation window.

### Step 5: Outbox and Event Emission (1 h)

Business row + outbox row in one transaction. Required tests:
- Kill between the two writes: assert neither exists (atomicity).
- Crash after publish, before `markPublished`: assert the event is delivered
  twice and the consumer dedups it.
- Assert `sum(balance) == sum(entries)` still holds after replaying events.

### Step 6: Reconciliation Classifier (2 h)

Implement `ReconciliationClassifier`. Required tests, including the ones that
must be *conservative*:

| Our view | Processor view | Pending | Expected |
|----------|---------------|---------|----------|
| PENDING | ABSENT | 30 s | IN_FLIGHT |
| PENDING | CONFIRMED | 30 s | WE_MISSED |
| PENDING | CONFIRMED | 2 days | STUCK |
| CONFIRMED | CONFIRMED, same amount | — | IN_FLIGHT |
| CONFIRMED | CONFIRMED, different amount | — | MISMATCHED |
| CONFIRMED | UNKNOWN (processor down) | — | STUCK |

Assert the last row. During a processor outage, "we don't know" must never
become "they missed it".

### Step 7: Adversarial Failure Injection (3 h)

The core of the lab. Inject a processor that fails at a specific point, then
assert the end state.

| Kill point | Expected end state |
|------------|-------------------|
| Before the capture request leaves | PENDING -> reconciliation finds nothing at processor -> WE_MISSED -> re-drive |
| Processor succeeds, response lost | PENDING -> reconciliation finds CONFIRMED -> WE_MISSED -> record, do NOT re-capture |
| Processor succeeds, we record, response lost to client | CAPTURED -> client retries -> dedup returns original result |
| After claim, before processor call | PENDING forever -> 24 h STUCK -> human |
| During a split payment, after 2 of 3 legs | Partial state visible -> reconciliation -> compensating refunds |
| Ledger append fails after processor capture | Processor has money, we do not -> WE_MISSED -> correction event |

**Checkpoint:** run every row 10x and assert the *distribution* of end states is
identical each time. Non-determinism here is the bug.

### Step 8: Continuous Verification and Metrics (1 h)

- Run `verifyInvariant()` on every append (production: as a metric/alert).
- Metrics: capture success/failure rate, pending-age distribution (p50/p95/p99),
  reconciliation queue depth by classification, correction events emitted,
  `STUCK` count, duplicate-reject count, dedup replay count.
- Alert on: invariant violation (page), `STUCK` > 0 (page), pending-age p99 >
  5 min (page), reconciliation queue growing for 3 cycles (page).

**Deliverable:** a metrics dashboard where every alert maps to a runbook step.

### Deliverables

1. Ledger with continuous invariant verification on every append.
2. Historical balance reconstruction verified against 100 known points.
3. Multi-currency correctness including JPY and BHD.
4. Split calculator with a 1M-case conservation property test.
5. State machine with an exhaustive transition cross-product test.
6. Layered idempotency including the different-amount conflict test and the
   restart test.
7. Transactional outbox with atomicity and duplicate-delivery tests.
8. Reconciliation classifier with all six rows including the processor-outage
   conservatism test.
9. Six failure-injection scenarios, each run 10x with identical end-state
   distributions.
10. Metrics, alerts, and runbook references.

### Stretch

- Build a deterministic replay tool: given the entry log, reconstruct every
  balance and prove it matches — the artefact a regulator would ask for.
- Add a two-phase "shadow ledger" that processes events in a separate pipeline
  and asserts agreement with the primary, so a single bad append is caught
  independently of the code that made it.