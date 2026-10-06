# Lab 09: API Gateways

## Overview
Multi-layer API gateways for a 200+ service platform: edge protection,
authentication, routing, aggregation, rate limiting, and observability as a
single deployable concern.

## Prerequisites
- Java 21+, familiarity with HTTP and REST
- OAuth 2.0 / JWT basics
- Basic reverse-proxy and load-balancer concepts

## What You Will Learn
- Why cross-cutting concerns belong at the edge, and where that rule breaks
- Four-layer gateway decomposition (edge, auth, routing, aggregation)
- Routing, transformation, and service discovery
- Aggregation and BFF patterns, including partial failure
- Rate limiting, quotas, and circuit breaking at the gateway
- Gateway observability: trace propagation and golden signals

## Lab Structure
| File | Description |
|------|-------------|
| VISION.md | What this lab is for and how to use it |
| THEORY.md | Gateway architecture, patterns, trade-offs |
| MATH_FOUNDATION.md | Latency budgets, fan-out, capacity, header cost |
| CODE_DEEP_DIVE.md | Router, BFF aggregator, JWT verifier, limiter |
| EXERCISES.md | 12 graded exercises with solutions |
| QUIZ.md | 15 questions with answers and explanations |
| FLASHCARDS.md | 60 review cards |
| MINI_PROJECT.md | A working multi-layer gateway |
| REAL_WORLD_PROJECT.md | Production gateway for 200+ services |

## Quick Start
```bash
cd 09-api-gateways
# 1. Read VISION.md, then THEORY.md
# 2. Work through MATH_FOUNDATION.md and budget a latency path
# 3. Implement CODE_DEEP_DIVE.md
# 4. Complete EXERCISES.md, then test yourself with QUIZ.md
# 5. Build MINI_PROJECT.md, then design REAL_WORLD_PROJECT.md
```

## Learning Path
1. `VISION.md` for the mental model.
2. `THEORY.md` for architecture and the layer decomposition.
3. `MATH_FOUNDATION.md` for the latency and fan-out arithmetic.
4. `CODE_DEEP_DIVE.md` for the implementation.
5. `EXERCISES.md` to apply it; `QUIZ.md` to check yourself.
6. `MINI_PROJECT.md` for hands-on; `REAL_WORLD_PROJECT.md` for production.

## Key Topics
- Edge / auth / routing / aggregation layer separation
- JWT verification, JWKS rotation, claim-based authorisation
- Path- and header-based routing, service discovery, load balancing
- BFF aggregation with partial-failure semantics
- Distributed rate limiting, quotas, and circuit breakers
- Request/response transformation and version translation
- Trace propagation and gateway-level RED metrics

## Estimated Time: 6 hours