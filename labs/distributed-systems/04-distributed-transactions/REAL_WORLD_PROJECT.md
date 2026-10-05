# Distributed Transactions - Real World Project

## Project: Replacing Cross-Service 2PC with SAGA + Outbox in an Order Platform

### Objective
Migrate a live order flow that currently uses distributed 2PC across an order service, a
payment service, and a broker to a SAGA-plus-outbox design — including the compensating
business logic and the reconciliation process it implies.

### Why This Is a Real Problem
2PC across services has a well-known failure profile: a broker or payment provider outage
holds database locks for the full recovery window, and the coordinator itself is a
single point of failure nobody monitors. Migrating away is not a refactor — it requires
product sign-off on what "cancelled" means when the refund has already been initiated.

### Architecture Overview
```
 Order svc (local tx)          Payment svc (local tx)        Broker
 ┌──────────────────┐        ┌──────────────────────┐
 │ stock reserve    │        │ authorize            │
 │ outbox:          │───────▶│ idempotency key      │
 │  order.created   │        │ journal: auth state  │──▶ order.created
 └──────────────────┘        └──────────────────────┘
        │                            │
        │ relay (CDC or poll)        │ on failure
        ▼                            ▼
  Shipping svc                 Compensation queue
  consume (dedupe)              refund / release stock
```

### Phase 1: Map the Current Transaction (Week 1)
1. Diagram every resource the 2PC transaction touches and who holds locks
2. Measure how often transactions land IN_DOUBT and how long recovery takes
3. Identify the coordinator: what happens if it is down mid-commit, and who pages?
4. Write down the current business meaning of each partial state — you need this for
   compensation, and today nobody has it written down

### Phase 2: Define Compensations with the Domain (Week 2)
For each forward step, define the compensating action and its *observable* behaviour:

| Forward step | Compensation | Reality |
|---|---|---|
| Reserve stock | Release reservation | instant, safe |
| Authorize card | Void authorization | instant, but only within the auth window |
| Capture payment | Refund | days, and the customer sees a pending credit |
| Create shipment | Cancel label | instant, but a label may already be scanned |
| Send notification | Send correction email | **not compensable** |

1. Mark `send notification` and any customer-visible action as non-compensatable
2. For every non-compensatable step, decide the business rule: compensate-before or
   compensate-after, and who reconciles
3. Get this table signed off by product, not just engineering

### Phase 3: Implement the Outbox and Relay (Week 3)
1. Add an `outbox` table to the order service in the same local transaction as the state change
2. Build the relay: poll unpublished rows, publish with the row ID as message key, mark sent
3. Deduplicate on the consumer side using that key, with a retention window longer than the
   maximum relay retry period
4. Add a dead-letter path and a replay tool — you will need both in month two

### Phase 4: Migrate the Flow Incrementally (Week 4)
1. Introduce the SAGA orchestrator alongside the old path, disabled by flag
2. Shadow: run both, compare resulting state, log every divergence
3. Cut over one step at a time, starting with the most failure-prone (payment)
4. Remove the 2PC coordinator only after a full business cycle with no IN_DOUBT events

### Phase 5: Build Reconciliation (Week 5+)
1. Daily job: find sagas stuck in any non-terminal state beyond a threshold
2. Route them to a manual review queue with full step history, not an auto-retry
3. Metrics: saga duration percentiles, compensation rate, manual-review volume
4. Alert if compensation rate exceeds baseline — that means something upstream is degrading

### Deliverables
1. Compensations table with product sign-off
2. Outbox schema, relay service, deduplicating consumers, DLQ and replay tooling
3. SAGA orchestrator with persistent step journal and resume-after-crash
4. Reconciliation job plus runbook for manual review

### Success Criteria
- No IN_DOUBT states after cutover
- No lost or duplicated order.created events after consumer dedupe, measured over 30 days
- Every stuck saga surfaces in the reconciliation queue within 24 hours
- SAGA duration p99 is within the old transaction's duration budget

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Martin Fowler, "Microservice Trade-Offs" —
  https://martinfowler.com/articles/microservice-trade-offs.html
  Use for: the argument that microservices make distributed transactions "frowned on (for
  good reason)" and shift the burden to detecting out-of-sync state. This is the framing to
  cite in the ADR justifying why 2PC is being removed rather than tuned.
- Amazon DynamoDB Developer Guide, "Core components of Amazon DynamoDB" —
  https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html
  Use for: transaction and conditional-write primitives used to implement idempotency and
  the conditional outbox insert. Verify feature availability per region before promising it.

### Estimated Time
6-8 weeks part-time