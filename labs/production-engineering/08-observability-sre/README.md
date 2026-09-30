# Lab 08: Observability — Logs, Metrics, Traces
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: SRE / Observability

---

## 🎯 Objectives

- Implement the three pillars of observability: logs, metrics, traces
- Design SLIs, SLOs, and error budgets
- Configure Prometheus metrics in Spring Boot
- Set up distributed tracing with OpenTelemetry + Jaeger
- Build Grafana dashboards for Java service health
- Configure structured logging with correlation IDs
- Create alerting rules that reduce noise and increase signal

---

## 📖 Real-World Context

**"You Can't Debug What You Can't Observe"**: A payment service was degrading for 20 minutes before anyone noticed. The only alert was "service is down" — far too late. After implementing proper observability:
- SLO: p99 < 200ms
- Alert fires at p99 > 150ms (30% of error budget consumed)
- Now the team has 15 minutes to fix it before users notice

The difference: reactive firefighting vs proactive defense.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Observability pillars, SLI/SLO/SLA, OpenTelemetry |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Real cases where observability saved the day |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Micrometer, OpenTelemetry, structured logging |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Observability stack decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Monitoring alert response runbooks |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Observability and SRE interview questions |
| [EXERCISES.md](./EXERCISES.md) | Instrument a service from scratch |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Alert fatigue, vanity metrics, no tracing |
| [CHECKLIST.md](./CHECKLIST.md) | Observability readiness checklist |

---

## 📊 Key Metrics to Track for Every Java Service

```yaml
# Business metrics
payment_processed_total{status="success"} counter
payment_amount_dollars_total counter
order_creation_latency_seconds histogram

# Technical metrics  
http_server_requests_seconds{uri, method, status} histogram
jvm_memory_used_bytes{area} gauge
jvm_gc_pause_seconds histogram
hikaricp_connections_active gauge
hikaricp_connections_pending gauge
resilience4j_circuit_breaker_state gauge
```

---

## 🔗 Related Labs
- Lab 03: [Production Debugging](../03-production-debugging/)
- Lab 14: [Incident Response](../14-incident-response/)
- Lab 20: [Production Readiness](../20-production-readiness/)
