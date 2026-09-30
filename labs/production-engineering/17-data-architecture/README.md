# Lab 17: Data Architecture & Migration Patterns
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Data

---

## 🎯 Objectives

- Design data models for scalability and performance
- Implement zero-downtime database schema migrations
- Handle data consistency in distributed systems
- Design for data archival and GDPR compliance
- Implement CQRS and event sourcing patterns
- Master database sharding and partitioning
- Design for polyglot persistence (right DB for right job)

---

## 📖 Real-World Context

**"The Migration That Ate Production"**: Team needed to add an index to a 500-million-row table. They ran `CREATE INDEX` in production. MySQL locked the table for 3 hours. All writes failed. The fix that should have been used: `CREATE INDEX CONCURRENTLY` (PostgreSQL) or pt-online-schema-change (MySQL) — tools that add indexes without table locks. Database migrations at scale require different thinking than migrations on a 10,000-row table.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Data modeling, ACID, BASE, consistency patterns |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Migration disasters and data corruption incidents |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Flyway, online schema changes, CQRS implementation |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Database selection and data architecture patterns |
| [RUNBOOKS.md](./RUNBOOKS.md) | Data migration emergency runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Data architecture interview questions |
| [EXERCISES.md](./EXERCISES.md) | Design a sharded data architecture |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Data anti-patterns (god table, no sharding strategy) |
| [CHECKLIST.md](./CHECKLIST.md) | Data architecture readiness checklist |

---

## 🔗 Related Labs
- Lab 05: [Database Production](../05-database-production/)
- Lab 11: [Event-Driven Architecture](../11-event-driven-production/)
- Lab 12: [Caching Strategies](../12-caching-production/)
