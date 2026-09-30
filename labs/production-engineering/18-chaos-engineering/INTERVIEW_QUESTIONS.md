# INTERVIEW QUESTIONS: Chaos Engineering & Fault Injection
## Lab 18 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What is the difference between Disaster Recovery (DR) testing and Chaos Engineering?
**Answer**:
- **Disaster Recovery (DR) Testing**: Evaluates whether a system can be restored from a total catastrophic event (e.g. primary data center destroyed, restore from cold backups, fail over DNS to disaster site). DR tests are typically planned weeks in advance, run once or twice a year, and often tolerate significant downtime during the transition.
- **Chaos Engineering**: Continuously and proactively injects realistic, small-scale turbulent conditions (e.g. packet loss, single pod kill, CPU starvation, disk fill) into running production or staging environments to verify whether automated resilience mechanisms (circuit breakers, retries, auto-scaling, leader elections) work seamlessly without user impact.

---

## Staff / Principal Level (8+ Years)

### Q2: How do you design an enterprise Game Day program for 50 distributed microservice teams without risking customer outages?
**Answer**:
1. **Safety Architecture (Automated Stop-Loss)**: Link chaos tooling directly to production SLO monitors. If error budget burn rate exceeds $2\times$, the chaos framework immediately executes emergency cleanup without human intervention.
2. **Progressive Promotion Pipeline**:
   - Level 1: Unit & integration testing using Mockito / Toxiproxy in CI.
   - Level 2: Staging Game Day injecting full AZ failure and database crashes.
   - Level 3: Production Canary testing (injecting faults into 1–5% of live traffic).
   - Level 4: Automated continuous chaos (running during business hours).
3. **Pre-Mortem & Hypothesis Requirement**: Teams must document their hypothesis: "If Service B latency increases to 3s, Service A circuit breaker will open within 2s and p99 checkout latency will stay $< 150\text{ms}$." If they cannot state the expected outcome, they are not ready to inject the failure.
