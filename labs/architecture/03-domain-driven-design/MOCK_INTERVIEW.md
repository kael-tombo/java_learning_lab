# Mock Interview: Domain-Driven Design

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design a payment processing platform using DDD

**Interviewer**: "Design a payment processing platform. Walk me through your DDD approach."

**Candidate**: "I'll start with domain analysis. The domain is payment processing. I identify three core subdomains: Payment Authorization (the core — this is our competitive advantage), Settlement (important but more straightforward), and Fraud Detection (supporting subdomain)."

**Interviewer**: "Define the bounded contexts."

**Candidate**: "Payment Authorization Context, Settlement Context, Fraud Detection Context, Dispute Management Context, and Notification Context. Each owns its own model and data."

**Interviewer**: "Walk me through the Payment Authorization context."

**Candidate**: "Within the Payment Authorization context, I have an aggregate called `Payment`. The aggregate root is `Payment` entity. It contains `Transaction` entities (authorization attempts), a `Money` value object, and `PaymentMethod` value object. Invariant: a payment cannot be captured more than the authorized amount. Another invariant: a refund cannot exceed the captured amount."

**Interviewer**: "Why is Payment the aggregate root and not Transaction?"

**Candidate**: "Because the consistency boundary is the payment — all invariants constrain the payment as a whole. Transactions within a payment can be added but the payment's total captures and refunds must be consistent. If Transaction were the root, we couldn't enforce payment-level invariants atomically."

**Interviewer**: "How do bounded contexts communicate?"

**Candidate**: "Through domain events. When Payment Authorizes, it emits `PaymentAuthorized` event. The Settlement context subscribes, the Fraud context subscribes. For the integration with external contexts, each context has an anti-corruption layer — for example, the Payment context translates the bank's model of a 'transaction' into its own `Authorization` concept."

**Interviewer**: "How do you handle the ubiquitous language across teams?"

**Candidate**: "The language is defined per bounded context. 'Authorization' in the Payment context means one thing; 'Authorization' in the Fraud context means risk scoring. We document the glossary per context. Cross-context communication uses published language — the events define the shared vocabulary. A context map documents how each context relates to others."

**Interviewer**: "When would you NOT use DDD for this system?"

**Candidate**: "If the system had simple CRUD operations — create account, update profile, delete — DDD adds complexity without benefit. DDD shines when you have complex business rules, not complex technology. Payment processing has rich business rules (authorization rules, settlement timing, reconciliation), so DDD is appropriate."

**Interviewer**: "How does DDD influence your microservice boundaries?"

**Candidate**: "Each bounded context maps to one or more microservices. The Payment Authorization context is one service. Fraud Detection is another. They communicate via domain events. If I'd drawn service boundaries differently — say, splitting Payment Authorization into two services — I'd have broken a bounded context and created consistency problems."

---

## Key Takeaways

- Start with domain analysis, not technology
- Bounded contexts define service boundaries
- Aggregate roots enforce consistency boundaries
- Anti-corruption layers protect your domain model
- Ubiquitous language is per-context, not global

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

