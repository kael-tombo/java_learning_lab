# Mock Interview: API Composition Pattern

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Designing a product detail page for an e-commerce platform

**Interviewer**: "Design the backend for a product detail page. A single page needs product info, inventory status, reviews, seller info, and recommendations. Currently the frontend calls 5 APIs. How do you improve this?"

**Candidate**: "I'd use the API Composition pattern with a gateway that aggregates data from multiple backend services into a single response."

**Interviewer**: "Walk me through the current problem."

**Candidate**: "The mobile client makes 5 sequential calls: (1) GET /products/{id} → product info. (2) GET /inventory/{productId} → stock status. (3) GET /reviews/{productId} → reviews. (4) GET /sellers/{sellerId} → seller info. (5) GET /recommendations/{productId} → recommendations. This causes 5 round trips from mobile, 5x latency because mobile-to-backend latency is high."

**Interviewer**: "How does the API Gateway change this?"

**Candidate**: "The gateway exposes a single endpoint: `GET /api/v1/product-detail/{id}`. When the gateway receives a request, it calls all 5 services IN PARALLEL (they're independent), aggregates the results, and returns a single response. The mobile client makes one call. The gateway handles fan-out and aggregation."

**Interviewer**: "What if one of the services fails?"

**Candidate**: "The gateway implements partial failure handling. If the recommendations service is down, the gateway returns the product detail with a `recommendations: null` or `recommendations: []` field and a warning. The client renders the page with 'recommendations unavailable' rather than blank. Each service call has its own timeout — if recommendations takes longer than 200ms, it times out and returns empty."

**Interviewer**: "How does the gateway handle different data shapes?"

**Partner**: "Each service returns its own data structure. The gateway transforms them into a unified product detail model. For example, the reviews service might return `{review_id, text, rating}` while the gateway's output has `{id, text, stars}`. This transformation logic is in the gateway — but it should be minimal. If transformation becomes complex, consider a dedicated composition service."

**Interviewer**: "How does this compare to GraphQL?"

**Candidate**: "GraphQL solves the same problem differently. With GraphQL, the client declares exactly what it needs, and the server (GraphQL resolver) fetches from multiple services to satisfy the query. The key difference: API Composition returns a fixed response shape; GraphQL returns a client-defined shape. GraphQL gives clients more flexibility but shifts complexity to the server-side resolver logic."

**Interviewer**: "When is API Composition the wrong choice?"

**Candidate**: "When the aggregated response has deeply nested data from different teams — you create a bottleneck in the gateway. When query patterns vary wildly across clients — GraphQL is better. When the aggregation logic is complex enough to need its own service with its own database — that's not composition, that's creating a new service with its own data."

**Interviewer**: "How do you handle caching for aggregated responses?"

**Candidate**: "Cache at the gateway level. The gateway caches the composed response by product ID with a TTL (60 seconds for product detail). When the cache is fresh, the gateway returns immediately without calling backend services. Cache invalidation: when product info changes, a service publishes a ProductUpdated event; the gateway subscribes and invalidates the cached response."

---

## Key Takeaways

- API Composition aggregates multiple service calls into one response
- Independent calls should be parallelized for minimal latency
- Partial failure handling ensures graceful degradation
- API Composition is simpler than GraphQL for fixed response shapes
- Caching at the gateway reduces backend load

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

