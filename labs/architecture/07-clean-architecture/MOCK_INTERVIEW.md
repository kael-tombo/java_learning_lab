# Mock Interview: Clean Architecture

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Architecture for a loan application processing system

**Interviewer**: "Design a loan application processing system. How do you structure the code to ensure business rules aren't coupled to frameworks?"

**Candidate**: "I'd follow Clean Architecture. The dependency rule is strict: inner circles define policies, outer circles implement details. Dependencies point inward — outer circles depend on inner circles, never the reverse."

**Interviewer**: "Walk me through the layers."

**Candidate**: "Layer 1 — Entities: `Loan`, `Applicant`, `CreditReport`, `UnderwritingDecision`. These are enterprise-wide business rules. A `Loan` has invariants: interest rate within legal limits, loan amount within applicant's credit capacity.

Layer 2 — Use Cases: `SubmitLoanApplication`, `UnderwriteLoan`, `ApproveLoan`. These orchestrate entity behavior. `UnderwriteLoan` checks credit score, debt-to-income ratio, and loan-to-value ratio by calling entity methods.

Layer 3 — Interface Adapters: `LoanController` converts HTTP requests to use case inputs, `LoanPresenter` converts use case outputs to HTTP responses. `LoanRepository` interface defines persistence operations — the implementation is an outer detail.

Layer 4 — Frameworks & Drivers: Spring Boot controllers, JPA repositories, PostgreSQL database. These implement the interfaces defined in inner layers."

**Interviewer**: "How do use cases communicate with the database without depending on it?"

**Candidate**: "The use case depends on an interface — `LoanRepository` interface — defined in the use case layer. The actual implementation (`JpaLoanRepository`) is in the outer layer. This is the Dependency Inversion Principle at work. The use case calls `loanRepository.save(loan)` without knowing whether the implementation uses JPA, JDBC, or a file system."

**Interviewer**: "How does data flow through these layers?"

**Candidate**: "The HTTP request hits the controller (outer). The controller creates a use case input model and calls the use case (inner). The use case calls entity methods and repository interfaces. The repository implementation (outer) persists data. The use case returns an output model. The presenter (outer) formats it as JSON. Data crosses boundaries as simple data structures, not entities."

**Interviewer**: "How do you handle cross-cutting concerns?"

**Candidate**: "Through the Interface Adapter layer. A `LoggingLoanPresenter` decorates the real presenter. An `AuditLoanRepository` decorates the real repository. The use cases don't know about logging or auditing — these are composed in the configuration layer. This keeps use cases clean of cross-cutting concerns."

**Interviewer**: "When would Clean Architecture be overkill?"

**Candidate**: "For CRUD-heavy applications where business logic is thin — simple create, read, update, delete operations. For applications with a single delivery mechanism (just HTTP, no CLI, no batch processing). For small teams where the indirection overhead isn't justified by the benefits."

**Interviewer**: "What's the most common mistake implementing Clean Architecture?"

**Candidate**: "Letting entities leak into the outer layers. I see `LoanEntity` (JPA) being used everywhere, not just in the repository. Or the controller passing `Loan` objects directly to the use case. The boundaries must be strict — entities belong in the innermost layer, and outer layers use their own models for communication."

---

## Key Takeaways

- Dependency rule: dependencies point inward
- Entities contain enterprise-wide business rules
- Use cases orchestrate application-specific behavior
- Interface adapters translate between layers
- Data crosses boundaries as simple structures, not entities

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

