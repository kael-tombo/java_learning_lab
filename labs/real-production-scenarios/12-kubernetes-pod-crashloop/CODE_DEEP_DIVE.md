# Lab 12 — Code Deep Dive: kubectl CrashLoop Runbook

## 1. 2-Minute Triage Bundle
```bash
NS=prod; POD=$(kubectl get pods -n $NS --sort-by=.metadata.creationTimestamp | grep -i crash | head -1 | awk '{print $1}'); echo "POD=$POD"
kubectl get pod $POD -n $NS -o wide
kubectl describe pod $POD -n $NS | tail -80
kubectl logs $POD -n $NS --previous --tail=150
kubectl get events -n $NS --sort-by=.lastTimestamp | tail -30
```

## 2. Log Snippets (Diagnose by Reading)
```
# Missing env
Exception in thread "main" java.lang.IllegalStateException: Missing required env: DB_URL
  at com.example.App.main(App.java:42)
# OOMKilled (describe shows it; logs just stop)
# describe: Last State: Terminated, Reason: OOMKilled, Exit Code: 137
# Liveness killing slow starter
Warning Unhealthy Liveness probe failed: HTTP probe failed with statuscode: 500
Warning Unhealthy Readiness probe failed: connection refused
Normal Killing Container failed liveness probe, will be restarted
# Bad image
Failed Failed to pull image "api:latest": rpc error: code = NotFound
Warning BackOff Back-off pulling image "api:latest"
# Exec format (arch mismatch)
standard_init_linux.go:228: exec user process caused: exec format error
```

## 3. Correlate With Deploy
```bash
kubectl rollout history deploy/api -n prod
kubectl rollout history deploy/api -n prod --revision=42 | head -40
kubectl get deploy api -n prod -o yaml | grep -B2 -A10 "livenessProbe\|readinessProbe\|startupProbe\|resources:"
kubectl diff -n prod  # if using kustomize/helm dry-run
# Fast mitigation
kubectl rollout undo deploy/api -n prod
kubectl rollout status deploy/api -n prod --timeout=180s
```

## 4. Probe + Resource Fix (Spring Boot Example)
```yaml
startupProbe:
  httpGet: {path: /actuator/health, port: 8080}
  failureThreshold: 30
  periodSeconds: 10
livenessProbe:
  httpGet: {path: /actuator/health/liveness, port: 8080}
  periodSeconds: 20
readinessProbe:
  httpGet: {path: /actuator/health/readiness, port: 8080}
  periodSeconds: 5
resources:
  requests: {memory: "1Gi", cpu: "500m"}
  limits: {memory: "1.6Gi", cpu: "2000m"}
```

## 5. Alerts
```promql
increase(kube_pod_container_status_restarts_total[15m]) > 3
kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"} == 1
```

Order: describe → logs --previous → events → rollout history → undo/fix → verify restarts flat.
