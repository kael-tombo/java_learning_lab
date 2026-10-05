# VISION — GraphQL: One Endpoint, Client-Shaped Queries
> Where this lab takes you: from "REST but nested" to owning the N+1 problem and query cost control.

## The Arc
1. **The model** — schema, types, resolvers, and the schema-first contract.
2. **Execution** — the resolver pipeline, parallelism, and why fields are resolved per-parent.
3. **The N+1 problem** — batching, DataLoader, and what the query planner does not fix.
4. **Operation safety** — query depth, complexity, cost analysis, and timeouts.
5. **Evolution & trade-offs** — deprecation, federation, and when REST remains the right answer.

## Milestones (checkable)
- [ ] M1: define a schema and implement a resolver without a framework.
- [ ] M2: demonstrate the N+1 problem with a query counter, then fix it with batching.
- [ ] M3: set a depth/complexity limit and show a malicious query rejected.
- [ ] M4: explain why `DataLoader` caching is per-request and what breaks if it is shared.
- [ ] M5: argue for and against GraphQL for a specific API, and reach a defensible answer.

## Core Competencies
- Resolver execution semantics, and the per-parent field resolution that causes N+1.
- DataLoader batching and request-scoped caching.
- Query cost analysis, depth limits, and timeouts as abuse controls.
- Schema evolution: additive changes, deprecation, and nullability as a contract decision.

## Anti-Goals
- Enabling introspection on a public API with no authentication.
- Unbounded query complexity exposed to anonymous clients.
- Treating GraphQL as a replacement for every REST endpoint by default.

## Interview Lens
- "Explain the N+1 problem in GraphQL terms."
- "A client can query 10,000 records. What stops them?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: schema, resolvers, execution tracing.
- Wk2 QUIZ/FLASHCARDS to 90%+; DataLoader and cost analysis.
- Wk3 MINI_PROJECT: a schema with nested resolvers, batching, and limits.
- Wk4 REAL_WORLD_PROJECT: a federated or migrated API with production cost controls.

## Done = You Can
- Ship a GraphQL API that cannot be used to exhaust your database, and explain the
  trade-off you made to get there.
