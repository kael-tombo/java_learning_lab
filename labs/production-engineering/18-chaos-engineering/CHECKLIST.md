# CHECKLIST: Chaos Experiment Readiness & Safety
## Lab 18 | Production Engineering Academy

---

## 1. Experiment Safety & Blast Radius Gates
- [ ] Steady state metrics defined with quantifiable Prometheus queries.
- [ ] Hypothesis written and reviewed with service owners.
- [ ] Blast radius strictly constrained (max 5% traffic or Canary pods only).
- [ ] Experiment scheduled during normal business hours with team on standby.
- [ ] Self-terminating dead-man's switch timeout configured ($\le 10\text{m}$).

## 2. Emergency Abort Controls
- [ ] Automated Prometheus alert wired to abort experiment if error budget burns $> 2\times$.
- [ ] Manual "Big Red Button" abort command verified and ready in terminal.
- [ ] Verified that abort script functions even if application network is degraded.

## 3. Post-Experiment Analysis
- [ ] Steady state maintained throughout experiment?
- [ ] Circuit breakers tripped as designed?
- [ ] Latency percentiles returned to baseline within 60s of experiment conclusion?
