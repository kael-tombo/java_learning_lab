# Mini Project — Advanced Strangler Fig Pattern

## Goal

Migrate a legacy order management system to a new microservices
architecture using advanced strangler fig techniques: event interception,
parallel running, data synchronization, and automated result validation.

## Requirements

### Legacy System (Simulated)
- Monolithic order management
- Single database
- Emits events on order changes

### New System
- `Order Service` — order management
- `Notification Service` — order notifications
- `Analytics Service` — order analytics

### Advanced Techniques

**1. Event Interception**
- Capture legacy system events (order created, updated, deleted)
- Forward events to new system
- New system processes events independently

**2. Parallel Running**
- Route read requests to both systems
- Compare responses for validation
- Route write requests to legacy (new system syncs via events)

**3. Data Synchronization**
- CDC (Change Data Capture) from legacy database
- Event-driven sync to new system
- Conflict resolution strategy

**4. Automated Validation**
- Compare responses from both systems
- Log discrepancies for investigation
- Alert on validation failures

## Technical Specifications

1. **Event interception**
   - Intercept legacy system events
   - Forward to message bus
   - New system consumes events

2. **Parallel running**
   - Route reads to both systems
   - Compare responses
   - Log differences

3. **Data sync**
   - CDC from legacy database
   - Event-driven updates to new system
   - Bidirectional sync where needed

4. **Validation**
   - Automated response comparison
   - Discrepancy logging
   - Validation metrics and alerting

## Steps

1. Set up legacy system with event emission
2. Implement event interception
3. Build new Order Service
4. Implement CDC from legacy database
5. Set up parallel running for reads
6. Implement response comparison
7. Add discrepancy logging and alerting
8. Gradually shift write traffic
9. Decommission legacy system
10. Write tests for event interception and sync

## Acceptance Criteria

- [ ] Legacy events are captured by new system
- [ ] Both systems run in parallel with consistent data
- [ ] Automated validation compares responses
- [ ] Discrepancies are logged and alerted
- [ ] Write traffic shifts gradually
- [ ] Legacy system is decommissioned
- [ ] Rollback is possible at any phase

## Stretch Goals

- Implement shadow mode (new system processes but doesn't affect users)
- Add automated rollback on validation failure
- Implement feature flags for granular control
- Add migration progress dashboard
