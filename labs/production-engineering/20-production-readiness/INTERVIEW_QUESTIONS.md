# INTERVIEW QUESTIONS: Production Readiness & Enterprise Architecture
## Lab 20 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What is a Production Readiness Review (PRR) and what are the essential gates before taking live traffic?
**Answer**:
A PRR is an engineering audit conducted by SRE, Architecture, and Security prior to launching a service into production.
Essential gates:
1. **Observability**: Metrics with SLOs, structured JSON logging with distributed trace propagation (OpenTelemetry), and burn-rate alerts.
2. **Resilience**: Socket timeouts, circuit breakers, backoff with jitter, bulkhead isolation, and graceful shutdown (`preStop` hooks).
3. **Capacity & Performance**: Load tested to $3\times$ peak traffic with verified JVM memory allocation and GC pause time targets.
4. **Security**: Secrets injected from Vault/KMS, non-root container user, zero static credentials, dependency CVE scanning.
5. **Operational Preparedness**: PagerDuty on-call rotation with actionable, tested runbooks for every alert, and tested rollback procedures.

---

## Staff / Principal Level (8+ Years)

### Q2: As Principal Architect, you are asked to conduct a comprehensive architectural evaluation of a mission-critical banking core processing $100M/day. Walk through your evaluation methodology.
**Answer**:
1. **Failure Domain & Boundary Analysis**:
   - Trace all external network calls: Are all synchronous calls bounded by strict timeouts and circuit breakers?
   - Is there a single point of failure (SPOF)? Are dependencies distributed across multiple Availability Zones?
2. **Data Integrity & Consistency Guarantees**:
   - Audit transaction boundaries: Is the system using dual-writes? Are Sagas properly implemented with persistent state logs and guaranteed idempotent compensation?
   - What is the database replication lag? Are read models susceptible to dirty reads, and is Read-Your-Own-Writes enforced?
3. **Runtime & Container Engineering**:
   - Inspect JVM garbage collection profiles (G1 vs Generational ZGC) and verify container memory limits vs `-XX:MaxRAMPercentage` (ensuring 25–30% non-heap headroom).
   - Verify CFS CPU throttling metrics (`nr_throttled`).
4. **Security & Zero Trust**:
   - Audit secret lifecycle: Are database passwords dynamically rotated?
   - Is mTLS enforced between services? Are outbound HTTP calls protected against SSRF?
5. **Operational SRE Maturity**:
   - Audit error budgets and alerting: Are teams alerted on user-impacting SLO burn rates or noisy symptoms?
   - Review blameless post-mortem history and verify whether systemic action items are tracked and resolved.
