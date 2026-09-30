# CHECKLIST: Kafka Production Readiness
## Lab 11 | Production Engineering Academy

---

## 1. Producer Hygiene & Durability
- [ ] Producer configured with `acks=all` (or `acks=-1`).
- [ ] `enable.idempotence=true` configured to prevent duplicate writes on network retry.
- [ ] `retries` set to high value (`Integer.MAX_VALUE`).
- [ ] `max.in.flight.requests.per.connection` set to $\le 5$ (maintains ordering with idempotence).
- [ ] Direct dual-writing avoided (Transactional Outbox implemented).

## 2. Consumer Resilience & Pacing
- [ ] `CooperativeStickyAssignor` configured for partition assignment.
- [ ] `max.poll.interval.ms` explicitly configured with sufficient headroom above max batch processing time.
- [ ] `max.poll.records` sized conservatively (e.g. 50-100 records).
- [ ] `enable.auto.commit=false` with manual acknowledgment after successful processing.
- [ ] ErrorHandlingDeserializer and Dead Letter Queue (DLQ) configured to catch poison pills.

## 3. Topic & Broker Configuration
- [ ] Topic replication factor $\ge 3$.
- [ ] `min.insync.replicas` set to 2.
- [ ] Partition count sized based on peak consumer parallelism requirement.
- [ ] Consumer lag alerting configured in Prometheus/Burrow.
