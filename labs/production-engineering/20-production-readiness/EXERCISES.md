# EXERCISES: Production Readiness Review (Capstone)
## Lab 20 | Capstone | Production Engineering Academy

---

## Capstone Exercise: Comprehensive Production Readiness Audit

### Objective
Conduct an end-to-end Production Readiness Review (PRR) on a production microservice, identify critical operational vulnerabilities, and deliver a formal architectural sign-off report.

### Scenario
You are the Principal Architect tasked with reviewing the **Global Core Payment Gateway (v3.0)** prior to taking 100% of enterprise checkout traffic next week.

### Deliverables & Steps
1. **Run Automated PRR Manifest Linter**:
   Execute `./scripts/prr-lint.sh` against the deployment manifest. Identify any missing security, lifecycle, or probe configurations.
2. **Review Resilience & Connection Configurations**:
   - Audit HikariCP connection pool settings against the hardware core formula.
   - Verify Resilience4j Circuit Breaker and Rate Limiter configurations.
3. **Audit Observability & Alerting**:
   - Verify OpenTelemetry W3C trace context propagation across Virtual Threads.
   - Verify that all Prometheus alerts include a valid `runbook_url`.
4. **Author Formal PRR Audit Sign-Off Document**:
   - Fill out the complete Master PRR Scorecard (`CHECKLIST.md`).
   - Categorize all identified risks into Critical (Blocker), High (Remediate in 14 days), or Low.
   - Issue the final verdict: **GO**, **CONDITIONAL GO**, or **NO-GO**.
