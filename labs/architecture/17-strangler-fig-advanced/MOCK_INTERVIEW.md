# Mock Interview: Advanced Strangler Fig (Database Decomposition)

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Splitting a shared database during monolith migration

**Interviewer**: "Our monolith uses a single PostgreSQL database shared by all domains. We're extracting services but the database is tightly coupled. How do you decompose the database?"

**Candidate**: "Database decomposition is the hardest part of strangler fig migration. I'd use a phased approach: Phase 1 — Logical separation within the shared DB. Phase 2 — Database view/materialization for new services. Phase 3 — Independent databases with async synchronization."

**Interviewer**: "Walk me through Phase 1."

**Candidate**: "Phase 1 is about identifying and documenting the data ownership within the existing database. Even though all tables are in one database, each domain 'owns' specific tables. I'd mark each table with its owning domain: `orders` table → Order domain owned. `inventory` table → Inventory domain owned. `order_items` is a shared reference — Order domain owns the relationship, Inventory domain owns the product data within. We document these boundaries."

**Interviewer**: "Phase 2?"

**Candidate**: "Phase 2 creates a separation layer. The Order Service (new) needs inventory data. Instead of querying the monolith DB directly, it queries a database VIEW that only exposes the columns it needs. The monolith still owns the actual table. For writes, the Order Service calls the new Inventory Service API, which writes to the shared DB. This break the direct DB dependency."

**Interviewer**: "Phase 3?"

**Candidate**: "Phase 3 gives each service its own database. Data is migrated through an event-driven synchronization process. When inventory changes in the monolith DB, CDC (Change Data Capture) captures the change and publishes an event. The Inventory Service subscribes and updates its own database. Eventually, the new service's database is the source of truth, and the monolith's copy is deprecated."

**Interviewer**: "How do you handle foreign key constraints across databases?"

**Candidate**: "By design, you eliminate cross-database foreign keys. If the Order Service has an `inventory_id` column, it's a logical reference, not a foreign key constraint. The Order Service stores the ID but doesn't enforce referential integrity at the database level. Application-level checks ensure the referenced inventory item exists (via API call or cached data). This is a fundamental shift — you lose database-level referential integrity for loose coupling."

**Interviewer**: "What about queries that joined across domain tables?"

**Candidate**: "Those queries must be rewritten. Options: (1) The query becomes a saga — call Order Service for order data, call Inventory Service for inventory data, combine in application code. (2) Create a read model that denormalizes data from both services — a dedicated reporting database updated via events. (3) Accept that some queries now have eventual consistency."

**Interviewer**: "How do you handle the rollout?"

**Candidate**: "Incremental. For each domain, I extract the data ownership in a separate phase. I never try to split the entire database at once. The rollout plan: (1) Extract Order Service with its tables. (2) Verify and stabilize. (3) Extract Inventory Service with its tables. (4) Remove the Order Service's dependency on the old inventory tables. The monolith's database shrinks gradually."

---

## Key Takeaways

- Database decomposition requires a phased approach over weeks/months
- Phase 1: Logical ownership documentation within shared DB
- Phase 2: Views and API calls replace direct DB access
- Phase 3: Independent databases with event-driven sync
- Eliminate cross-DB foreign keys; use application-level references
- Rewrite cross-domain joins as application-level composition or read models

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

