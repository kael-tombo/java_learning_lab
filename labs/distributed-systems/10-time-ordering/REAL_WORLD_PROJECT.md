# Time and Ordering - Real World Project

## Project: Causality-Aware Event Ordering Across Services

### Objective
Add causal ordering guarantees to an existing event pipeline so that a consumer can never
observe an effect before its cause, and can *detect* violations when it happens.

### Why This Is a Real Problem
Retries, parallel consumers, and cross-region producers guarantee that events arrive out of
order sometimes. Today that shows up as a support ticket: an order cancelled before it was
created, an inventory release before the reservation. Detecting and reporting the ordering
violation is worth as much as preventing it.

### Architecture Overview
```
 Order svc ──▶ topic ─┬─▶ Inventory svc (causal consumer)
                      ├─▶ Billing svc    (causal consumer)
                      └─▶ Analytics      (order-tolerant)

 Envelope: { eventId, sourceId, hlc, causalContext (bounded), traceId }
```

### Phase 1: Find the Actual Violations (Week 1)
1. Pick one cross-service invariant that has ever been reported as violated
2. Instrument arrival order vs emission order for the involved events
3. Quantify: how often does event N+1 arrive before event N, and how long is the window
4. Confirm the business impact in incidents or support volume — if you cannot connect it,
   fix a more urgent problem instead

### Phase 2: Choose a Clock (Week 2)
| Approach | Cost | Use when |
|---|---|---|
| HLC on the envelope | 16 bytes, no coordination | most services; ordering + readable time |
| Vector clock | O(sources) bytes | you must detect concurrency explicitly |
| Per-key sequence numbers | small | ordering is naturally per aggregate (orderId) |
| Partition-ordered topic | zero app cost | broker guarantees it for you |

1. Prefer **per-key sequence numbers** when ordering is per aggregate — it is the cheapest
   correct answer and the broker can enforce it
2. Use HLC when you need cross-source total order plus readable timestamps
3. Use vector clocks only where you must distinguish "concurrent" from "ordered"
4. Document the choice per topic; do not apply one scheme everywhere

### Phase 3: Implement the Causal Envelope (Week 3)
1. Add to every event: `eventId`, `sourceId`, `hlc`, optional `causalContext`, `schemaVersion`
2. Bound the causal context — an unbounded vector clock is a payload that grows forever
3. Consumer side: maintain per-key `lastAppliedSequence`; buffer out-of-order events in a
   bounded window with a timeout, then apply
4. On window timeout, emit a **causality violation** metric with both event IDs — do not
   silently apply out of order
5. Make the consumer idempotent so buffered replay after restart is safe

### Phase 4: Make the Broker Do What It Can (Week 4)
1. Where per-key ordering is required, produce with the aggregate ID as the partition key
   so ordering is a broker guarantee rather than an application convention
2. Verify skew: no partition dominates, because one hot partition serialises everything
3. Where multiple topics are involved, document that cross-topic order is application-enforced
4. Add a test that asserts ordering invariants per key under injected reordering

### Phase 5: Operate (Week 5+)
1. Metrics: out-of-order arrival rate, buffer occupancy, window timeouts, causal violations
2. Alerts: causal violation rate above zero (this should be genuinely rare)
3. Runbook: "causality violation" — identify the pair, determine whether the invariant broke,
   decide whether replay is safe
4. Replay tooling: rebuild a consumer's state from the log with ordering enforced

### Deliverables
1. Baseline measurement of real ordering violations
2. Causal event envelope with bounded context and schema version
3. Per-key ordered consumer with buffering, timeout, and violation reporting
4. Tests under injected reordering, plus dashboards and the violation runbook

### Success Criteria
- Zero undetected out-of-order applications on the chosen invariant
- Any violation surfaces as a metric within one window timeout, not as a user bug
- Buffer memory bounded under sustained reordering, verified by stress test
- Consumer replay rebuilds identical state

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Kafka Documentation, "Message Delivery Semantics" and design sections —
  https://kafka.apache.org/documentation/#semantics
  Use for: the authoritative statement that ordering is guaranteed per partition, not per
  topic, and that the producer chooses the ordering scope by choosing the key. This is the
  citation that ends the "is Kafka ordered?" debate.
- Apache Kafka replication documentation —
  https://kafka.apache.org/documentation/#replication
  Use for: how in-sync replicas and the leader determine which records are acknowledged —
  directly relevant to whether an ordering violation is caused by a retry or by a replication
  gap. Pin to the version you run.

### Estimated Time
5-6 weeks part-time