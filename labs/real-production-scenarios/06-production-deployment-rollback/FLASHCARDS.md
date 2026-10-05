# FLASHCARDS — Lab 06: Production Deployment Rollback

| Front | Back |
|---|---|
| Rolling update | Incremental pod replacement; controlled by maxSurge/maxUnavailable |
| maxUnavailable 25% | Up to 25% pods may be down during rollout |
| Canary | Small traffic % to new version with metric comparison |
| Promotion criteria | Stat-significant error/latency check + min requests + duration |
| t-test in canary | Tests whether error-rate difference is significant, not noise |
| Feature flag | Runtime toggle gating risky path without redeploy |
| Kill-switch | Flag that instantly disables feature everywhere |
| Automated rollback | Pipeline reverts on metric breach (e.g., err>1% 2 min) |
| `kubectl rollout history` | Lists ReplicaSet revisions for a deployment |
| `kubectl rollout undo` | Reverts to previous revision |
| `kubectl get events --sort-by` | Time-ordered cluster events for correlation |
| Readiness probe | Gates pod entry into endpoints; must be deep |
| Liveness probe | Restarts stuck container; keep shallow to avoid cascade |
| Connection draining | Lets in-flight requests finish before pod removal |
| terminationGracePeriodSeconds | Max wait for graceful shutdown before SIGKILL |
| preStop hook | e.g., sleep to allow LB deregistration before SIGTERM |
| Deployment marker | Version-change annotation on dashboards |
| Golden signals | Latency, traffic, errors, saturation |
| Error rate PromQL | sum(rate(http_5xx[2m]))/sum(rate(http_total[2m])) |
| SLO 99.95% budget | 21.6 min/month |
| Error budget | 1 − SLO; spend governs deploy velocity |
| Burn rate | How fast budget is consumed vs sustainable rate |
| MTTD / MTTR | Mean time to detect / recover |
| Blue-green | Two envs; LB flips traffic; instant rollback |
| Progressive exposure | 1→5→25→50→100% traffic steps |
| Expand-migrate-contract | Safe DB change pattern compatible with rollback |
| Blameless post-mortem | Systemic fixes, no individual blame |
| 5 Whys | Drill from symptom to systemic root cause |
| IC role | Coordinates response, comms, decisions |
| SEV1/P0 | Critical customer-facing outage, all hands |
| PodDisruptionBudget | Limits voluntary disruptions during rollout |
| maxSurge | Extra pods allowed above desired during rollout |
| CrashLoopBackOff | Repeated container crash; check `logs --previous` |
| `logs --previous` | Shows logs of crashed container instance |
| Image tag correlation | Match failing revision tag to error onset time |
| Azure Front Door | Geo-routing LB in front of AKS regions |
| AKS | Azure Kubernetes Service |
| LaunchDarkly | Feature-flag platform |
| App Config | Azure feature-flag/config store alternative |
| Freeze rule | Stop deploys when budget <10% remaining |
| Rollback SLA | Target e.g., <5 min decision-to-recovery |
| Scribe | Real-time timeline recorder in incident |
| Ops lead | Executes technical mitigation |
| Comms lead | Internal/external status updates |
| Stale flag | Old toggle left on; hygiene: expire/remove |
| Default-off | Risky flags start disabled |
| Targeted rollout | Internal→1%→10%→100% flag exposure |
| Deep health check | Health endpoint exercising downstream dependency |
| Shallow probe risk | Bad pod marked ready, serves 500s |
| `kubectl describe pod` | Probe failures, events, restarts for one pod |
| `kubectl get endpoints` | Which pods currently receive traffic |
| Revert vs rollforward | Revert restores fast; rollforward risks new bug |
| Revenue math | Downtime min × $/hour = direct loss |
| Churn cost | Long-term trust loss beyond direct revenue |
| Action item | Fix with owner + due date from post-mortem |
| Tabletop exercise | Simulated incident drill without prod impact |
| Chaos drill | Planned failure injection to test rollback |
| Deploy freeze notice | Comms halting releases until budget recovers |
| Statistical significance | p<0.05 guard against noisy canary promotion |
| Minimum sample | e.g., ≥2000 req before canary decision |
