# RUNBOOK: Production Readiness Review Execution & Audit
## Lab 20 | Capstone | Production Engineering Academy

---

## RUNBOOK 01: Conducting a Production Readiness Review (PRR)

### Phase 1: Intake & Self-Assessment (T-4 Weeks to Launch)
1. Service team clones the PRR Scorecard (`CHECKLIST.md`).
2. Complete automated PRR linter check on deployment manifests:
   ```bash
   ./scripts/prr-lint.sh k8s/production/deployment.yaml
   ```
3. Attach architecture diagrams, data flow maps, and load test reports.

### Phase 2: SRE & Architecture Audit (T-2 Weeks to Launch)
1. Schedule a 60-minute PRR review session with SRE and Security leads.
2. Review the 8 Pillars:
   - Check circuit breakers and timeouts.
   - Verify alerting rules and PagerDuty escalations.
   - Audit runbook coverage: Does every alert have a step-by-step diagnostic runbook?
3. Outcome:
   - **GO**: All gates pass. Proceed to staged Canary launch.
   - **CONDITIONAL GO**: Non-critical action items must be completed within 14 days.
   - **NO-GO**: Critical architectural, security, or observability gaps identified. Launch postponed.

---

## RUNBOOK 02: Production Launch Day Protocol
1. **Freeze Window Verification**: Confirm no concurrent deployments or cluster maintenance.
2. **Pre-Flight Traffic Drain Verification**: Verify Canary routing is functioning at 1%.
3. **SRE Observer on Deck**: Designated SRE monitors Prometheus error budget burn rate and latency histograms during step promotions.
