# Lab 12 — Real-World Project: CrashLoop War Room

## Incident Timeline (Bad Deploy)
| Time | Event |
|------|-------|
| T+0 | Deploy v2.4.0 to prod (image `api:latest` moved) |
| T+1m | Restart alert: `increase(restarts[15m]) > 3` on 8/10 pods |
| T+3m | On-call: describe → Exit 1, logs --previous → `Missing required env: PAYMENTS_URL` (new required var, Helm values not updated) |
| T+5m | SEV-2 declared; rollout paused (`kubectl rollout pause`) |
| T+7m | Decision: rollback (faster than forward-fix) → `kubectl rollout undo` |
| T+10m | Restarts flat, readiness green, error rate normal |
| T+25m | Status resolved; forward-fix PR: default + CI required-env check |
| T+2d | Post-mortem; policy gate added |

## War-Room Runbook
1. **Scope**: one pod (node/app) vs all pods (deploy)? `kubectl get pods` + rollout time.
2. **Evidence**: describe + logs --previous + events (paste all three in incident channel).
3. **Stop bleed**: `rollout pause` then `rollout undo` for fleet-wide; cordon node for single-node.
4. **Verify**: `rollout status`, restart rate flat 10 min, p99 latency normal.
5. **Communicate**: 10-min status page, 15-min updates, resolve with duration + impact.
6. **Follow-up**: pin digest, add probe/limit policy, CI env check.

## Metrics That Matter
- TTD: restart alert <3 min. TTM: rollback <5 min.
- SLI: crash-free pods %; SLO 99.9% over 30d.
- Deploy health: % rollouts with zero crashloops in 15 min.
- MTTR trend per service; top-restart table weekly.

## Prevention Backlog
- [ ] Deny `latest`, require digest + probes + limits (Kyverno).
- [ ] startupProbe for all JVM services.
- [ ] Canary + auto-rollback on restart-rate SLO.
- [ ] CI check for required env/ConfigMap keys.
- [ ] Runbook dashboard: describe + prev-logs + revision in one view.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes pod lifecycle, probes, and kubectl reference: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- kubectl describe / logs / events triage: https://kubernetes.io/docs/reference/kubectl/
- Java container memory/limits guidance (general): https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
