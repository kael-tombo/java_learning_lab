# Consistency Models - Real World Project

## Project: Per-Endpoint Consistency Policy for an Order Platform

### Objective
Audit an existing order, payment, and catalogue service and assign an explicit,
justified consistency level to every read and write endpoint — then prove each assignment
with a test that reproduces the failure the weaker model would permit.

### Why This Is a Real Problem
Teams inherit implicit consistency from whatever the ORM or client SDK defaults to. Nobody
chose eventual consistency for the payment-capture read; it was chosen by an omission. This
project converts omissions into decisions with owners and expiry dates.

### Architecture Overview
```
  Checkout (order svc)  ──strong──▶  Payment capture   (never stale: money)
          │
          ├──read-your-writes──▶  Customer order history
          │
          ├──monotonic reads──▶  Order detail page
          │
          └──eventual─────────▶  Catalogue / pricing feed  (stale is acceptable)
```

### Phase 1: Inventory the Endpoints (Week 1)
1. Enumerate every externally reachable read and write in the three services
2. For each, record the current effective model (framework default, client flag, DB setting)
3. Mark each as `explicit` or `implicit` — the implicit count is your real backlog
4. Capture current latency percentiles per endpoint as the cost baseline

### Phase 2: Classify by Harm (Week 2)
For each endpoint, ask: if this read is stale, what breaks?

| Harm class | Example | Required model |
|---|---|---|
| Irreversible financial | capture, refund, settlement | Strong (quorum) |
| Legally attributable | tax record, immutable receipt | Strong or append-only log |
| User-visible surprise | cart, order status | Read-your-writes / monotonic |
| Self-healing | recommendations, banners | Eventual |
| Derivable | analytics, audit projection | Eventual, rebuildable |

1. Assign every endpoint a harm class with a named owner
2. Anything in `Irreversible financial` that is not already strong becomes a P1 finding

### Phase 3: Implement the Policy Layer (Week 3)
1. Introduce `ConsistencyPolicy` per endpoint in config, not in code branches
2. Implement session tokens for read-your-writes: version stamp returned on write, required
   on subsequent reads for that session
3. Add sticky-replica routing for monotonic reads, with failover detection
4. Add a `ConsistencyAuditor` that fails the build if an endpoint has no declared policy

### Phase 4: Prove the Policies (Week 4)
1. Per endpoint, write a test that injects replication lag and asserts the policy holds
2. For each strong endpoint, demonstrate that the test *fails* when the policy is downgraded
3. Test the session-token expiry path explicitly — an expired token must not silently
   downgrade to eventual
4. Publish the test suite as the regression net for the whole policy

### Phase 5: Roll Out and Govern (Week 5+)
1. Ship policy changes behind flags, one service per week
2. Track the `implicit` count to zero as a burn-down metric
3. Quarterly review: has a new endpoint shipped without a policy? Add a CI gate if so
4. Document the session-token TTL and who owns it

### Deliverables
1. Endpoint-by-endpoint consistency register with owner, class, and model
2. `ConsistencyPolicy` implementation plus the `ConsistencyAuditor` build gate
3. Per-endpoint policy tests, including downgrade-detection tests
4. ADR explaining why the catalogue feed stays eventual

### Success Criteria
- Zero endpoints with implicit consistency at the end of the rollout
- Every strong endpoint has a test proving it refuses stale reads
- Payment capture latency impact measured and accepted by the owning team
- A new endpoint cannot merge without a declared policy

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon DynamoDB Developer Guide, "DynamoDB read consistency" —
  https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
  Use for: the production vocabulary of `ConsistentRead`, and the fact that eventually
  consistent reads are the default (and cost half a read unit). This is the canonical
  example of a team inheriting a consistency choice it never made.
- Martin Fowler, "Microservice Trade-Offs" —
  https://martinfowler.com/articles/microservice-trade-offs.html
  Use for: the "inconsistency window" — the period where a get can be served by a node that
  has not received your update. Quote this when a stakeholder asks why a read-your-writes
  session exists at all.

### Estimated Time
5 weeks part-time