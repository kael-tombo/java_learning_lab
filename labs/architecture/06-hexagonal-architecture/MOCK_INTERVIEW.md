# Mock Interview: Hexagonal Architecture (Ports & Adapters)

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design a notification service using hexagonal architecture

**Interviewer**: "Design a notification service. How would you structure the code to keep it maintainable and testable?"

**Candidate**: "I'd use hexagonal architecture (ports and adapters). The core domain is notification dispatch — business rules about when to send, which channel, retry logic. The infrastructure — email provider, SMS gateway, push notification service — are adapters that plug into the core."

**Interviewer**: "Define the core domain."

**Candidate**: "The core contains the `NotificationService` which takes a `NotificationRequest`, determines the appropriate channel(s), applies business rules (rate limiting, opt-out checks, priority queuing), and calls an output port to dispatch. The core has no dependencies on external libraries or frameworks — just plain Java objects."

**Interviewer**: "What are the ports?"

**Candidate**: "Input ports: `SendNotificationUseCase` — an interface defining what the application does. Output ports: `NotificationDispatcher` — an interface for sending notifications. The core defines these interfaces. Adapters implement them. This is the Dependency Inversion Principle — core defines contracts, infrastructure implements them."

**Interviewer**: "Show me the adapter structure."

**Candidate**: "The `EmailAdapter` implements `NotificationDispatcher` for email. The `SmsAdapter` implements it for SMS. The `PushAdapter` implements it for push notifications. Each adapter handles the specific provider's API, error handling, and retry logic. If we switch from SendGrid to Amazon SES for email, we only change `EmailAdapter` — core stays untouched."

**Interviewer**: "How does the application assemble these adapters?"

**Candidate**: "A configuration layer (Spring Boot @Configuration, Guice module, or a main function) wires the adapters to the core. The `NotificationService` receives the `NotificationDispatcher` implementations via constructor injection. The configuration decides which dispatchers to inject based on the environment or feature flags."

**Interviewer**: "How does this affect testing?"

**Candidate**: "The core can be tested with mock adapters — pure unit tests with no infrastructure. Integration tests test adapters against real providers. End-to-end tests verify the wiring. Testing the email adapter in isolation is straightforward because the adapter has minimal logic — it translates core types to provider-specific API calls."

**Interviewer**: "What are the downsides of hexagonal architecture?"

**Candidate**: "Indirection — you have interfaces, implementations, and wiring that can feel like overhead for simple operations. Not all applications benefit from it. For CRUD-heavy applications with thin business logic, hexagonal architecture adds unnecessary complexity. It shines when business logic is complex and you have multiple infrastructure options."

**Interviewer**: "How do you handle cross-cutting concerns like logging and metrics?"

**Candidate**: "These belong in the adapter layer, not the core. A `LoggingNotificationDispatcher` decorator wraps the real dispatcher and adds logging. A `MetricsNotificationDispatcher` tracks dispatch latency and success rates. This keeps the core free of infrastructural concerns and allows cross-cutting behavior to be composed via decorators."

---

## Key Takeaways

- Core domain is framework-free, infrastructure-independent
- Ports define contracts; adapters implement them
- Dependency inversion: core owns the interfaces
- Testability is a primary benefit of hexagonal architecture
- Cross-cutting concerns are composed as decorators outside the core

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

