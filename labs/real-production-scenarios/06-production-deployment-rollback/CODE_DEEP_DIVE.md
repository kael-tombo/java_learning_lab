# CODE DEEP DIVE — Lab 06: Rollback Runbook Commands

## 1. Correlate Deploy with Errors
```bash
kubectl rollout history deployment/user-profile -n prod
kubectl get replicasets -n prod --sort-by=.metadata.creationTimestamp
kubectl get events -n prod --sort-by=.lastTimestamp | tail -30
```

## 2. Inspect Bad Pods + Logs
```bash
kubectl get pods -n prod -l app=user-profile | grep -v Running
kubectl describe pod user-profile-7d9c4-xxxxx -n prod | tail -40
kubectl logs -n prod -l app=user-profile --tail=200 | grep -A5 NullPointerException
kubectl logs -n prod deployment/user-profile --previous --tail=100
# log snippet:
# java.lang.NullPointerException: Cannot invoke "Preferences.getTheme()" because "prefs" is null
#   at UserPreferenceCache.resolve(UserPreferenceCache.java:87)
```

## 3. Null-Guard Fix (Java)
```java
Preferences prefs = client.getPreferences(userId);
if (prefs == null) {
  metrics.counter("pref.fallback.null").increment();
  log.warn("pref null, user={}", userId);
  prefs = Preferences.defaults();
}
return prefs;
```

## 4. Feature-Flag Kill-Switch
```java
if (flags.enabled("pref-cache-v2", userId)) { return newCachePath(userId); }
return legacyPath(userId);
```
```bash
# LaunchDarkly CLI / API pseudo:
ldcli flag update pref-cache-v2 --off
curl -s http://localhost:8080/actuator/health/prefCache | jq .
```

## 5. Rollback Commands
```bash
kubectl rollout undo deployment/user-profile -n prod
kubectl rollout status deployment/user-profile -n prod --timeout=300s
kubectl get endpoints user-profile -n prod -w
```

## 6. Drain Verification
```yaml
lifecycle:
  preStop:
    exec: { command: ["sleep","20"] }
terminationGracePeriodSeconds: 60
readinessProbe:
  httpGet: { path: /actuator/health/readiness, port: 8080 }
  periodSeconds: 5
```
```bash
curl -s http://pod-ip:8080/actuator/health/readiness; echo
```

## 7. Error-Rate Alert (Prometheus)
```promql
sum(rate(http_server_requests_seconds_count{status=~"5.."}[2m]))
/ sum(rate(http_server_requests_seconds_count[2m])) > 0.01
```

## 8. Azure Monitor / Front Door Checks
```bash
az monitor metrics list --resource <aks-id> --metric requests_failed --interval PT1M
az network front-door backend-pool show --help | head -20
curl -s -o /dev/null -w "%{http_code} %{time_total}\n" https://api.example.com/profile/me
```

## 9. Anti-Patterns
- Shallow `/healthz` returning 200 always → bad pods stay in rotation.
- `kubectl delete pod --force` during drain → dropped in-flight, client 502.
- Rolling back DB-migrated schema without expand-contract → startup crash loop.
