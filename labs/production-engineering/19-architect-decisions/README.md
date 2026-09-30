# Lab 19: Java Architect Decision Framework
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Principal/Staff | **Domain**: Architecture

---

## 🎯 Objectives

- Apply a structured decision-making framework for architecture choices
- Write effective Architecture Decision Records (ADRs)
- Evaluate technology choices with TCO and risk analysis
- Balance short-term pragmatism with long-term technical vision
- Navigate organizational dynamics in technical decisions
- Communicate architecture to non-technical stakeholders
- Understand when to NOT invent, and when to innovate

---

## 📖 Real-World Context

**"The Framework War"**: Two senior engineers disagreed on whether to use Spring Boot or Quarkus for a new service. The debate went on for 3 weeks. No decision was made. A junior developer eventually used Spring Boot "because that's what we know." Three months later, they needed native compilation for Lambda — Quarkus would have been better. The real failure wasn't the choice — it was the **decision process**. An ADR written in the first week would have captured the context, options, and criteria.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Decision frameworks, ADRs, technical risk analysis |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Architecture decisions that went well and badly |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | ADR templates, architecture diagrams as code |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | 20 real architectural decisions with full context |
| [RUNBOOKS.md](./RUNBOOKS.md) | Architecture review process runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Architect-level "how would you design X" questions |
| [EXERCISES.md](./EXERCISES.md) | Write ADRs for 5 real-world scenarios |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Architecture anti-patterns (YAGNI violation, resume-driven) |
| [CHECKLIST.md](./CHECKLIST.md) | Architecture review checklist |

---

## 📝 ADR Template

```markdown
# ADR-042: Use Event Sourcing for Order State Management

## Status: Accepted

## Context
Order state transitions are complex and frequent. Audit trail is legally required.
Multiple services need to react to order events asynchronously.

## Decision
Implement event sourcing for the Order aggregate. Events stored in Kafka.
Current state rebuilt from event stream. Snapshots for performance.

## Consequences
+ Complete audit trail (legal compliance built-in)
+ Loose coupling via events
+ Temporal queries possible (state at any point in time)
- Increased complexity vs simple CRUD
- Eventual consistency (not immediate read-after-write)
- Kafka dependency (single point of failure if not HA)

## Alternatives Considered
1. State-based with audit log → rejected: audit not reliable
2. State-based with CDC → rejected: complex, CDC has ordering issues

## Decision Authority: Principal Architect + Team Leads
## Review Date: 2027-03-30
```

---

## 🗺️ Key Architecture Decision Areas

```
Language/Runtime:
  Java LTS vs Java latest | JVM vs GraalVM Native | Spring vs Quarkus vs Micronaut

Communication:
  REST vs gRPC vs GraphQL | Sync vs Async | Request-Reply vs Event-Driven

Data:
  SQL vs NoSQL | Relational vs Document vs Key-Value vs Time-series
  ACID vs BASE | Consistency vs Availability | Sharding strategy

Deployment:
  Monolith vs Microservices vs Modular Monolith
  Containers vs VMs vs Serverless | Multi-region vs Single-region

State:
  Stateless vs Stateful | Cache-aside vs Write-through | Eventual vs Strong

Observability:
  OpenTelemetry standard | Centralized vs Distributed logging
  Pull-based (Prometheus) vs Push-based metrics
```

---

## 🔗 This is the Synthesis Lab — References All Previous Labs
Lab 19 is where you apply everything from Labs 01-18 to make real architectural decisions.
