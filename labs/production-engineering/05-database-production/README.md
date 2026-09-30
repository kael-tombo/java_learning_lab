# Lab 05: Database Performance & Connection Pools in Production
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Data Layer

---

## 🎯 Objectives

- Configure HikariCP connection pools for production workloads
- Write N+1-safe JPA/Hibernate code
- Understand and use database indexes effectively
- Master transactions: isolation levels, deadlocks, long transactions
- Implement read replicas and CQRS for scalability
- Handle schema migrations safely with Flyway/Liquibase
- Profile slow queries and optimize execution plans

---

## 📖 Real-World Context

**"The N+1 Apocalypse"**: A new feature ships. Internally, it loads a list of 500 orders, then for each order fetches the customer (another query), then for each customer fetches their address (another query). That's 1 + 500 + 500 = **1,001 database queries per page request**. At 100 concurrent users, that's **100,100 DB queries/sec**. The database CPU hits 100%, all queries slow down, cascading into a full outage. The fix? One `JOIN FETCH` in JPQL. 30-second code change, hours of downtime prevented.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Connection pooling, transaction isolation, indexing |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | N+1 disasters, connection pool exhaustion, deadlocks |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | HikariCP config, JPA optimization, query analysis |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | CQRS, read replicas, sharding decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | DB connection exhaustion & slow query runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Database performance interview questions |
| [EXERCISES.md](./EXERCISES.md) | Fix the N+1, optimize the slow query |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | DB anti-patterns (God transactions, cartesian products) |
| [CHECKLIST.md](./CHECKLIST.md) | Database production readiness checklist |

---

## ⚙️ HikariCP Production Config

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20        # Rarely > 20; DB is the bottleneck
      minimum-idle: 5              # Keep 5 connections warm
      connection-timeout: 3000     # Fail fast: 3s to get connection
      idle-timeout: 600000         # Remove idle connections after 10min
      max-lifetime: 1800000        # Replace connections every 30min
      validation-timeout: 1000     # Connection validation: 1s max
      leak-detection-threshold: 5000  # Warn if connection held > 5s
      pool-name: payment-db-pool
```

---

## 🔗 Related Labs
- Lab 12: [Caching Strategies](../12-caching-production/)
- Lab 17: [Data Architecture](../17-data-architecture/)
- Lab 04: [Distributed Resilience](../04-distributed-resilience/)
