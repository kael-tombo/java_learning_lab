# Lab 20: Production Readiness & SLO Engineering
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: SRE / Engineering Excellence

---

## 🎯 Objectives

- Define what "production ready" actually means for Java services
- Design SLIs, SLOs, and error budgets aligned to business requirements
- Build a production readiness review (PRR) process
- Implement graceful shutdown and startup for zero-downtime
- Define and test disaster recovery procedures
- Create runbooks for every production scenario
- Implement capacity planning with data-driven projections

---

## 📖 Real-World Context

**"The Production Readiness Review That Saved a Launch"**: A financial services team ran a PRR before launching their new payment service. The review found:
- No graceful shutdown → requests dropped during deployments
- No timeout on external calls → thread exhaustion
- No runbook for DB failover → no one knew what to do
- SLO defined as "99.9% availability" → but not measured
- Load test at 2x expected → not 10x

They delayed launch by 2 weeks. Those 2 weeks saved them from what would have been a P1 incident on day 1.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | PRR framework, SLO math, capacity planning |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Services that should have had a PRR |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Graceful shutdown, health endpoints, SLO tracking |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Production readiness criteria decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Comprehensive operational runbook template |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Production readiness interview questions |
| [EXERCISES.md](./EXERCISES.md) | Run a full PRR on a sample service |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | "We'll fix it in prod" anti-patterns |
| [CHECKLIST.md](./CHECKLIST.md) | **THE** ultimate production readiness checklist |

---

## ✅ Production Readiness Checklist (Summary)

### Reliability
- [ ] SLIs defined and measured
- [ ] SLOs set and agreed with product
- [ ] Error budget tracking automated
- [ ] Circuit breakers on all external calls
- [ ] Timeouts on all external calls
- [ ] Retries with exponential backoff + jitter
- [ ] Dead letter queues for async processing
- [ ] Rate limiting implemented

### Operability
- [ ] Health endpoints: liveness + readiness + startup
- [ ] Graceful shutdown (SIGTERM handled, in-flight requests complete)
- [ ] Configurable via environment variables (no redeploy for config)
- [ ] Runbook for every alert
- [ ] On-call rotation defined
- [ ] Escalation policy documented

### Observability
- [ ] Structured logging with trace correlation
- [ ] Business metrics tracked
- [ ] Technical metrics: latency, throughput, error rate, saturation
- [ ] Distributed tracing in all service calls
- [ ] Dashboards for service health
- [ ] Alerts with documented response procedures

### Security
- [ ] No secrets in code or config files
- [ ] Dependencies scanned for CVEs
- [ ] SBOM generated
- [ ] Authentication/authorization implemented
- [ ] PII fields encrypted or masked in logs
- [ ] Least-privilege service account

### Performance
- [ ] Load tested at 3x expected peak
- [ ] Load tested at realistic traffic patterns (not uniform)
- [ ] p99 latency verified under load
- [ ] Memory usage stable under sustained load
- [ ] No Full GC under expected load

### Data
- [ ] Backup strategy defined and tested
- [ ] Restore procedure documented and tested
- [ ] Data retention policy implemented
- [ ] Schema migrations are backward compatible
- [ ] DR failover tested

### Deployment
- [ ] Blue-green or canary deployment configured
- [ ] Automatic rollback on error rate increase
- [ ] Deployment takes < 10 minutes
- [ ] Rollback takes < 5 minutes
- [ ] Zero user-visible errors during deployment

---

## 🎓 Graduation: You Are Production Ready

Completing this lab means you have the knowledge to:
- Take ownership of a production Java service
- Be the incident commander during a P1 outage
- Make architectural decisions that will be right 5 years from now
- Mentor others in production engineering practices
- Lead a production readiness review

**Welcome to the Production Engineering Academy graduate program.**

---

## 🔗 Final Lab — Synthesis of All Labs
This lab references everything from Lab 01-19. It's your capstone.
