# ANTI-PATTERNS: Production Readiness & Launch Engineering
## Lab 20 | Capstone | Production Engineering Academy

---

## Anti-Pattern 1: The "Check-the-Box" Bureaucratic PRR

### The Mistake
Treating the Production Readiness Review as an administrative checklist completed 2 hours before launch by marking every item "Yes" without executing real load tests or chaos failure drills.

### Why It Fails
- Untested failure modes remain completely latent.
- When an incident strikes in production, the "verified" runbooks turn out to contain broken commands, obsolete links, or un-permissioned scripts.

### The Correct Production Fix
Require working evidence for every gate: attach Grafana dashboard URLs, load test percentile output files, Chaos Game Day report links, and verified runbook commands.

---

## Anti-Pattern 2: Alerting Without Runbooks (The Naked Alert)

### The Mistake
Creating 50 Prometheus alerting rules with no linked documentation or remediation procedures.

### Why It Fails
When an alert pages an on-call engineer at 3:00 AM, the engineer has no context on:
- What does the alert mean?
- What are the customer consequences?
- What is the step-by-step diagnostic procedure?
- How to mitigate the alert within 15 minutes?
Result: Engineers freeze, MTTR explodes, and mitigation is delayed.

### The Correct Production Fix
**Every alert must contain a `runbook_url` annotation** pointing directly to a tested, step-by-step triage guide in Git.
