# ANTI-PATTERNS: Chaos Engineering & Failure Testing
## Lab 18 | Production Engineering Academy

---

## Anti-Pattern 1: Running Chaos Without Automated Abort Conditions

### The Mistake
Injecting network failure or pod deletion in production without an automated Prometheus/Datadog circuit breaker watching the error budget.

### Why It Fails
If an unexpected vulnerability triggers a cascading outage, human engineers require minutes to notice, convene, and manually execute abort commands. By that time, thousands of customer transactions have failed and the monthly SLO is destroyed.

### The Correct Production Fix
Always link chaos experiments to automated monitoring triggers:
If `error_rate > 1%` or `p99_latency > 500ms`, the chaos controller must automatically abort within 5 seconds.

---

## Anti-Pattern 2: Running Chaos on Untested Failure Modes in Production

### The Mistake
Injecting catastrophic database failover into production before ever validating basic circuit breaker behavior in Staging or Canary environments.

### Why It Fails
Chaos engineering is about *confirming* hypotheses, not reckless gambling. If you do not know how your system will react, the experiment will almost certainly cause a customer-facing outage.

### The Correct Production Fix
Follow the **Chaos Promotion Pipeline**:
Unit tests (Mockito faults) $\rightarrow$ Integration tests (Testcontainers / Toxiproxy) $\rightarrow$ Staging Chaos Game Day $\rightarrow$ Production Canary Experiment.
