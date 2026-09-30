# Lab 10: API Design & Evolution at Scale
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 8 hours | **Level**: Advanced | **Domain**: Architecture

---

## 🎯 Objectives

- Design APIs that survive years of evolution without breaking clients
- Implement versioning strategies (URI, header, media type)
- Master REST best practices and OpenAPI specification
- Design event-driven APIs with AsyncAPI
- Handle backward and forward compatibility
- Rate limiting, pagination, and bulk operation design
- API governance: standards, linting, contract testing

---

## 📖 Real-World Context

**"The Breaking Change"**: Team A changed a JSON field name from `customerId` to `customer_id` for "consistency." They announced it in Slack. 12 teams were using the API. 3 teams missed the announcement. On deployment day, 3 services broke in production. Emergency rollback. Post-mortem: API contracts must be enforced by tooling, not trust.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | REST principles, versioning, compatibility, OpenAPI |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Breaking changes, API deprecation failures |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Spring MVC REST, OpenAPI 3, contract testing |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | REST vs gRPC vs GraphQL decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | API breaking change emergency runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | API design interview questions |
| [EXERCISES.md](./EXERCISES.md) | Design a versioned API and migrate clients |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Anti-patterns (breaking changes, no pagination, etc.) |
| [CHECKLIST.md](./CHECKLIST.md) | API production readiness checklist |

---

## 🔗 Related Labs
- Lab 06: [Microservices at Scale](../06-microservices-scale/)
- Lab 09: [Security Engineering](../09-security-production/)
