# VISION — API Gateways: The Edge Is a Product Decision
> Where this lab takes you: from "route requests" to deciding what belongs at the edge and what does not.

## The Arc
1. **Patterns** — reverse proxy, routing, composition/aggregation, and gateways as an abstraction boundary.
2. **Cross-cutting** — auth, rate limiting, quota, transformation, and where each belongs.
3. **Composition** — aggregating N calls into one response, and the failure semantics of doing so.
4. **Performance** — connection pooling, streaming vs buffering, and the latency you added.
5. **Operations** — config-driven routing, canary routing, and observability of the edge.

## Milestones (checkable)
- [ ] M1: implement a reverse proxy and explain how it differs from a load balancer.
- [ ] M2: aggregate three services into one response and define the failure behaviour.
- [ ] M3: implement a token-bucket rate limiter and show it is per-client, not global.
- [ ] M4: measure the latency cost you added and decide whether each filter earns its place.
- [ ] M5: route 5% of traffic to a canary and write the rollback trigger.

## Core Competencies
- Gateway patterns: proxy, gateway-as-abstraction, and composition; when each is right.
- Where each cross-cutting concern belongs — edge, service, or library.
- Failure semantics of aggregation: partial success, fail-fast, and fallback.
- Config-driven routing with per-route policies and a change process.

## Anti-Goals
- A gateway that becomes a monolith: business logic accumulating at the edge.
- Buffering a streaming response to "normalise" it, destroying the streaming benefit.
- Global rate limits where per-client limits were required.

## Interview Lens
- "What's the difference between an API gateway and a reverse proxy?"
- "Your aggregation endpoint returns stale prices sometimes. Explain the trade-off."

## 30-Day Plan
- Wk1 THEORY + EXERCISES: proxy implementation, routing, and aggregation.
- Wk2 QUIZ/FLASHCARDS to 90%+; rate limiting and performance experiments.
- Wk3 MINI_PROJECT with routing, auth, and composition.
- Wk4 REAL_WORLD_PROJECT: a production gateway for a real estate.

## Done = You Can
- Design a gateway that reduces client complexity without becoming the system that fails.
