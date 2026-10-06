# Lab 10: Microservices

## Overview
Decomposing a monolith into independently deployable services: domain
boundaries, data ownership, communication styles, failure isolation, and the
migration path that keeps the business running throughout.

## Prerequisites
- Java 21+, solid understanding of monolith architecture
- Relational database and transaction fundamentals
- Basic networking and HTTP
- CAP theorem and distributed systems basics

## What You Will Learn
- How to find service boundaries using domain analysis, not table counts
- Data ownership: the database-per-service rule and why it is non-negotiable
- Sync vs async communication and when each is correct
- Circuit breakers, bulkheads, and graceful degradation
- The Strangler Fig migration and its verification window
- Testing, observability, and deployment of a distributed system

## Lab Structure
| File | Description |
|------|-------------|
| VISION.md | What this lab is for and how to use it |
| THEORY.md | Decomposition, communication, failure, migration |
| MATH_FOUNDATION.md | Latency compounding, capacity, failure probability |
| CODE_DEEP_DIVE.md | Saga orchestrator, outbox, breaker, service discovery |
| EXERCISES.md | 12 graded exercises with solutions |
| QUIZ.md | 15 questions with answers and explanations |
| FLASHCARDS.md | 60 review cards |
| MINI_PROJECT.md | A decomposed, failure-tolerant service set |
| REAL_WORLD_PROJECT.md | Migrating a monolith to microservices |

## Quick Start
```bash
cd 10-microservices
# 1. Read VISION.md, then THEORY.md
# 2. Use MATH_FOUNDATION.md to test your decomposition's latency and failure assumptions
# 3. Implement CODE_DEEP_DIVE.md
# 4. Complete EXERCISES.md, then test yourself with QUIZ.md
# 5. Build MINI_PROJECT.md, then plan REAL_WORLD_PROJECT.md
```

## Learning Path
1. `VISION.md` for the mental model.
2. `THEORY.md` for decomposition and communication patterns.
3. `MATH_FOUNDATION.md` for the latency and failure arithmetic.
4. `CODE_DEEP_DIVE.md` for the implementation.
5. `EXERCISES.md` to apply it; `QUIZ.md` to check yourself.
6. `MINI_PROJECT.md` for hands-on; `REAL_WORLD_PROJECT.md` for production.

## Key Topics
- Domain-driven decomposition and bounded contexts
- Database-per-service and the cost of cross-service joins
- Sync (REST/gRPC) vs async (events) communication
- Saga pattern, choreography vs orchestration
- Transactional outbox and idempotent consumers
- Circuit breakers, bulkheads, deadline propagation
- Strangler Fig migration with shadow verification
- Distributed tracing across service boundaries
- Per-service SLOs and error budgets

## Estimated Time: 7 hours