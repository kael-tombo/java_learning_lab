# Lab 04: Distributed Systems Failures & Resilience
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Distributed Systems

---

## 🎯 Objectives

- Understand the 8 fallacies of distributed computing
- Implement circuit breakers, retries, and bulkheads with Resilience4j
- Design for partial failures (graceful degradation)
- Master consensus, split-brain, and distributed locking
- Handle network partitions and timeouts correctly
- Apply the CAP theorem to real design decisions
- Build idempotent APIs and at-least-once processing

---

## 📖 Real-World Context

**"The Cascading Failure"**: During a routine deployment, the recommendation service started responding slowly (high CPU). This caused the product detail page to wait for recommendations, blocking threads. Within 3 minutes, all threads on the product service were blocked. The product service stopped responding. This cascaded to the checkout service. Within 8 minutes, the entire platform was down — from one slow service.

This is a real pattern that happened at Netflix, Amazon, and countless others. This lab teaches how to design systems that don't cascade-fail.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | CAP, fallacies, circuit breakers, consensus |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Cascading failures, split-brain, network partition incidents |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Resilience4j, Feign, WebClient resilience patterns |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Resilience patterns: when to use what |
| [RUNBOOKS.md](./RUNBOOKS.md) | Cascading failure incident runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Distributed systems design questions |
| [EXERCISES.md](./EXERCISES.md) | Build a resilient microservice exercise |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) — | Distributed anti-patterns (sync coupling, no timeouts, etc.) |
| [CHECKLIST.md](./CHECKLIST.md) | Resilience readiness checklist |

---

## 🔖 Key Patterns

```java
// Circuit Breaker with Resilience4j
CircuitBreaker cb = CircuitBreaker.of("recommendation-service", CircuitBreakerConfig.custom()
    .failureRateThreshold(50)           // Open if 50% of calls fail
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .slidingWindowSize(10)
    .permittedNumberOfCallsInHalfOpenState(3)
    .build());

Supplier<List<Product>> decorated = CircuitBreaker.decorateSupplier(cb,
    () -> recommendationClient.getRecommendations(userId));

List<Product> recs = Try.ofSupplier(decorated)
    .recover(ex -> EMPTY_RECOMMENDATIONS)  // Graceful degradation
    .get();
```

---

## 🔗 Related Labs
- Lab 06: [Microservices at Scale](../06-microservices-scale/)
- Lab 11: [Event-Driven Architecture](../11-event-driven-production/)
- Lab 14: [Incident Response](../14-incident-response/)
