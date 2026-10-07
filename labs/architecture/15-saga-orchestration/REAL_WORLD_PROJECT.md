# Real-World Project — Saga Orchestration

## Scenario

A hotel booking platform coordinates reservations across multiple
services: room inventory, payment processing, loyalty points, email
notifications, and partner booking systems. A guest booking a room
requires all steps to succeed, or the entire booking must be reversed.
The platform uses saga orchestration to manage these complex,
long-running transactions with full visibility and control.

## System Overview

The booking saga is managed by a central orchestrator:

| Step | Service | Action | Compensation |
|------|---------|--------|-------------|
| 1 | Inventory Service | Reserve room | Release room |
| 2 | Payment Service | Charge card | Refund payment |
| 3 | Loyalty Service | Deduct points | Restore points |
| 4 | Notification Service | Send confirmation | Send cancellation |
| 5 | Partner Service | Sync booking | Cancel partner booking |

## Architecture Decisions

### Orchestrator Design
- **State machine-based orchestrator** with explicit state transitions
- **Persistent state** in PostgreSQL with step-level tracking
- **Event-driven step execution** — orchestrator publishes commands, services respond
- **Timeout management** — each step has SLA; timeout triggers compensation

### State Management
- **Saga state**: PENDING, RUNNING, COMPLETED, COMPENSATING, COMPENSATED, FAILED
- **Step state**: PENDING, EXECUTING, COMPLETED, FAILED, COMPENSATED
- **Recovery job** scans for interrupted sagas and resumes them
- **Audit log** records all saga actions for debugging

### Compensation Strategy
- **Reverse order** — compensations execute in opposite order of original steps
- **Idempotent compensations** — safe to retry if orchestrator crashes
- **Async compensations** — some compensations (refunds) take time
- **Manual intervention** — compensation failures trigger alerts and manual workflows

### Failure Handling
- **Transient failures**: retry with exponential backoff (max 3 retries)
- **Permanent failures**: trigger compensation immediately
- **Orchestrator failure**: recovery job resumes saga from last persisted state
- **Service unavailability**: circuit breaker + fallback to compensation

## Implementation Phases

### Phase 1: Foundation
1. Implement saga orchestrator with state machine
2. Build state persistence and recovery
3. Implement step execution framework
4. Add compensation framework

### Phase 2: Core Flow
5. Integrate Inventory Service
6. Integrate Payment Service
7. Implement compensation for both
8. Add saga monitoring and alerting

### Phase 3: Additional Steps
9. Integrate Loyalty Service
10. Integrate Notification Service
11. Integrate Partner Service
12. Add compensation for all steps

### Phase 4: Operations
13. Implement saga timeout handling
14. Add manual intervention workflows
15. Build saga monitoring dashboard
16. Implement saga replay for recovery

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Microservices.io — Saga Pattern**: (link removed)saga.html
  Comprehensive guide to the saga pattern, including orchestration and
  choreography approaches, compensation strategies, and implementation examples.

- **Chris Richardson — Microservices Patterns**: https://web.archive.org/web/20190125150822/https://microservices.io/book/
  Chris Richardson's book on microservices patterns, with detailed coverage
  of saga orchestration, distributed transactions, and failure management.

## Success Metrics

- Booking success rate: over 95%
- Saga completion time: p99 under 30 seconds
- Compensation success rate: over 99.9%
- Zero orphaned reservations
- Recovery time after orchestrator failure: under 5 minutes

## Lessons from Production

1. **Keep orchestrator stateless where possible** — state in the database,
   not in memory; this enables recovery and scaling.

2. **Design compensations as first-class operations** — they're not
   afterthoughts; they must be as reliable as the original operations.

3. **Monitor compensation failures** — a failed compensation means
   inconsistent state; alert immediately and have runbooks ready.

4. **Set realistic timeouts** — too short causes false failures;
   too long delays compensation; tune based on service SLAs.
