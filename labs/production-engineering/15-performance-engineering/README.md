# Lab 15: Performance Engineering & Load Testing
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Performance

---

## 🎯 Objectives

- Design and execute production-representative load tests
- Interpret Gatling/k6/JMeter reports for bottleneck identification
- Profile under load with async-profiler and JFR
- Identify and fix throughput bottlenecks vs latency bottlenecks
- Understand Little's Law and queuing theory for capacity planning
- Perform back-of-envelope capacity calculations
- Set meaningful performance SLOs and track them

---

## 📖 Real-World Context

**"The 10x Test That Wasn't"**: Team load tested at 10x expected load. System held fine. On launch day, real traffic patterns were totally different: high concurrency on a single endpoint, not spread across endpoints. The load test used uniform traffic distribution. Real users hammered one endpoint. System buckled. Load testing without realistic traffic patterns is worse than useless — it creates false confidence.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Queuing theory, Little's Law, performance metrics |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Load testing war stories and production perf incidents |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Gatling simulation, k6 scripts, JMH benchmarks |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Performance vs correctness tradeoffs |
| [RUNBOOKS.md](./RUNBOOKS.md) | Performance degradation investigation runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Performance engineering interview questions |
| [EXERCISES.md](./EXERCISES.md) | Load test a service and find the bottleneck |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Load testing anti-patterns |
| [CHECKLIST.md](./CHECKLIST.md) | Performance testing readiness checklist |

---

## 📊 Key Performance Formulas

```
Little's Law:
  L = λ × W
  (avg items in system) = (arrival rate) × (avg time in system)

  Example: 1000 req/s arrival rate, avg 100ms response time
  → L = 1000 × 0.1 = 100 concurrent requests in flight

Amdahl's Law:
  Speedup = 1 / (1 - P + P/N)
  P = parallel fraction, N = processors
  
  Example: 80% parallel code on 8 cores
  → Speedup = 1 / (0.2 + 0.8/8) = 1 / 0.3 = 3.3x (not 8x!)
```

---

## 🔗 Related Labs
- Lab 01: [JVM Memory & GC](../01-jvm-memory-gc/)
- Lab 03: [Production Debugging](../03-production-debugging/)
- Lab 08: [Observability & SRE](../08-observability-sre/)
