# THEORY — Lab 06: Production Deployment Rollback

## 1. Mechanics: How Rolling Deployments Fail
- Rolling update replaces pods incrementally (`maxSurge 25%`, `maxUnavailable 25%`).
- New ReplicaSet scales up while old scales down; bad pods pass readiness if probe is shallow.
- NPE in `UserPreferenceCache` path: only hit when preference missing + L2 miss + concurrent refresh.
- Connection draining misconfigured (`terminationGracePeriodSeconds` too short) stalls rollback.
- Without feature flag, entire binary must roll back; no surgical kill-switch.

## 2. Deployment Strategies Compared
| Strategy | Rollback speed | Risk | Cost |
|---|---|---|---|
| Rolling | minutes | medium | low |
| Blue-green | seconds (LB flip) | low | 2x capacity |
| Canary 1-5-25-50-100% | minutes | lowest | analysis infra |
| Recreate | minutes + downtime | high | low |

## 3. Canary Analysis Mechanics
- Compare canary vs baseline on error rate, p95 latency, throughput, saturation.
- Naive mean comparison misses variance; use t-test / Mann-Whitney + minimum sample (≥500 req).
- Canary too short (15 min) misses peak-traffic edge cases and cold-cache races.
- Require statistical significance (p<0.05) + effect size before promotion.

## 4. Feature Flags as Safety Valve
- Wrap risky paths: `if (flags.enabled("pref-cache-v2", user)) { newPath(); } else { oldPath(); }`.
- Kill-switch: disable flag in <30s via LaunchDarkly / App Config, no redeploy.
- Targeted rollout: internal → 1% → 10% → 100% with metric gates.
- Flag hygiene: expire stale flags, default-off for risky paths.

## 5. Detection: Signals and Thresholds
- Golden signals: error rate (>1% for 2 min), p95 latency delta (+50%), 5xx per pod, crashloop count.
- Deployment markers in dashboards correlate version change with metric shift.
- Alerts: `sum(rate(http_5xx[2m])) / sum(rate(http_total[2m])) > 0.01` pages SRE.
- Readiness/liveness probes must exercise real dependency (deep health check).
- Audit: `kubectl rollout history`, `kubectl get events`, Azure Monitor deployment annotations.

## 6. Automated Rollback Triggers
- Pipeline watches metrics for N minutes post-step; breach → `kubectl rollout undo`.
- Conditions: error-rate breach, SLO burn-rate >14x, probe failure rate, manual IC override.
- Test rollback monthly; untested rollback is not a control.
- Freeze deploys when error budget <10% remaining.

## 7. Connection Draining and Pod Lifecycle
- `preStop` sleep + SIGTERM + `terminationGracePeriodSeconds: 60` lets in-flight finish.
- Misconfigured drain keeps bad pods in endpoints → prolonged 500s.
- Verify: `kubectl get endpoints`, check Front Door backend health.
- Fix: PodDisruptionBudgets + correct readiness gates.

## 8. Common Misconceptions
- "CI green = safe" — integration tests rarely cover prod concurrency/load.
- "Canary 15 min is enough" — need traffic mix + peak coverage.
- "Rollback is free" — DB migrations may be irreversible; need expand-migrate-contract.
- "Manual approval is safer" — slows MTTR; automate guardrails instead.

## 9. Detection Checklist (First 5 Minutes)
1. Confirm deploy correlation (version, time, scope).
2. Check error rate + affected nodes/regions.
3. Inspect pod logs for exception signature.
4. Decide: flag-off vs rollback (prefer fastest blast-radius cut).
5. Page IC + feature owner; open bridge.

## 10. Key Takeaways
- 70% of incidents are change-induced; design deploys for fast reversal.
- Rule: rollback first, investigate second.
- Every risky path behind a flag; every deploy behind automated guardrails.
