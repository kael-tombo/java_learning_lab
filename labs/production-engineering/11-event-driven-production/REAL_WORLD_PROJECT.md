# Lab 11: Event-Driven Architecture & Kafka in Production — Real World Project

## Scenario: "The Backlog We Did Not Know We Had"

You are a staff engineer on a retail platform: 12 Spring Boot 3 services, Java 21, Kubernetes, a 9-broker Kafka cluster (RF=3, 3,600 msg/s average, 34,000 msg/s at peak), PostgreSQL for OLTP, Redis for caching.

**The incident** — Black Friday, 11:20, peak trading window. Something is wrong and nobody knows what.

**What happened over 9 hours**:

1. **11:20** — `order-events` consumer group `fulfilment-writer` lag begins to climb: 200k, 600k, 1.4M. No alert fires. The dashboard exists but is on a wall display nobody reads.
2. **11:38** — An unrelated upstream HTTP 5xx alert fires on `payment-service`. The responder looks at the payment dashboard, sees nothing, and closes the alert. The lag dashboard is not linked from the alert.
3. **12:05** — Fulfilment starts falling behind the checkout SLA. Customer service reports orders "not confirming". A developer checks the Kafka consumer and sees `Rebalance` in the log, repeating every ~90 seconds. Diagnosis: `max.poll.records = 2,000` combined with a downstream `inventory-service` p99 that had risen to 260 ms after a database migration.
4. **12:05, the arithmetic** — `2,000 × 0.26 s = 520 s` per poll cycle against `max.poll.interval.ms = 300,000`. The consumer is evicted mid-batch forever. Effective throughput collapses to near zero while CPU sits idle.
5. **13:30** — The team raises `max.poll.records` to 200 *and* `max.poll.interval.ms` to 15 minutes. Throughput recovers; lag begins to drain.
6. **Meanwhile** — `notification-service`, a different consumer group on the same topic, had been silently consuming the growing backlog's *partitions* fine, so no other group alerted. Its own lag had been stable because it is cheap to process.
7. **20:15** — Lag finally reaches zero. Total impact: 9 hours of degraded fulfilment, 1.9M orders processed out of SLA window, 14,000 customer refunds, a Black Friday revenue miss of $2.1M. No data was lost.
8. **The luck**: `retention.bytes` happened to be 4 TB, and at peak production that is ~14 hours of backlog. At 20:15 the oldest unconsumed message was ~9 hours old. It was within ~5 hours of expiring.

**Postmortem finding**: three separate failures. (a) Consumer lag was monitored but not alerted, and the alert that did fire pointed at the wrong service. (b) `max.poll.records` and the downstream p99 were never compared, because nobody owns that relationship. (c) Retention was set by habit, not by outage tolerance — and it was within five hours of deleting 1.9M orders.

**Your job over 4 weeks**: make delivery guarantees explicit, make lag an alerting input with the right owner, size retention from an outage tolerance, and prove that the same event cannot be lost — with retention sized so that even a 24-hour outage is survivable.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Reconstruct and enumerate (Day 1–4)

### 1.1 Reconstruct the timeline

From consumer logs, broker metrics, and `kafka-consumer-groups` output: time → lag → rebalance count → poll cycle time → effective throughput → downstream p99. Compute the `poll_cycle` for the actual configuration and show it exceeded `max.poll.interval.ms`.

**Deliverable 1 — Causal analysis** with the arithmetic at each step, the 2-hour detection gap, and the misdirected-alert explanation.

### 1.2 Flow inventory

For every topic: producers, consumer groups, partitions, retention, expected rate (average and peak), the owner, and the business meaning of lag for that flow. For every consumer group: `max.poll.records`, `max.poll.interval.ms`, processing time p50/p99, dedup strategy, DLT, and on-call owner.

**Deliverable 2 — Flow and consumer inventory** with the full configuration table and the per-flow owner list.

### 1.3 Retention audit

For each topic compute:
```
retention_capacity_hours = retention_bytes / (peak_rate × avg_bytes_per_message)
```
Compare against the largest outage in the last 12 months. Any topic where capacity < max observed outage duration is a silent-loss candidate.

**Deliverable 3 — Retention audit table**: topic, capacity in hours, longest outage in hours, margin, verdict. The `order-events` result should be a near-miss with a documented margin.

### 1.4 Delivery-semantics audit

For every producer/consumer edge: what guarantee exists today, where is the dual-write, is the consumer idempotent, and what is the dedup TTL versus the redelivery window?

**Deliverable 4 — Delivery-semantics table**: edge, guarantee, dual-write present?, idempotency key, dedup TTL, redelivery window, TTL adequate?

---

## Phase 2 — Fix the immediate exposures (Day 4–8)

### 2.1 Consumer configuration standards

Define and apply per consumer class:

| Class | `max.poll.records` | `max.poll.interval.ms` | Rule |
|---|---|---|---|
| Cheap (< 20 ms/record) | 1,000 | 300,000 | batch freely |
| Medium (20–200 ms) | 200 | 600,000 | `records × p99 ≤ 0.5 × interval` |
| Expensive (> 200 ms) | 50 | 900,000 | prefer pause/commit/resume |

And the invariant, asserted in code review and in a CI config test:
```
max_poll_records × processing_time_p99 < max_poll_interval_ms
```
with the downstream p99 taken from the service's own telemetry, not a guess.

Also apply: `group.instance.id` for every consumer (static membership), MANUAL_IMMEDIATE commits, pause/commit/resume for the expensive class, and explicit `max.poll.records` (never the 500 default by accident).

**Deliverable 5 — Consumer configuration standard** applied to all consumer groups, with a before/after table and the p99 inputs used.

### 2.2 Retention from an outage tolerance

Define a platform rule:
```
retention_bytes ≥ peak_rate × avg_bytes × max_tolerable_outage_hours × safety(2)
```
Set `max_tolerable_outage` per flow from the business (checkout: 24 h; analytics: 6 h; audit: 1 year).

**Deliverable 6 — Retention policy** with the computed size per topic, the cost impact, and the approval to increase disk accordingly.

### 2.3 Alerting on lag with the right owner

- `deriv(lag[10m]) > 0` for 15 min → page the owning team (growth, not absolute lag).
- `oldest_unconsumed_age_seconds > retention × 0.5` → page: "you are halfway to data loss".
- `oldest_unconsumed_age_seconds > retention × 0.8` → **critical**: data is expiring.
- `increase(consumer_rebalances[5m]) > 5` → page (early warning for the storm).
- `poll_interval_margin = max_poll_records × processing_p99 / max_poll_interval_ms > 0.5` → warn. This is the alert that would have caught Black Friday at 09:00.
- DLT rate (5 min) and DLT depth.
- Outbox depth / oldest unpublished age.
- Producer error rate and retry rate.

Every alert routes to the owning team's rotation, with the dashboard and runbook linked, and a "no owner = no alert" rule so nothing is silently unowned.

**Deliverable 7 — Alert pack** with the measured lead time each alert would have given on Black Friday (simulated against the historical series).

---

## Phase 3 — Delivery guarantees (Week 2)

### 3.1 Outbox everywhere it matters

Identify every dual-write site (a DB transaction plus a Kafka publish). For the 9 that matter (order, payment, fulfilment, inventory, refund), implement the transactional outbox: outbox table in the same DB, relay with `FOR UPDATE SKIP LOCKED`, at-least-once publication, published lag metric.

**Deliverable 8 — Outbox implementation** for 9 flows, with the relay's publication-latency p50/p99 per flow, and the migration plan for the rest.

### 3.2 Idempotency and dedup TTL discipline

For every consumer: an idempotency key (business key where available, otherwise `(topic, partition, offset)`), check-and-insert in the same transaction as the effect, and a dedup TTL set from the **maximum redelivery window** (rebalance + relay retry + client retry), not from retention. Aim for hours, not days.

**Deliverable 9 — Idempotency standard** with the dedup TTL per consumer, the computed redelivery window that justifies it, and the dedup storage sizing.

### 3.3 Schema governance

- Schema Registry with `FULL_TRANSITIVE` (or `BACKWARD_TRANSITIVE` where a documented reader inventory justifies it) on every topic.
- CI runs `confluentinc/schema-registry` compatibility checks against the previous schema; breaking changes require an ADR + a versioned topic.
- A schema inventory: topic, schema id, version, owner, last changed, known consumers.

**Deliverable 10 — Schema governance** with the breaking-change gate, plus the results of replaying the last 12 months of schema changes through the checker (how many would have been blocked).

---

## Phase 4 — Prove it (Week 2–3)

Run the Black Friday event shape in a production-shaped environment, plus the surrounding failure modes:

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Baseline peak (34,000 msg/s) | all groups keep up; lag ~0; no alerts |
| S2 | Downstream `inventory-service` p99 → 260 ms (the Black Friday condition) | poll-margin alert fires *before* the storm; lag growth alert fires within 15 min |
| S3 | Same, with the new standard applied | no rebalance storm; consumer absorbs the latency via pause/commit/resume |
| S4 | Consumer group entirely down for 24 h | no data loss: retention sized for 24 h × peak × safety; lag drains afterwards; expiry alert never fires |
| S5 | Consumer group down for 48 h (over tolerance) | expiry alert fires at 50% and 80% of retention; documented data-loss volume; the runbook executes |
| S6 | Broker loss (1 of 3) at peak | producer retries, no loss (`acks=all`, idempotence); consumer lag blips and recovers |
| T7 | Poison message on a hot partition | 4 retries → DLT; partition keeps flowing; DLT alert within 5 min |
| T8 | Hot key (80% of traffic on one `orderId`) | skew detected and alerted; salting applied where ordering permits |
| T9 | Relay crash mid-batch | no lost events; no double effects; publication lag spike then recovery |
| T10 | Schema change to `OrderCreated` | a break is rejected in CI; the safe additive change succeeds |
| T11 | Poisoned consumer database | retries → DLT → partition continues; compensating DLT for business-invalid events |
| T12 | Black Friday peak + concurrent partition expansion | ordering impact documented and accepted/mitigated |

**Deliverable 11 — Resilience test report** with all twelve scenarios, measured lead times, and fixes for anything missed.

---

## Phase 5 — Operate it (Week 3–4)

- **Runbooks**: `RUNBOOK_CONSUMER_LAG.md`, `RUNBOOK_REBALANCE_STORM.md`, `RUNBACK_DATA_EXPIRY.md`, `RUNBOOK_DLT_BACKLOG.md`, `RUNBOOK_HOT_PARTITION.md`, `RUNBOOK_PRODUCER_RETRIES.md`. Each with symptom → first three commands → decision tree → escalation.
- **Dashboards**: per flow, with consumption rate, lag, lag growth, oldest-unconsumed age vs retention, rebalance rate, poll-margin, DLT, outbox depth, per-partition rate.
- **Ownership**: every topic and consumer group has an owning team in the catalogue, in the alert routing, and in the on-call escalation path. Unowned = alert disabled + a ticket to the platform team.
- **Game day**: S2, S4, T7, T9 with the on-call in business hours, measuring the time to first correct hypothesis.
- **Change management**: no `max.poll.records` change without a poll-margin recomputation; no retention reduction without a capacity recomputation; both enforced in CI for config-as-code.

**Deliverable 12 — Operational package**: runbooks, per-flow dashboards, ownership catalogue, game-day report, CI config checks.

---

## Phase 6 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| Lag alerting | none; dashboard only | growth + age-vs-retention + poll-margin alerts, routed to owners |
| Detection time for the Black Friday condition | 1h 45m (and misdirected) | < 10 min via poll-margin alert |
| Rebalance storms in 90 days | 6 | 0 |
| Flows with a stated delivery guarantee | 0 / 24 | 24 / 24 |
| Dual-write sites on money-moving flows | 9 | 0 |
| Consumers with idempotency + bounded dedup TTL | 4 / 31 | 31 / 31 |
| Topics with retention ≥ 24 h × peak × 2 | 3 / 24 | 24 / 24 |
| Time to expiry alert from outage start | n/a (silent) | < 1 h at 50% of retention |
| Data lost in a 24 h consumer outage | silent loss at ~14 h | none |
| Black Friday revenue miss (this class) | $2.1M | ~0 |
| Mean recovery from a downstream p99 regression | 9 h | < 20 min |

Institutionalize: a "flow template" in the platform starter (outbox + idempotent consumer + DLT + registry config + dashboard + alerts), a "new event flow" review checklist, retention and poll-margin calculations required in the flow's design doc, and a quarterly audit of ownership, retention, and dedup TTLs.

**Deliverable 13 — Business case + institutionalization**, including the disk cost of the retention increase traded against the $2.1M single-event exposure.

---

## Deliverables checklist

- [ ] Phase 1 causal analysis, flow/consumer inventory, retention audit, delivery-semantics audit.
- [ ] Phase 2 consumer standard, retention policy, alert pack with simulated lead times.
- [ ] Phase 3 outbox for 9 flows, idempotency standard, schema governance.
- [ ] Phase 4 twelve-scenario resilience report.
- [ ] Phase 5 runbooks, dashboards, ownership catalogue, game day, CI config checks.
- [ ] Phase 6 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "Consumers were slow" | `poll_cycle` arithmetic vs `max.poll.interval.ms`, 1h45m detection gap explained, alert misdirection explained |
| Inventory | "We have 24 topics" | Full flow/consumer configuration table with owners and p99 inputs |
| Retention | "We have 4 TB" | Capacity-in-hours per topic vs outage history, with the near-miss quantified |
| Guarantees | "Kafka is durable" | Explicit per-edge semantics, dual-write removal via outbox, idempotency with bounded TTL |
| Alerting | "Alert when lag is high" | Lag growth + age-vs-retention + poll-margin, routed to owners, with measured lead times |
| Proof | "Load test with a slow downstream" | Replays the exact p99 regression, plus 24/48 h outages, poison messages, hot keys, relay crash |
| Operations | "Watch the lag chart" | Runbooks, ownership catalogue, expiry-aware alerts, game day |
| Economics | Technical only | Retention disk cost traded against a $2.1M single-event exposure |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Apache Kafka — consumer configuration documentation (`max.poll.interval.ms`, `max.poll.records`, `group.instance.id`) and the design/consumer internals page** — https://kafka.apache.org/documentation/ — the authoritative source for the consumer configuration contract, including that `max.poll.interval.ms` bounds the time between `poll()` calls and that a consumer exceeding it leaves the group. `group.instance.id` (static membership) and its version-introduction caveats are documented with the config; verify the exact defaults and the KIP version for your broker release rather than quoting numbers from memory, since `session.timeout.ms` and rebalance behaviour have changed across Kafka versions.
2. **Google SRE Workbook — "Data Processing Pipelines" and "Monitoring Distributed Systems"** — (link removed) and (link removed) — the canonical treatment of end-to-end latency versus pipeline latency, the argument for monitoring *time-to-completion* (which for a stream is the lag you owe the user) rather than per-stage throughput, and the "at-least-once + idempotent processing" default that Kafka designs inherit. Also the source for why a "backlog alarm" should exist before a pipeline is considered safe.

Additional anchors worth verifying: Confluent Schema Registry compatibility modes for your registry version (`BACKWARD_TRANSITIVE` / `FULL_TRANSITIVE` semantics differ subtly between Confluent and Apicurio), Debezium's exactly-once/transactional behaviour and its connector configuration names, and your client library's `DefaultErrorHandler`/`DeadLetterPublishingRecoverer` configuration surface — these differ between Spring Kafka versions and are the most common source of a silently misconfigured retry/DLT policy.

---

## Reflection questions

1. An alert fired and pointed at the wrong service. What single change to your alert *routing* would have fixed it, and why is that a different problem from missing alerts?
2. The team raised `max.poll.records` *and* `max.poll.interval.ms` at the same time. Which of those actually fixed the storm, and what risk did the second one introduce?
3. Retention was 5 hours away from deleting 1.9M orders. What should have been the alert threshold, and why did nobody own retention?
4. Nobody owns the relationship between a consumer's batch size and its downstream's p99. Where should that ownership live — the consumer team, the platform team, or a machine?
5. If you could only add one alert to this estate, which one, and how many minutes of Black Friday would it have saved?
