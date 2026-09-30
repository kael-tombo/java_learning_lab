# Lab 02: Thread Concurrency & Virtual Threads in Production
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Concurrency

---

## 🎯 Objectives

- Master Java concurrency primitives: synchronized, volatile, locks, atomics
- Understand the Java Memory Model (JMM) and happens-before
- Use `java.util.concurrent` correctly in production
- Design thread pools for different workload profiles
- Debug deadlocks, livelocks, and race conditions in live systems
- Leverage Java 21 Virtual Threads for massive I/O concurrency
- Know when to use reactive vs imperative threading models

---

## 📖 Real-World Context

A payment gateway processes 5,000 concurrent requests. Each request requires:
- Database lookup (50ms I/O)
- Fraud check service call (30ms I/O)
- Core banking API call (100ms I/O)
- Response assembly (5ms CPU)

With traditional threads: 5,000 platform threads × ~1MB stack = **5GB RAM** just for stacks.  
With Virtual Threads: 5,000 virtual threads → ~10-20 platform carrier threads → **negligible memory**.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | JMM, happens-before, concurrency primitives, virtual threads |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Real deadlock, race condition, thread leak incidents |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Complete Java concurrency patterns with production code |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Threading model decisions: reactive vs virtual threads |
| [RUNBOOKS.md](./RUNBOOKS.md) | Deadlock & thread leak incident runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Concurrency interview deep-dives |
| [EXERCISES.md](./EXERCISES.md) | Fix-the-race-condition hands-on exercises |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Concurrency anti-patterns with war stories |
| [CHECKLIST.md](./CHECKLIST.md) | Thread safety review checklist |

---

## 🔗 Related Labs
- Lab 01: [JVM Memory & GC](../01-jvm-memory-gc/)
- Lab 15: [Performance Engineering](../15-performance-engineering/)
- Lab 04: [Distributed System Resilience](../04-distributed-resilience/)
