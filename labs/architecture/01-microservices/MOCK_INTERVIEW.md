# Mock Interview: Microservices Architecture

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design a ride-hailing dispatch system

**Interviewer**: "We're building a ride-hailing dispatch system. Walk me through how you'd design the microservices architecture."

**Candidate**: "Let me start by identifying the bounded contexts. I see: Rider Management, Driver Management, Trip Dispatch, Payment Processing, and Notification. Each maps to a microservice boundary."

**Interviewer**: "Interesting. Why not a monolith for simplicity?"

**Candidate**: "Good question. Three reasons: (1) Different scaling needs — dispatch is real-time and high-throughput, payments needs strong consistency, notifications is throughput-oriented. (2) Different reliability requirements — dispatch can tolerate brief downtime, payments cannot. (3) Team autonomy — each domain can be owned by a separate team. I'd start with a modular monolith and extract services as bottlenecks emerge."

**Interviewer**: "Walk me through the dispatch service specifically."

**Candidate**: "The dispatch service is the most latency-sensitive component. It needs to match riders with nearby drivers in under 2 seconds. The key data structure is a geospatial index — I'd use Uber's H3 library for hexagonal indexing. Driver locations stream in via Kafka. The dispatch service subscribes to a 'driver location' topic, maintains an in-memory index in Redis, and exposes a gRPC endpoint for matching."

**Interviewer**: "What happens when a driver's location update is delayed?"

**Candidate**: "Excellent edge case. Stale location data leads to poor matches. I'd design the system to (1) expire stale driver locations after 10 seconds, removing them from the index, (2) have drivers send heartbeats every 3 seconds, and (3) treat missing heartbeats as 'driver offline' to avoid dispatching to a driver who's no longer available."

**Interviewer**: "How do you handle the race condition where two dispatch services assign the same driver?"

**Candidate**: "That's a critical problem. I'd use a distributed lock per driver — perhaps Redis Redlock — during the dispatch window. When the dispatch service selects a driver, it acquires a lock on the driver ID, then sends the dispatch request. If the lock is unavailable, the driver is already being dispatched to another rider, so we skip that candidate and try the next."

**Interviewer**: "What about the data consistency between services?"

**Candidate**: "For cross-service workflows, I'd use saga patterns. A trip lifecycle saga would orchestrate: RideRequested → DriverAssigned → PaymentAuthorized → TripStarted → TripCompleted → PaymentCaptured. If payment authorization fails, the saga triggers compensating actions — notify the rider and driver, and make the driver available again."

**Interviewer**: "How do you handle service discovery and communication?"

**Candidate**: "For synchronous queries, I'd use gRPC for low-latency internal calls. For async events, Kafka. Service discovery via Kubernetes DNS or a service mesh like Istio. For resilience, each service implements circuit breakers, retries with exponential backoff, and bulkheads for critical vs non-critical dependencies."

**Interviewer**: "How do you monitor such a distributed system?"

**Candidate**: "Three pillars: (1) Distributed tracing with OpenTelemetry — trace a single trip through all services. (2) Structured logging with correlation IDs — every log entry includes the trip ID. (3) Metrics aggregation — RED metrics for every service: Rate (requests/sec), Errors (error rate), Duration (latency P50/P95/P99). Custom dashboards for trip lifecycle stages."

**Interviewer**: "What's the biggest risk in this architecture?"

**Candidate**: "Distributed complexity — specifically, debugging failures across service boundaries. When a trip fails, is it the dispatch service timing out, the payment service rejecting, or the driver app not responding? This is why distributed tracing and good instrumentation are non-negotiable, not optional."

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Did you decompose the system into meaningful service boundaries?
- **Trade-off awareness**: Do you understand when microservices help vs hurt?
- **Failure handling**: Did you proactively address failure modes?
- **Operational maturity**: Did you discuss observability, deployment, and monitoring?

## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions — ask "why microservices?" not just "how to build them"
- Discuss organizational alignment (Conway's Law) — service boundaries should match team boundaries
- Address data consistency challenges — the hardest part of microservices
- Consider migration strategy — you're not building from scratch
- Discuss cost implications — microservices are operationally expensive

## Common Follow-Up Questions

1. "How would your design change if the system had 100x more traffic?"
   - Introduce more partitions, add caching layers, consider read replicas
2. "What if the team grows from 3 to 30 engineers?"
   - Each service becomes owned by a dedicated team; API contracts become more formal
3. "How do you handle schema changes in event-driven communication?"
   - Schema Registry with backward compatible Avro/Protobuf schemas
4. "What's the first service you'd extract from the monolith?"
   - The one with the clearest boundary, most independent data, and highest change frequency
5. "How do you test inter-service interactions?"
   - Consumer-driven contract tests, integration test suites per service, end-to-end smoke tests

## Key Takeaways

- Start with bounded contexts, not technology choices
- Address failure scenarios proactively (stale data, race conditions)
- Use saga patterns for distributed transactions
- Treat observability as a first-class concern
- Consider team autonomy and organizational alignment

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Clear decomposition into meaningful boundaries
- **Trade-off awareness**: Understanding of when this pattern helps vs hurts
- **Failure handling**: Proactive identification of failure modes
- **Operational maturity**: Discussion of monitoring, deployment, and operations
- **Communication**: Ability to explain complex concepts clearly


## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions and ask clarifying questions
- Discuss organizational implications (team boundaries, Conway's Law)
- Address data consistency challenges proactively
- Consider migration and evolution strategy
- Discuss cost and operational trade-offs
- Connect technical decisions to business outcomes

## Common Follow-Up Questions

1. ""How would this design change at 100x scale?"" — Discuss partitioning, caching, read replicas
2. ""How do you handle schema evolution?"" — Backward compatibility, versioning, migration strategies
3. ""Whats the biggest risk in this architecture?"" — Identify the weakest link and mitigation
4. ""How would you migrate from the current system?"" — Strangler Fig, feature toggles, parallel run
5. ""How do you test this system?"" — Unit, integration, contract, and end-to-end testing strategies

## Key Takeaways

This mock interview demonstrates the depth of discussion expected at staff+ level. The interviewer is not looking for a single ""correct"" answer but rather evaluating your thought process, trade-off awareness, and ability to communicate complex architectural decisions clearly.

