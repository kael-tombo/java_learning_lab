# Mock Interview: CQRS

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design a reporting dashboard using CQRS

**Interviewer**: "Design a reporting dashboard for an e-commerce platform. How would you approach the read vs write models?"

**Candidate**: "CQRS is a natural fit here. The e-commerce writes are transactional — orders, payments, inventory changes. The reads are analytical — revenue reports, sales trends, customer analytics. They have fundamentally different shapes."

**Interviewer**: "Explain the write side."

**Candidate**: "The write model is the command side. It processes commands like PlaceOrder, ProcessPayment, ShipOrder. Each command goes through validation, business logic, and persistence. The write model is normalized — orders table, order_items table, payments table. Strong consistency within each aggregate."

**Interviewer**: "And the read side?"

**Candidate**: "The read model is denormalized for query performance. A `daily_sales_summary` table might have columns: date, total_revenue, order_count, avg_order_value, top_selling_category. These are pre-computed from the write model and updated asynchronously. Queries are simple SELECT statements with no joins — fast and efficient."

**Interviewer**: "How does data flow from writes to reads?"

**Candidate**: "When the write side processes a command, it emits domain events. OrderPlaced triggers a projection that updates the read models. I'd use an event handler that subscribes to the event stream, transforms the event data into the read model format, and upserts it. For real-time needs, I'd use Kafka with stream processing."

**Interviewer**: "What about eventual consistency? The dashboard shows stale data."

**Candidate**: "Acceptable for reporting — most dashboards have 5-15 minute freshness SLAs. If a specific report needs freshness, I'd either (1) read directly from the write side for that report (bypassing CQRS for that query), or (2) implement a faster projection with CDC from the write database."

**Interviewer**: "When would CQRS be the wrong choice?"

**Candidate**: "When reads and writes have the same shape — simple CRUD where the read model is identical to the write model. When strong consistency between reads and writes is mandatory for every read. When the team is small and the complexity of maintaining two models outweighs the query benefits."

**Interviewer**: "How do you handle schema changes across read and write models?"

**Candidate**: "Versioned projections. Each projection specifies the version of the events it handles. When the write model changes, events get a new version. Old projections continue processing old-version events. New projections handle both. This allows independent evolution of read models without blocking the write side."

**Interviewer**: "What about the API? Does the client know about CQRS?"

**Candidate**: "No, the API abstracts it. The client calls `GET /api/reports/daily-sales` and gets a response. The service determines which read model to query. The client doesn't know or care about CQRS — it's an implementation detail. The API contract is stable even if the internal model changes."

---

## Key Takeaways

- CQRS separates read and write concerns for optimized performance
- Eventual consistency is acceptable for reporting and analytics
- Event-based projections keep read models in sync
- CQRS adds complexity — only use when read/write shapes diverge
- The API should hide the CQRS implementation from clients

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

