# Mock Interview: Saga Pattern

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design a distributed transaction for an e-commerce checkout

**Interviewer**: "Design the checkout flow for an e-commerce platform. It involves order creation, payment processing, inventory reservation, and shipping. How do you handle distributed transactions?"

**Candidate**: "I'd use the Saga pattern. A saga is a sequence of local transactions where each step has a compensating action for rollback. For checkout, the saga would orchestrate: CreateOrder, ReserveInventory, ProcessPayment, and ScheduleShipping."

**Interviewer**: "Choreography or orchestration?"

**Candidate**: "For this flow, orchestration. The checkout flow has clear sequential steps with specific compensation logic. An orchestrator manages the flow, tracks state, and handles failures. Choreography works better for simpler, more independent steps where events naturally trigger the next action."

**Interviewer**: "Walk me through the orchestrated saga."

**Candidate**: "The CheckoutOrchestrator receives the checkout request. Step 1: Send CreateOrder command to Order Service. If successful, the orchestrator records the state. Step 2: Send ReserveInventory command to Inventory Service. If successful, move to Step 3. Step 3: Send ProcessPayment to Payment Service. If payment fails, the orchestrator triggers compensating actions in reverse: ReleaseInventory (compensation for ReserveInventory), CancelOrder (compensation for CreateOrder)."

**Interviewer**: "How does the orchestrator handle state between steps?"

**Candidate**: "The orchestrator maintains a saga log. It persists the current state after each step — which steps completed, which failed, the data needed for compensating actions. If the orchestrator itself fails, another instance can recover by reading the saga log and continuing or compensating."

**Interviewer**: "What about semantic locking during the saga?"

**Candidate**: "Good point. The inventory should be 'reserved' not 'deducted' — a temporary hold that prevents other processes from using that inventory. If the saga completes, the reservation becomes a deduction. If the saga fails, the reservation is released. This prevents overselling during the saga execution window."

**Interviewer**: "How do you handle a scenario where a compensation also fails?"

**Candidate**: "That's the hardest case. The saga enters a 'compensation failed' state and requires manual intervention. I'd design the system to minimize this — compensating actions should be simple and unlikely to fail. For example, releasing inventory is a simple state change that shouldn't fail. A monitoring system alerts the operations team if compensations consistently fail."

**Interviewer**: "Isolation is a challenge with sagas. How do you handle concurrent sagas?"

**Candidate**: "Sagas lack ACID isolation. For the checkout scenario, I'd use countermeasures: (1) Semantic locking — reserves prevent concurrent modifications. (2) Commutative updates — inventory deductions are commutative, so order doesn't matter. (3) Pending state — orders are 'pending' until the saga completes, preventing downstream actions on incomplete orders."

**Interviewer**: "When would you choose saga over a distributed transaction (XA)?"

**Candidate**: "Saga is for long-lived transactions (seconds to hours). XA is for short-lived transactions (milliseconds). Saga handles business failures gracefully through compensation. XA requires all participants to support two-phase commit. For e-commerce checkout, saga is the right choice — the steps are long-running and involve external systems."

---

## Key Takeaways

- Sagas manage distributed transactions through local transactions + compensation
- Orchestration provides clear control flow; choreography offers better decoupling
- Saga logs ensure recovery from orchestrator failures
- Semantic locking prevents concurrent saga conflicts
- Design compensating actions to be simple and reliable

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

