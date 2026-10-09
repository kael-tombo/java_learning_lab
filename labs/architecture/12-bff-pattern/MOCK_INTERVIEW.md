# Mock Interview: Backend for Frontend (BFF) Pattern

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Designing APIs for a multi-client platform

**Interviewer**: "We have mobile apps (iOS, Android), a web app, and a third-party API. Currently, all clients consume the same API, causing inefficiencies. How do you fix this?"

**Candidate**: "I'd implement the Backend for Frontend (BFF) pattern. Each client type gets its own dedicated backend that optimizes the API for that specific client's needs."

**Interviewer**: "What problems does the current shared API cause?"

**Candidate**: "Three main problems: (1) Over-fetching — mobile clients download data they don't need because the API serves desktop use cases. (2) Under-fetching — the web client makes multiple round trips to compose a page because the API doesn't aggregate data for that specific view. (3) Client-specific logic leaks into the shared API — conditional parameters, feature flags, platform-specific endpoints."

**Interviewer**: "Define the BFF structure."

**Candidate**: "Three BFFs: Mobile BFF (optimized for low bandwidth, battery efficiency, offline support), Web BFF (optimized for page rendering, SEO, streaming), and Public API (optimized for rate limits, API keys, developer experience). Each BFF sits between the client and the backend services."

**Interviewer**: "What does the Mobile BFF do differently?"

**Candidate**: "The Mobile BFF: (1) Returns smaller payloads — only fields visible on screen. (2) Batches multiple requests into one — a 'home screen' endpoint that aggregates data from 5 backend services. (3) Handles offline synchronization — conflict detection, delta updates. (4) Compresses responses (gzip, protobuf). (5) Implements retry logic for poor network conditions."

**Interviewer**: "How does the Web BFF differ?"

**Candidate**: "The Web BFF: (1) Returns HTML or JSON with full page data — over-fetching is fine on desktop. (2) Handles server-side rendering (SSR) for SEO. (3) Returns streaming HTML for fast page load. (4) Manages session state (cookies, CSRF tokens). (5) Optimizes for cacheability — CDN-friendly responses."

**Interviewer**: "What about the shared backend services?"

**Candidate**: "The backend services remain shared — Order Service, Product Service, User Service. Each BFF is a thin aggregation layer that communicates with these services internally. The BFFs don't contain business logic — they're translation and aggregation layers. Business logic stays in the services."

**Interviewer**: "How do you handle BFF maintainability?"

**Candidate**: "BFFs can become a maintenance burden if they each duplicate logic. Mitigations: (1) Share utility code (auth, logging, retry) via a shared library. (2) Use GraphQL for the BFF layer — each client defines its own query, avoiding per-client API development. (3) Ensure BFFs are thin — if a BFF has business logic, it should be moved to a backend service."

**Interviewer**: "When is BFF the wrong pattern?"

**Candidate**: "When you have a single client type (just a web app). When the shared API already meets all clients' needs efficiently. When the team is small and can't maintain multiple BFFs. BFF adds operational overhead — more services to deploy, monitor, and debug. Only introduce it when the shared API is demonstrably causing problems for specific clients."

---

## Key Takeaways

- BFF provides client-specific API optimization
- Mobile BFF: small payloads, batching, offline support
- Web BFF: full data, SSR, caching optimization
- Backend services remain shared; BFFs are thin aggregation
- Use GraphQL as an alternative to BFF for simpler cases

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

