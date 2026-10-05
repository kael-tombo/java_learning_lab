# REAL_WORLD_PROJECT — War Room: Search Pods Pegged at 100% After Deploy

## 1. Scenario
Search service (Java 17, 12 pods, 2 vCPU limit) p99 200ms→4s right after deploy v2.14. CPU alerts fire on all pods. Rollback is debated — but cause is unknown. You lead.

## 2. Timeline
| T | Event |
|---|---|
| T+0 | Page: CPU >95% all pods + p99 breach, correlated with v2.14 |
| T+5m | Confirm app-caused: `top -H` shows one thread/pod at 90%, not evenly spread |
| T+8m | 60s async-profiler CPU flame → `Pattern$Curly.match` via `SearchFilter.matches:88` |
| T+12m | Diff v2.13→v2.14: new "fuzzy" regex `(.*a+)+b` without input cap |
| T+15m | Mitigate: pin traffic to v2.13 pods (canary rollback), raise replica buffer |
| T+30m | Hotfix: possessive quantifier + 200-char input cap + ReDoS unit test |
| T+60m | Canary hotfix, flame flat, p99 220ms, full rollout |
| T+24h | Postmortem + ReDoS lint + profiling gate in CI |

## 3. Runbook
```bash
POD=$(kubectl get pod -l app=search -o jsonpath='{.items[0].metadata.name}')
PID=$(kubectl exec $POD -- pgrep -f java | head -1)
kubectl exec $POD -- top -H -b -n1 -p $PID | head -20
kubectl exec $POD -- jstack -l $PID > /tmp/search-tdump.txt; grep -A15 RUNNABLE /tmp/search-tdump.txt | head -40
kubectl exec $POD -- /opt/profiler/profiler.sh -e cpu -d 60 -f /tmp/cpu.html $PID
kubectl cp $POD:/tmp/cpu.html ./cpu-$(date +%s).html
kubectl rollout undo deploy/search  # if flame inconclusive in 15m, rollback first
```

## 4. Metrics
- Container CPU vs limit, throttle ratio, per-thread CPU, GC CPU fraction (rule out thrash).
- Flame top-frame share, p99/p999, error rate, queue depth.
- Success: top-frame share <5%, CPU <60% limit, p99 < SLO 1h.

## 5. Log Snippets
```
"http-nio-12" nid=0x4a2f runnable
  at java.util.regex.Pattern$Curly.match(Pattern.java:4237)
  at com.shop.SearchFilter.matches(SearchFilter.java:88)
[deploy] v2.14 14:02 "fuzzy search regex" merged (#4821)
```

## 6. Prevention
ReDoS-safe regex review + `safe-regex` lint, input length caps, continuous profiling with deploy-diff flames, load test with adversarial inputs, auto-rollback on CPU+p99 joint alert.

## 7. Postmortem Outline
Impact (search degraded 45m), detection win (flame in 8m), root cause (catastrophic backtracking), fix, 5 Whys (why no regex gate?), actions/owners.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- async-profiler usage (cpu/wall/lock modes): https://github.com/async-profiler/async-profiler
- OpenJDK JFR profiling + Mission Control: https://openjdk.org/projects/jmc/
- Kubernetes CPU sizing / throttling debug: https://kubernetes.io/docs/tasks/configure-pod-container/assign-cpu-resource/
