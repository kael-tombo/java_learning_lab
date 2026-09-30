# ARCHITECTURE DECISIONS: Enterprise Release Engineering Standards
## Lab 13 | Production Engineering Academy

---

## ADR-01: Progressive Delivery & Automated Canary Deployment Standard

### Status: ACCEPTED

### Context
Manual release verifications took 2 hours per deployment and failed to catch subtle tail-latency regressions and memory leaks prior to 100% rollout.

### Decisions
1. **Argo Rollouts Standard**:
   - All customer-facing microservices must deploy using Argo Rollouts with automated metric analysis.
   - Traffic weighting: 5% (10m) -> 20% (15m) -> 50% (10m) -> 100%.
2. **Automated Rollback Thresholds**:
   - Automated abort triggers if HTTP 5xx error rate exceeds 0.5% or p99 latency increases by $> 25\%$ compared to baseline.
3. **Database Migration Separation**:
   - Migrations decoupled from container startup; executed via ArgoCD PreSync Jobs.
   - Breaking migrations strictly prohibited; mandatory expand-contract pattern.

### Consequences
- MTTR for bad deployments reduced from 45 minutes to $< 90$ seconds.
- Fully automated canary evaluation removes human verification bottlenecks.
