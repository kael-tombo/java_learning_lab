# ARCHITECTURE DECISIONS: Production Readiness Review Policy
## Lab 20 | Capstone | Production Engineering Academy

---

## ADR-01: Mandatory Production Readiness Review (PRR) Gate Policy

### Status: ACCEPTED

### Context
Unstandardized operational practices and skipped readiness verifications resulted in 14 major customer outages in 2025 during the launch of newly deployed microservices.

### Decisions
1. **Mandatory PRR for All Tier-0 and Tier-1 Services**:
   - No new microservice may receive live customer traffic without passing a formal PRR conducted by SRE and Architecture leads.
2. **Automated CI PRR Linter**:
   - Automated manifests linter must pass in the CI pipeline (verifying non-root execution, probes, preStop hooks, resource requests, and dump volume mounts).
3. **Runbook Linking Rule**:
   - Prometheus alerting rules without a valid `runbook_url` pointing to an approved markdown runbook will be rejected by CI.
4. **Waiver Policy**:
   - Skipping a PRR requires written sign-off from the Vice President of Engineering and Chief Technology Officer, accepting explicit financial risk.

### Consequences
- Post-launch Sev-1 incidents reduced by 85%.
- Establishes a uniform engineering quality bar across all teams.
