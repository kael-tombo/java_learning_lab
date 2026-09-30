# Lab 06: Microservices Architecture at Scale
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 12 hours | **Level**: Expert | **Domain**: Architecture

---

## 🎯 Objectives

- Design microservice boundaries using Domain-Driven Design
- Implement API gateway patterns, service mesh concepts
- Handle service discovery, load balancing, and health checks
- Implement distributed transactions with Saga pattern
- Design for observability-first microservices
- Manage service versioning and backward compatibility
- Know when NOT to use microservices

---

## 📖 Real-World Context

**"The Microservices Regret"**: A startup rewrote their monolith into 47 microservices. Deployment complexity skyrocketed. Network latency added 15ms per service hop (6 hops = 90ms just in network). Debugging cross-service issues took days. They ended up re-merging 35 services back into a "modular monolith." The lesson: microservices solve organizational problems, not technical ones.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | DDD, service boundaries, inter-service communication |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Deployment failures, saga rollbacks, service mesh issues |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Spring Cloud, OpenFeign, distributed transactions |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Monolith vs microservices vs modular monolith |
| [RUNBOOKS.md](./RUNBOOKS.md) | Service dependency failure runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Architecture design interview questions |
| [EXERCISES.md](./EXERCISES.md) | Design a microservices decomposition |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Distributed monolith, chatty services, shared DB |
| [CHECKLIST.md](./CHECKLIST.md) | Microservices production readiness |

---

## 🔗 Related Labs
- Lab 04: [Distributed Resilience](../04-distributed-resilience/)
- Lab 07: [Kubernetes for Java](../07-kubernetes-java/)
- Lab 11: [Event-Driven Architecture](../11-event-driven-production/)
- Lab 19: [Architect Decisions](../19-architect-decisions/)
