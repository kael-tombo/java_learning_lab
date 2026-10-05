# Real-World Project — Event-Driven Architecture

## Scenario

A financial services company processes millions of transactions daily.
The current synchronous architecture struggles with peak loads, and
business teams need real-time insights into transaction patterns,
fraud signals, and customer behavior. The system must process events
with exactly-once semantics for financial operations while allowing
eventual consistency for analytics.

## System Overview

The platform uses a central event backbone (Apache Kafka) with the
following event streams:

| Event Stream | Producers | Consumers |
|--------------|-----------|-----------|
| transactions | Payment Service | Fraud Detection, Analytics, Ledger |
| user-events | User Service | CRM, Analytics, Recommendations |
| notifications | All services | Notification Gateway |
| audit-events | All services | Compliance, Audit Log |

## Architecture Decisions

### Event Backbone
- **Apache Kafka** as the central event backbone
- Partitioned by entity ID for ordering guarantees
- Schema Registry (Avro) for event contract management
- Retention policies per topic (7 days for transactions, 1 year for audit)

### Delivery Semantics
- **Exactly-once** for financial transactions (idempotent producers + transactions)
- **At-least-once** for analytics and notifications (idempotent consumers)
- Dead letter topics with alerting for unprocessable events

### Event Design
- Events represent facts: `TransactionInitiated`, `TransactionCompleted`, `TransactionFailed`
- Enriched events carry context from multiple sources
- Event schema versioning with backward compatibility

### Consumer Architecture
- Consumer groups for parallel processing
- Backpressure handling through lag monitoring
- Graceful shutdown with offset commits

## Implementation Phases

### Phase 1: Foundation
1. Set up Kafka cluster with Schema Registry
2. Define event schemas and naming conventions
3. Implement event publishing library with outbox pattern
4. Build consumer framework with idempotency support

### Phase 2: Core Flows
5. Implement transaction event flow
6. Build fraud detection consumer
7. Build real-time analytics consumer
8. Implement notification event flow

### Phase 3: Reliability
9. Add dead letter topics and replay tooling
10. Implement consumer lag monitoring and alerting
11. Add end-to-end tracing with correlation IDs
12. Implement event replay for recovery

### Phase 4: Evolution
13. Add schema evolution tooling
14. Implement event sourcing for audit trail
15. Build event catalog for discoverability
16. Add data quality validation on events

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Kafka Documentation**: https://kafka.apache.org/documentation/
  Official Apache Kafka documentation covering architecture, configuration,
  and operational best practices for event-driven systems.

- **Martin Fowler — What do you mean by Event-Driven?**: https://martinfowler.com/articles/201701-event-driven.html
  Martin Fowler's analysis of event-driven architecture patterns,
  including event notification, event-carried state transfer, and event sourcing.

## Success Metrics

- Event processing latency: p99 under 500ms
- Zero data loss for financial events
- Consumer lag under 1000 messages during normal operation
- Schema evolution without breaking changes 100% of the time

## Lessons from Production

1. **Start with at-least-once and idempotent consumers** — exactly-once
   is expensive and often unnecessary; design for idempotency first.

2. **Monitor consumer lag religiously** — it's the earliest indicator of
   consumer problems and can prevent cascading failures.

3. **Version your events from day one** — retrofitting schema evolution
   onto existing events is painful and error-prone.

4. **Plan for event replay** — bugs in consumer logic will happen; the
   ability to replay events from a point in time is essential for recovery.
