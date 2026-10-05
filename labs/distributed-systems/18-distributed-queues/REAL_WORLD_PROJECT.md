# Distributed Queues - Real World Project

## Project: A Work Queue That Survives a Partial Region Outage

### Objective
Design a task-processing platform on a managed queue with explicit delivery guarantees,
idempotent workers, a real dead-letter workflow, and backlog behaviour that is survivable.

### Why This Is a Real Problem
Queues are easy to adopt and hard to operate. The realistic failures are: a poison message
that blocks a partition, a consumer that processes successfully and then fails to ack (now
processing twice), and a backlog that grows faster than it drains for four hours before anyone
notices.

### Architecture Overview
```
  Producers ─▶ topic (partitioned by entityId)
                  │
                  ├── group: notifications   (fan-out, at-least-once, dedupe by msgId)
                  ├── group: enrichment      (idempotent upsert, safe to retry)
                  └── group: billing         (strict: fenced lease + idempotency key)
                            │
                            ▼ on failure x N ─▶ DLQ ─▶ triage tool ─▶ replay

 Backlog metrics: queue depth, oldest-message age, DLQ depth, retry rate
```

### Phase 1: Pick Guarantees Per Consumer (Week 1)
| Consumer | Work type | Guarantee needed | Implementation |
|---|---|---|---|
| notifications | side effect, user-visible | at-least-once | dedupe on `msgId` in a send log |
| enrichment | DB upsert | at-least-once | natural idempotence via upsert |
| billing | financial | effectively-once | idempotency key + fenced lease |

1. Explicitly choose per consumer — a single queue-wide guarantee is a false abstraction
2. For the user-visible one, accept duplicates in the send log and dedupe at send time
3. For billing, refuse to start processing unless the idempotency key store is reachable

### Phase 2: Make Workers Idempotent (Week 2)
1. Every message carries a stable `idempotencyKey` derived from business identity, not from
   the transport's message ID
2. The key is written in the same transaction as the effect
3. Replaying a message must produce the same result, not a second effect
4. Test: replay 24 hours of messages into every consumer and assert zero double effects

### Step 3: Dead Letters as a Workflow (Week 3)
1. Max receive count configured per queue; exceeding it moves the message to the DLQ
2. **Redrive policy per message class:** notification failures should redrive automatically;
   a malformed payload never will, and retrying it forever burns the DLQ budget
3. Build a triage tool: list DLQ, show the failure reason, preview the effect, replay or drop
4. Triage is a human workflow with an audit trail — someone must own the DLQ depth
5. Alert on DLQ depth above zero for any queue, and on growth rate

### Step 4: Backlog and Capacity (Week 4)
1. Measure service rate per consumer group (messages/sec sustained)
2. Set autoscaling on queue depth *with lag* as the signal — depth alone reacts late
3. Compute the time to drain a peak: `backlog / (service_rate × consumers)` and publish it
4. Identify the burst scenario: what does a 10x event do to the backlog, and how long to clear?
5. Load test to confirm the drain model, and rehearse it once in production

### Step 5: Operate (Week 5+)
1. Dashboards: depth and oldest-message age per group, processing rate, DLQ depth, dedupe
   hit rate, latency distribution per group
2. Alerts: oldest-message age above threshold, DLQ non-empty, drain time above budget,
   consumer count below desired
3. Runbook: "backlog growing" — scale consumers, identify the slow stage, decide whether to
   shed low-priority work
4. Runbook: "DLQ filling" — triage, classify by failure reason, fix the cause before replay

### Deliverables
1. Per-consumer guarantee matrix with implementation notes
2. Idempotent workers with a 24-hour replay test proving no double effects
3. DLQ triage tool, redrive policy, and audit trail
4. Drain-time model, load test results, dashboards, and the two runbooks

### Success Criteria
- Replaying any 24-hour window produces no double effects in any consumer
- DLQ depth is alerted, owned, and driven to zero within one business day
- Peak backlog drains within the published budget under an induced 10x burst
- Every consumer has a documented guarantee and an idempotency implementation

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon SQS Developer Guide, dead-letter queues —
  https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
  Use for: maxReceiveCount semantics, redrive policies, and the visibility timeout model.
  Verify the current redrive-policy limits (maximum DLQs per source queue) before designing
  the triage workflow around them.
- Apache Kafka Documentation, consumer configuration —
  https://kafka.apache.org/documentation/#consumerconfigs
  Use for: `max.poll.records`, `max.poll.interval.ms`, and the rebalance behaviour that
  determines effective throughput. These settings explain why a healthy consumer group can
  still fall behind, which is a common misdiagnosis in backlog incidents.

### Estimated Time
6 weeks part-time