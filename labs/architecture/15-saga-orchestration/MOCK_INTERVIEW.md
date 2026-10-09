# Mock Interview: Saga Orchestration vs Choreography

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Designing a hotel booking distributed transaction

**Interviewer**: "Design a hotel booking flow: room reservation, payment, loyalty points credit, and confirmation. How do you handle it as a distributed transaction?"

**Candidate**: "I'd model this as a saga. The question is whether to use choreography (event-driven) or orchestration (centralized coordinator). The answer depends on complexity and change frequency."

**Interviewer**: "Describe the choreography approach."

**Candidate**: "Each service publishes events and subscribes to relevant events. Booking Service publishes `RoomReserved` → Payment Service subscribes, processes payment, publishes `PaymentProcessed` → Loyalty Service subscribes, credits points, publishes `LoyaltyCredited` → Notification Service subscribes, sends confirmation. Each service knows only about its immediate predecessor's event. Failure handling: Payment Service publishes `PaymentFailed` → Booking Service compensates by cancelling the room reservation."

**Interviewer**: "Describe the orchestration approach."

**Candidate**: "A BookingOrchestrator manages the flow. It sends commands to each service and tracks the saga state. Step 1: Send `ReserveRoom` to Booking Service → record state. Step 2: Send `ProcessPayment` to Payment Service → record state. Step 3: Send `CreditLoyalty` to Loyalty Service → record state. Step 4: Send `SendConfirmation` to Notification Service. If any step fails, the orchestrator triggers compensating actions in reverse order. The orchestrator persists its state in a saga log."

**Interviewer**: "Which approach do you choose and why?"

**Candidate**: "I'd start with orchestration for hotel booking. Reasons: (1) The flow has clear sequential dependencies — you can't credit loyalty until payment succeeds. (2) The compensation logic is non-trivial — cancelling a room and refunding a payment requires coordinated action. (3) Business requirements change frequently — the orchestrator makes it easy to add/remove steps. (4) Monitoring and debugging are simpler with a centralized saga log."

**Interviewer**: "What about the criticism that orchestration creates a 'god service'?"

**Candidate**: "Valid concern. To mitigate: (1) The orchestrator doesn't contain business logic — just flow coordination. (2) The orchestrator sends commands to services that still own their domain logic. (3) If the flow becomes too complex, split it into sub-orchestrators. The orchestrator for hotel booking might orchestrate sub-sagas for payment and loyalty."

**Interviewer**: "When would you prefer choreography?"

**Candidate**: "For simpler flows with independent steps. Example: when a user updates their profile, services that cache the profile need to invalidate their cache. Each service independently subscribes to ProfileUpdated event — no orchestrator needed. Choreography shines when steps can run in parallel and failure doesn't require complex compensation."

**Interviewer**: "How do you handle the 'dual write problem' — publishing events while updating state?"

**Candidate**: "Using the transactional outbox pattern. The service writes the state change and the event to the same database in one transaction. A separate process (CDC or outbox poller) reads the outbox and publishes events to the broker. This ensures atomicity: both the state change and the event happen, or neither does."

---

## Key Takeaways

- Orchestration: centralized coordinator, better for complex flows
- Choreography: decentralized events, better for simple independent steps
- Orchestrator should not contain business logic — only flow coordination
- Sagas require compensating actions for rollback
- Transactional outbox ensures reliable event publishing

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

