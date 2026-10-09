# Mock Interview: Layered Architecture

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Design a content management system

**Interviewer**: "Design a content management system (CMS). Walk me through the architecture."

**Candidate**: "I'd use a layered architecture — the traditional N-tier approach. It's a proven pattern for enterprise applications where the primary concern is separation of concerns, not distributed scale."

**Interviewer**: "Define the layers."

**Candidate**: "Four layers: (1) Presentation layer — REST controllers, request/response DTOs. (2) Application layer — service classes that orchestrate business logic. (3) Domain layer — entities that encapsulate business rules. (4) Persistence layer — repositories that handle database access."

**Interviewer**: "Walk me through creating a blog post."

**Candidate**: "The `POST /api/posts` request hits the `PostController` (presentation). The controller creates a `CreatePostRequest` DTO and calls the `PostService` (application). The service validates business rules — 'author has publishing permissions,' 'content passes moderation.' Then it creates a `Post` entity (domain) and calls `postRepository.save(post)` (persistence). The result flows back through the layers to the HTTP response."

**Interviewer**: "What are the dependencies between layers?"

**Candidate**: "Each layer depends on the layer below. Presentation depends on application. Application depends on domain. Domain has no dependencies. Persistence depends on domain (it knows about entities). The direction of dependency follows the layers: higher layers depend on lower layers."

**Interviewer**: "What are the limitations of this architecture?"

**Candidate**: "Three main limitations: (1) As the application grows, a layer becomes a 'god service' — the application layer accumulates all business logic. (2) It tends to become database-driven — domain entities mirror database tables. (3) It doesn't scale to distributed systems well — layers don't map to service boundaries. For a CMS, these limitations are manageable. For complex domains, DDD or hexagonal architecture is better."

**Interviewer**: "How do you prevent the layers from leaking?"

**Candidate**: "Strict layer boundaries. The presentation layer shouldn't know about the persistence layer. The application layer returns domain objects or DTOs, not database entities. The persistence layer handles ORM mapping internally. I enforce this through package structure and module boundaries. If a layer needs data from another, it goes through the proper intermediate layers."

**Interviewer**: "How does testing work in layered architecture?"

**Candidate**: "Each layer is tested independently. Unit tests for domain entities. Service-layer tests with mocked repositories. Controller integration tests. The layered structure makes testing straightforward — each layer has clear inputs and outputs. The challenge is preventing tests from becoming brittle when the internal structure changes."

**Interviewer**: "When is layered architecture the right choice?"

**Candidate**: "For applications with moderate complexity where the primary goal is separation of concerns. Enterprise CRUD applications, simple web services, internal tools. When the team is familiar with the pattern and the application is unlikely to need microservice decomposition. It's pragmatic and well-understood — not innovative, but reliable."

---

## Key Takeaways

- Layered architecture separates concerns into stacked layers
- Each layer depends on the layer below
- Strict boundaries prevent layer leakage
- Suitable for moderate-complexity enterprise applications
- Testing benefits from clear layer interfaces

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

