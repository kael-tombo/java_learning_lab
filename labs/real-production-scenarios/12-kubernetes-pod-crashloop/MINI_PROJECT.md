# Lab 12 — Mini Project: Reproduce + Detect + Fix CrashLoop

## Objective
Deploy a crashing pod on kind/minikube, diagnose with kubectl, and harden it — ~60 minutes.

## Part 1 — Reproduce (20 min)
1. Bad-env Deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: crash-demo}
spec:
  replicas: 2
  selector: {matchLabels: {app: crash-demo}}
  template:
    metadata: {labels: {app: crash-demo}}
    spec:
      containers:
      - name: app
        image: eclipse-temurin:17-jre
        command: ["sh","-c","echo missing DB_URL; exit 1"]
```
2. `kubectl apply -f bad.yaml && kubectl get pods -w` — observe CrashLoopBackOff.
3. Capture `describe` Last State + `logs --previous` + `events` into `evidence.txt`.

## Part 2 — Detect (20 min)
1. Write `triage.sh`: takes pod name, dumps describe + previous logs + events to a file.
2. Simulate metrics: record restart counts at 0/5/10 min; plot rate.
3. Write the PromQL alert and explain firing threshold.
4. Break probes: set liveness `initialDelaySeconds: 1` on a sleep-60 starter; show premature kills.

## Part 3 — Fix (20 min)
1. Fix image to a healthy server + add startup/readiness/liveness probes + limits.
2. Pin image to digest: `docker pull <img> && docker inspect --format='{{index .RepoDigests 0}}'`.
3. RollingUpdate with `maxUnavailable: 1`; verify zero-downtime `kubectl rollout status`.
4. Rollback drill: push bad image again, `kubectl rollout undo`, time it (<5 min goal).

## Deliverables
- `evidence.txt`, `triage.sh`, fixed Deployment YAML, rollback timing log, 1-page runbook.
- Success: crash diagnosed from evidence alone; hardened deploy survives restart test.

## Grading
- Reproduce (30%), Detect/triage script (35%), Fix + rollback (35%).
