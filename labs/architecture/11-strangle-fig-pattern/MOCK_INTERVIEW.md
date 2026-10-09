# Mock Interview: Strangler Fig Pattern

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Migrating a monolithic e-commerce platform to microservices

**Interviewer**: "We have a 10-year-old monolith handling 500K orders/day. We need to modernize without downtime. Walk me through the strategy."

**Candidate**: "I'd use the Strangler Fig pattern — incrementally replace monolith functionality with microservices while routing traffic through an API gateway."

**Interviewer**: "Where do you start?"

**Candidate**: "Identify the first bounded context to extract. I look for: (1) A domain that changes frequently — high business value for extraction. (2) A domain with clear boundaries — low risk of monolith dependency. (3) A domain that can be extracted with minimal database changes. Often, I start with the user management or notification domain — they're relatively independent."

**Interviewer**: "Walk me through extracting the notification domain."

**Candidate**: "Phase 1: Build the new Notification Service alongside the monolith. Phase 2: Add a feature toggle in the monolith — when enabled, route notification calls to the new service instead of the internal code. Phase 3: Enable for a small percentage of traffic, monitor, gradually increase. Phase 4: Once fully rolled out, remove the notification code from the monolith."

**Interviewer**: "How do you handle the database during extraction?"

**Candidate**: "Database strangling is the hardest part. For notifications, the monolith had a `notifications` table shared with orders. I'd: (1) Add a `notification_service_id` column to the monolith's DB — dual-write to both DBs. (2) Create a database view or materialized view in the new service that reads from the monolith's DB. (3) Eventually, the new service owns the notifications data, and the monolith queries the new service when it needs notification data."

**Interviewer**: "How do you handle transactions spanning the monolith and new service?"

**Candidate**: "Eliminate distributed transactions. Use the saga pattern instead. For example, when a customer places an order and needs a confirmation notification, the Order service (still in monolith) emits an OrderPlaced event. The new Notification Service subscribes to that event and sends the confirmation. If sending fails, the Notification Service retries. There's no two-phase commit between monolith and service."

**Interviewer**: "What about rollback?"

**Candidate**: "Feature toggles are the safety net. If the new Notification Service has issues, I toggle the feature flag back to 'use monolith implementation' — instant rollback with no deployment. This is why feature flags are essential to strangler fig migration. They provide a kill switch for each extraction step."

**Interviewer**: "How do you know when the migration is complete?"

**Candidate**: "When the monolith handles zero functionality from the extracted domain and the old code is deleted. I track this in a 'migration scoreboard' — a dashboard showing: which domains are extracted, which are in progress, and which remain in the monolith. Target: monolith deletion. But the monolith may never fully disappear — some domains may stay if extraction cost exceeds benefit."

---

## Key Takeaways

- Strangler Fig incrementally replaces monolith functionality
- Feature flags enable instant rollback without deployment
- Database decomposition is the most challenging aspect
- Use saga patterns instead of distributed transactions
- Some functionality may never be worth extracting

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

