# Distributed Transactions - REAL WORLD PROJECT

## Project: Payments Platform with an Auditable, Compensatable Ledger

**Time**: 3-4 weeks (team of 3-4)

**Scenario**: You process card payments for a marketplace. Requirements:
money movement must be auditable end to end, retries must never double-charge,
and every state transition must be reconstructable for a regulator.

This is deliberately *not* "use sagas for checkout". It is the harder problem:
a money ledger where the primary invariant is that the books balance.

### Step 1: Model the Invariant First

Write the invariant in one sentence before writing any code:

```
INVARIANT: For every account A at every version v,
           sum(entries where account=A and version<=v) == balance(A, v)
```

Then state what you are NOT promising: intra-saga atomicity is never promised.
An order can exist without a capture; that is a *visible, expected* state.

### Step 2: Event-Sourced Ledger, Not Row Updates

Every money movement is an immutable entry. Balances are a projection.

```
entry_id, account_id, seq (per-account monotonic), type, amount_minor,
 currency, reference, idempotency_key UNIQUE, created_at, effective_at
```

Requirements on the write path:

1. The idempotency key comes from the **caller** (the checkout service), not
   generated per attempt. `UNIQUE` on it makes double-application impossible
   at the storage layer, not just in application logic.
2. `seq` is allocated per account. Per-account ordering is required; global
   ordering is not, and buying it would be a mistake.
3. No `UPDATE balance SET balance = balance + ?`. A balance you cannot derive
   from entries is a balance you cannot audit.

Build the projection (current balance per account) as a separate, rebuildable
read model with a checkpoint. Prove rebuildability: wipe the projection,
replay, and assert the diff is zero.

### Step 3: Replace 2PC With an Explicit State Machine

The capture flow, and its honestly-visible intermediate states:

```
AUTHORIZED -> CAPTURE_PENDING -> CAPTURED -> SETTLED
                   |                 |
                   +-> CAPTURE_FAILED+-> REFUND_PENDING -> REFUNDED
```

Design decisions to justify in writing:

- **No 2PC with the payment processor.** We call their API; we do not share a
  transaction manager. Their API is idempotent on our `reference`; ours is
  idempotent on our `idempotency_key`.
- **Timeouts, not locks.** A stuck capture blocks nothing else. It blocks
  *that account's* capture for the same `reference`.
- **Authorisation is not capture.** Store them separately so a capture failure
  does not require reversing an authorisation immediately — reverse it on the
  authorisation's own expiry, or force it. Writing this down prevents an
  entire class of "ghost authorisation" disputes.

### Step 4: The Reconciliation Loop (the real work)

Assume the happy path is broken and something must find it.

```
Every 15 minutes:
  1. Query the processor for all transactions in non-terminal states older
     than 90 s.
  2. For each, re-query by our reference (NOT by re-sending the request).
  3. Classify: we missed it | they missed it | genuinely in flight.
  4. Emit a correction event for anything in state 1 or 2.
  5. Emit a metric per classification; alert on "we missed it" > 0.
```

Required: a *contingency* path for "genuinely in flight" for more than 24 h —
a phone call to the processor's operations team is a legitimate step in this
state machine, and pretending otherwise is how systems accumulate invisible
money.

### Step 5: Idempotency Across the Whole System

One key derivation, agreed with every caller, documented in a shared spec:

```
idempotency_key = merchant_id + ":" + checkout_order_id + ":" + operation
```

Enforcement points, all of which you must implement:

| Layer | Mechanism |
|-------|-----------|
| Edge | Reject reuse with a *different* request body (409) |
| Service | Redis SETNX fast path for the hot case |
| Ledger | `UNIQUE` constraint — the real guarantee |
| Processor | Their reference field, stable across our retries |

Test the cross-layer case: same key, different amount → must be rejected, not
silently served the cached first response. This is the bug that produces
"customer was charged $10 but the receipt says $100".

### Step 6: Outbox and Event Delivery at Ledger Scale

```
Ledger DB -> outbox (same tx) -> poller (SKIP LOCKED) -> Kafka topic
    -> projections: balance cache, statements, reconciliation, analytics
```

Partition the topic by `account_id` to preserve per-account order. Measure
outbox drain latency and set the alerting threshold on *drain lag*, not on
publish errors — a stalled outbox is silent until someone queries a projection
and gets stale data.

**Deliverable:** a documented drain-latency SLO and the runbook for what to do
when it is breached.

### Step 7: Failure Drills

1. **Crash after charge, before recording.** Kill the service between the
   processor's success response and your DB write. Verify reconciliation
   recovers the capture and that the customer is not charged twice when
   checkout retries.
2. **Broker outage for 40 minutes.** Verify the outbox absorbs it, the
   projection goes stale by a bounded amount, and the drain completes after
   recovery. Measure the stale window.
3. **Duplicate checkout request.** Fire the same `checkout_order_id` 50 times
   concurrently. Assert exactly one capture.
4. **Clock skew / delayed response.** Return an old success response for an
   already-timed-out request. Verify the state machine handles the stale
   response instead of regressing the state.

### Deliverables

1. Invariant statement and the ledger entry schema with constraints.
2. State machine with every visible intermediate state documented.
3. Reconciliation loop with classification metrics and the 24 h contingency.
4. Layered idempotency with the cross-layer test (409 on key reuse with a
   different body).
5. Outbox to Kafka pipeline with a drain-latency SLO and runbook.
6. Four drill reports with timelines, plus one incident your drills found.
7. A regulator-facing audit export: reconstruct any account balance at any past
   timestamp, on demand, with a reproducible procedure.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Ledger | Mutable balance row | Immutable entries, rebuildable projection |
| Duplicate charge | App-level check | `UNIQUE` at storage + layered keys |
| Retry safety | New key per attempt | Business-identity key agreed across callers |
| Stuck money | Not considered | Reconciliation + 24 h contingency + metrics |
| Audit | "We have logs" | Reconstruct balance at timestamp, reproducible |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 9110 — *HTTP Semantics*: the normative definitions of `Idempotent`
  methods, `409 Conflict`, and `412 Precondition Failed`. Cite this when you
  need to justify idempotency keys or conditional requests to a non-engineer.
  https://www.rfc-editor.org/rfc/rfc9110.html
- Apache Kafka documentation — *design/delivery semantics* and the consumer
  group / offset commit model, which is what "at-least-once with an idempotent
  consumer" actually depends on.
  https://kafka.apache.org/documentation/

Both are stable, versioned references. Quote the RFC section number (not the
landing page) and check the Kafka version's exact consumer semantics before
relying on offset-commit behaviour — it has changed across major versions.