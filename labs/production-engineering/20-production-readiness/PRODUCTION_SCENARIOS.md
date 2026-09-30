# PRODUCTION SCENARIOS: Production Readiness Case Studies
## Lab 20 | Capstone | Production Engineering Academy

---

## Scenario 1: The Bypassed PRR & Black Friday Meltdown

### Context
A fast-growing retail enterprise built a brand-new "One-Click Checkout" service. Under extreme business pressure to launch before Black Friday, executive leadership granted a waiver to skip the formal Production Readiness Review.

### The Disaster
- At 00:01 on Black Friday, 120,000 shoppers flooded the new checkout service.
- **Hour 1**: Database connection pools exhausted within 90 seconds because HikariCP had been configured with default 30-second connection timeouts and no pool sizing formula.
- **Hour 2**: When pods crashed, Kubernetes attempted to restart them, but the service lacked a `startupProbe`. Pods entered infinite `CrashLoopBackOff`.
- **Hour 3**: On-call engineers were paged, but there were **zero runbooks**, no Prometheus dashboards, and logs were unformatted plain text without trace IDs.
- **Hour 4**: The team attempted a manual rollback, but the database migration had dropped a column without backward compatibility, making rollback impossible!
- Total downtime: 9 hours. Estimated revenue loss: $18.5M.

### Post-Mortem Finding
Every single failure mode encountered during the outage was an explicit check item on the standard Production Readiness Review scorecard. Had the PRR been completed, all 5 failure modes would have been identified and resolved weeks in advance.

---

## Scenario 2: The Successful PRR That Saved Launch Day

### Context
A global logistics provider developed an AI-powered dispatch optimization platform.

### The PRR Audit
During the Phase 3 PRR review 2 weeks prior to launch:
1. SRE auditors reviewed the load test results and observed that p99 latency jumped from 20ms to 4,200ms when traffic exceeded 8,000 req/s.
2. GC log analysis revealed that young generation was sized too small, triggering continuous minor GC pauses and premature promotion into Old Gen.
3. Security auditors discovered that the container image ran as `root` (UID 0) and lacked an SSRF validator on outbound webhook URLs.
4. Launch was delayed by 4 days to tune JVM flags (`-XX:+UseZGC -XX:+ZGenerational`), add SSRF validation, and run as non-root user (UID 10001).
5. On launch day, the service processed 14,000 req/s with flawless 12ms p99 latency and zero incidents.
