# Lab 12 — Kubernetes Pod CrashLoopBackOff — Theory: Mechanics + Detection

## 1. What CrashLoopBackOff Means
- Kubelet starts container → container exits non-zero → backoff delay (10s, 20s, 40s … capped 5 min) → retry. `kubectl get pods` shows `CrashLoopBackOff`.
- Distinct from `ImagePullBackOff` (registry) and `Error` (single failure): CrashLoop = repeated crashes.
- `restartPolicy: Always` (Deployments) retries forever; `Never`/`OnFailure` (Jobs) behave differently.

## 2. Common Mechanics
- App exits on boot: missing env/secret, bad config, failed migration, port already bound.
- Liveness probe kills healthy-but-slow starter (probe too aggressive).
- OOMKilled (exit 137): limit < working set; check `kubectl describe` Last State.
- Panic in init: `NullPointerException` in Spring `@PostConstruct`, missing DB.
- Bad image tag (`latest` moved), architecture mismatch (arm64 vs amd64 → exec format error).

## 3. Detection Layers
| Layer | Signal |
|-------|--------|
| Pod state | `kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"}==1` |
| Restarts | `increase(kube_pod_container_status_restarts_total[15m]) > 3` |
| Events | `Failed`, `BackOff`, `Unhealthy` in `kubectl get events` |
| Logs | Previous container logs (`--previous`) show stack trace |
| Traces | Crash right after deploy → correlate with rollout revision |

## 4. Triage Order
1. `kubectl describe pod` → Last State (exit code, reason) + Events.
2. `kubectl logs --previous` → actual exception.
3. `kubectl get events --sort-by=.lastTimestamp` → probe vs OOM vs config.
4. Diff last deploy: `kubectl rollout history deploy/X`.

## 5. Exit Codes Cheat
- 1: app error; 2: misuse; 126/127: permission/command not found; 137: OOMKilled; 139: segfault; 143: SIGTERM (probe/scale-down race).

## 6. Prevention
- Readiness vs liveness separation; `initialDelaySeconds` / `startupProbe` for slow JVMs.
- Validate config at CI (schema check), required-env check with clear error.
- Resource requests/limits from load test; VPA recommendations.
- Canary + auto-rollback on crash-rate SLO.

## 7. Key Takeaway
Describe tells you *how it died* (exit code/events); previous logs tell you *why*. Always fetch both before restarting blindly.
