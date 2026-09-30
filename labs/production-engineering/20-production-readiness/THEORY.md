# THEORY: Production Readiness Reviews (PRR) & Operational Excellence
## Lab 20 | Capstone | Production Engineering Academy

---

## 1. The Google SRE Production Readiness Review (PRR) Framework

A Production Readiness Review assesses whether a service is reliable, secure, maintainable, and observable enough to be onboarded to production and handled by on-call engineers:

```
[Design Phase] ---> [Architecture Review] ---> [Implementation & Test]
                                                         |
                                                         v
                                              [Production Readiness Review]
                                                         |
                                 +-----------------------+-----------------------+
                                 |                                               |
                                 v (Pass)                                        v (Gaps Found)
                      [Tier-1 Production Launch]                       [Remediation Sprint]
```

### The 8 Pillars of Production Readiness
1. **Design & Architecture**: Clear bounded contexts, absence of single points of failure (SPOF), stateless request workers.
2. **Capacity Planning & Scalability**: Stress tested to $3\times$ peak load, auto-scaling policies configured.
3. **Observability**: Metrics, OpenTelemetry traces, structured JSON logs, burn-rate alerting.
4. **Reliability & Resilience**: Timeouts on all sockets, circuit breakers, retries with jitter, graceful shutdown.
5. **Security & Compliance**: Secrets in Vault/KMS, non-root containers, zero static credentials, dependency vulnerability scans.
6. **Release Engineering**: Canary deployments, automated metric analysis rollback, backward-compatible database migrations.
7. **Emergency Preparedness & Documentation**: On-call rotation in PagerDuty, verified runbooks for all alerts, tested incident command protocol.
8. **Disaster Recovery (DR)**: Multi-AZ resilience, tested database point-in-time recovery (PITR), tested failover procedures.

---

## 2. Operational Readiness Scorecards & Service Tiers

Enterprises categorize applications into standardized operational tiers:

| Tier | Description | Availability Target | MTTR Target | Disaster Recovery RTO/RPO | Review Frequency |
|:---:|:---|:---:|:---:|:---:|:---:|
| **Tier 0 / Critical** | Core Payment, Authentication, Ledger | 99.99% | $< 10\text{ min}$ | RTO $< 5\text{m}$, RPO = 0 | Bi-weekly Audit |
| **Tier 1 / High** | Order Processing, Search, Catalog | 99.9% | $< 20\text{ min}$ | RTO $< 30\text{m}$, RPO $< 1\text{m}$ | Monthly Audit |
| **Tier 2 / Medium** | Notification, Analytics, Recommendations | 99.5% | $< 60\text{ min}$ | RTO $< 4\text{h}$, RPO $< 1\text{h}$ | Quarterly Audit |
| **Tier 3 / Low** | Internal Tools, Batch Reporting | 99.0% | Next Business Day | RTO $< 24\text{h}$, RPO $< 24\text{h}$ | Annual Audit |
