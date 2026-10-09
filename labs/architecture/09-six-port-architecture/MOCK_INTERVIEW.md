# Mock Interview: Six-Port Architecture (Hexagonal Deep Dive)

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Designing a multi-channel customer support system

**Interviewer**: "Design a customer support ticket system that handles email, chat, and phone. How do you structure the architecture for flexibility?"

**Candidate**: "I'd use six-port architecture — an evolution of hexagonal architecture that explicitly distinguishes driving (inbound) and driven (outbound) ports. Each communication channel is a driving adapter that translates external protocols into use cases."

**Interviewer**: "Explain the driving and driven ports."

**Candidate**: "Driving ports are the use cases the application exposes: `CreateTicket`, `AssignTicket`, `ResolveTicket`. Driving adapters (email listener, chat bot, phone IVR) convert external inputs into these use case calls. Driven ports are what the application needs from outside: `TicketRepository`, `NotificationService`, `CustomerServiceClient`. Driven adapters implement these — PostgreSQL, Twilio, Salesforce."

**Interviewer**: "How does a new channel get added?"

**Candidate**: "Add a new driving adapter. For a WhatsApp channel, I'd implement a `WhatsAppAdapter` that receives WhatsApp messages, converts them to `CreateTicket` use case calls, and returns responses. The core domain doesn't change — it has no knowledge of WhatsApp. The port defines the contract; the adapter implements the protocol."

**Interviewer**: "How do you handle different state machines per channel?"

**Candidate**: "The core defines a generic ticket state machine: New → Assigned → InProgress → Resolved → Closed. Channel-specific states are handled in the adapter. The email adapter might have a 'waiting for customer response' substate, but it maps back to the core 'InProgress' state. The core stays channel-agnostic."

**Interviewer**: "What about channel-specific routing logic?"

**Candidate**: "Routing is a core use case — 'assign ticket to appropriate agent based on skill and workload.' The routing algorithm is in the core domain. But channel-specific routing rules (e.g., 'premium customers get priority in chat') can be adapter-specific. The adapter sets priority on the `CreateTicket` command; the core doesn't know whether the priority came from the channel or a business rule."

**Interviewer**: "How do you test this architecture?"

**Candidate**: "Core domain: pure unit tests with mock driven ports — fast, no infrastructure. Driving adapters: integration tests against the adapter with a mocked driving port. Driven adapters: integration tests against real infrastructure with a core use case as the driver. End-to-end: full stack tests that send an email and verify the ticket is created and assigned."

**Interviewer**: "What's the main benefit over traditional layered architecture?"

**Candidate**: "Testability and replaceability. In traditional layered architecture, the domain layer depends on the persistence layer (or at least knows about it). In six-port, the domain defines the persistence contract (port), not the implementation. You can replace the database, add a new channel, or change an external service without touching the core domain logic."

---

## Key Takeaways

- Six-port architecture distinguishes driving (inbound) and driven (outbound) ports
- Driving adapters convert external protocols into use case calls
- Core domain is completely isolated from infrastructure
- Adding new channels requires only adapter code, not domain changes
- Testing is layered: unit tests for core, integration for adapters

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

