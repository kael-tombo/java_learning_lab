# Real-World Project — Saga Pattern

## Scenario

A travel booking platform coordinates flights, hotels, car rentals,
and payments across multiple third-party providers and internal services.
A customer booking a vacation package requires all components to succeed,
or the entire booking must be cancelled with full refunds. Traditional
distributed transactions (2PC) are impractical due to the number of
independent services and external providers involved.

## System Overview

The booking saga coordinates the following services:

| Service | Step | Compensation |
|---------|------|-------------|
| Booking Service | Create booking record | Delete booking |
| Flight Service | Reserve flight seats | Release flight seats |
| Hotel Service | Reserve hotel room | Cancel hotel reservation |
| Car Rental Service | Reserve vehicle | Cancel vehicle reservation |
| Payment Service | Charge customer | Refund payment |
| Notification Service | Send confirmation | Send cancellation notice |

## Architecture Decisions

### Orchestration vs Choreography
- **Orchestration** chosen for complex, long-running bookings
- Central orchestrator (Booking Saga Manager) coordinates all steps
- Easier to understand and debug than choreography for this use case
- Clear visibility into booking state

### State Management
- Saga state persisted in PostgreSQL with step-level tracking
- Each step records: status, start time, completion time, compensation status
- Saga recovery job resumes interrupted sagas after crashes

### Compensation Strategy
- Compensations execute in reverse order of original steps
- Each compensation is idempotent (safe to retry)
- Compensation failures trigger alerts and manual intervention workflows
- Some compensations are asynchronous (e.g., refunds take 3-5 business days)

### Failure Handling
- Transient failures: retry with exponential backoff (max 3 retries)
- Permanent failures: trigger compensation immediately
- Timeout: steps have SLA; timeout triggers compensation
- Circuit breaker: if a service is down, fail fast and compensate

## Implementation Phases

### Phase 1: Core Saga
1. Implement saga orchestrator with state machine
2. Build Booking Service with saga participation
3. Implement compensation framework
4. Add saga state persistence and recovery

### Phase 2: Provider Integration
5. Integrate Flight Service with reservation/release
6. Integrate Hotel Service with reservation/cancellation
7. Integrate Car Rental Service with reservation/cancellation
8. Integrate Payment Service with charge/refund

### Phase 3: Reliability
9. Add retry policies and circuit breakers
10. Implement saga timeout handling
11. Add compensation failure alerting
12. Build saga monitoring dashboard

### Phase 4: Operations
13. Implement manual intervention workflows
14. Add saga replay for recovery
15. Build compensation audit trail
16. Add customer communication for saga failures

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Microservices.io — Saga Pattern**: (link removed)saga.html
  Comprehensive guide to the saga pattern, including orchestration and
  choreography approaches, compensation strategies, and implementation examples.

- **Chris Richardson — Microservices Patterns**: https://web.archive.org/web/20190125150822/https://microservices.io/book/
  Chris Richardson's book on microservices patterns, with detailed coverage
  of sagas, distributed transactions, and failure management in microservices.

## Success Metrics

- Booking success rate: over 95%
- Saga completion time: p99 under 30 seconds
- Compensation success rate: over 99.9%
- Zero orphaned reservations (all compensated)
- Customer notification within 5 minutes of saga outcome

## Lessons from Production

1. **Design compensations carefully** — some actions are hard to undo
   (e.g., flights already ticketed); plan for partial compensation and
   manual intervention.

2. **Idempotency is non-negotiable** — network retries, crashes, and
   duplicate messages mean every step and compensation must be idempotent.

3. **Monitor compensation failures** — a failed compensation means
   inconsistent state; alert immediately and have runbooks ready.

4. **Set realistic timeouts** — third-party providers may be slow;
   balance between failing fast and allowing legitimate slow operations.
