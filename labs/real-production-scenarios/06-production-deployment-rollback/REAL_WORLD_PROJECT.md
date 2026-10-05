# REAL WORLD PROJECT — Lab 06: War-Room Rollback Runbook

## 1. War-Room Timeline (47-min SEV1)
| T | Event | Owner |
|---|---|---|
| T+0 | Deploy v2.4.1 to 100% (48 nodes, 3 regions) | Platform |
| T+3 | Error 1%→12%, 500s on 12 nodes; DLQ quiet | Monitor |
| T+6 | Bridge open, IC declared SEV1/P0 | SRE primary |
| T+9 | NPE signature found in pod logs | Feature team |
| T+14 | Decision: rollback (flag unavailable — no kill-switch) | IC |
| T+20 | Rollback started; drain stalls on 6 nodes | Ops |
| T+35 | Force-drain + endpoint fix; errors declining | Ops |
| T+47 | All nodes healthy, errors baseline | IC closes |

## 2. Triage Runbook (First 10 Minutes)
1. Confirm deploy correlation: `kubectl rollout history`, image tags, markers.
2. Scope: nodes/regions, error %, sessions impacted.
3. Logs: `kubectl logs -l app=... | grep NullPointer` + `describe pod`.
4. Decide fastest cut: flag-off (if exists) else `rollout undo`.
5. Page IC/feature owner; start scribe timeline.

## 3. Rollback + Verify Commands
```bash
kubectl rollout undo deployment/user-profile -n prod
kubectl rollout status deployment/user-profile -n prod --timeout=300s
kubectl get endpoints user-profile -n prod -w
curl -s -o /dev/null -w "%{http_code}\n" https://api.example.com/profile/me
```

## 4. Metrics That Prove Recovery
- Error rate back <0.1% for 10 min; p95 latency to baseline ±10%.
- Zero CrashLoopBackOff; endpoints show all desired pods.
- SLO burn back <2x; Front Door backend health 100%.

## 5. Comms Template
> SEV1 update: bad deploy v2.4.1 causing 12% 5xx. Rollback in progress, ETA 15 min. Next update :15. IC: <name>, bridge: <link>.

## 6. Prevention Backlog
- Mandatory flags for new paths + kill-switch drill monthly.
- Canary 30 min + min-request + stat test; auto-rollback on err>1%/2min.
- Fix drain (preStop + grace 60s); test rollback quarterly; budget-gated freezes.

## 7. Cost of This Outage (Template)
Direct $52k + churn $120–200k + eng $28k ≈ $200–280k. Budget 217% consumed.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes rolling update + `kubectl rollout undo` mechanics: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- Blue-green / progressive delivery concepts (Argo Rollouts): https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#updating-a-deployment
- GitHub Actions progressive deployment gates: https://docs.github.com/en/actions/deployment/about-deployments
