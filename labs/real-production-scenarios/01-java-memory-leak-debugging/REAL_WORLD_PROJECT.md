# REAL_WORLD_PROJECT — War Room: Slow-Burn Memory Leak Before Black Friday

## 1. Scenario
Checkout service (Java 17, G1, 8 pods × 1Gi heap in 1.5Gi containers) shows p99 climbing 300ms→1.2s over 3 days. Two pods OOMKilled overnight. Traffic is normal. Deploy 3 days ago added an in-memory promo-code cache. You lead the war room.

## 2. Timeline (compressed drill)
| T | Event |
|---|---|
| T+0 | Page: 2 OOMKills + `OutOfMemoryError: Java heap space` in logs |
| T+5m | Confirm scope: all pods Old Gen rising; oldest pods worst → leak, not spike |
| T+10m | Capture: `GC.heap_info`, `jmap -histo`, one live heap dump to object storage |
| T+15m | Mitigate: rolling restart, scale 8→12 pods, raise heap 1Gi→1.2Gi temporarily |
| T+30m | MAT: dominator = `PromoCode` retained by static `HashMap` in `PromoCache` |
| T+60m | Hotfix: bound cache (Caffeine 20k + 1h TTL) + canary 1 pod, verify flat Old Gen |
| T+90m | Full rollout, watch GC time <2%, p99 recovered |
| T+24h | Postmortem + backlog: cache-size metric, slope alert, soak test |

## 3. Runbook (copy-paste)
```bash
kubectl get pods -l app=checkout --sort-by=.status.startTime
kubectl logs -l app=checkout --tail=200 | grep -i "OutOfMemory\|GC overhead"
POD=$(kubectl get pod -l app=checkout -o jsonpath='{.items[0].metadata.name}')
PID=$(kubectl exec $POD -- pgrep -f java | head -1)
kubectl exec $POD -- jcmd $PID GC.heap_info
kubectl exec $POD -- jmap -histo:live $PID | head -30
kubectl exec $POD -- jmap -dump:live,format=b,file=/tmp/heap.hprof $PID
kubectl cp $POD:/tmp/heap.hprof ./heap-$(date +%s).hprof
kubectl rollout restart deploy/checkout  # mitigation
```

## 4. Metrics to Watch
- `jvm_memory_used_bytes{area="heap"}` per pod + after-Full-GC trend (slope `b`).
- `increase(jvm_gc_pause_seconds_sum[15m])/900` (GC fraction), Full GC count.
- Pod restarts, OOMKilled events, p99 latency, readiness failures.
- Success: Old Gen flat across 2× previous T_oom window, GC fraction <3%.

## 5. Log Snippets (drill seeds)
```
java.lang.OutOfMemoryError: Java heap space
 at com.shop.PromoCache.put(PromoCache.java:57)
[gc] GC(1234) Pause Full 2345ms, Heap: 1020M->1018M(1024M)  # no reclaim = leak
```

## 6. Prevention Backlog
Bounded caches by default (max size + TTL + size metric), heap-slope alerts with T_oom estimate, auto-dump flags on all JVMs, weekly soak test failing on Old Gen growth, PR checklist for static collections.

## 7. Postmortem Outline
Impact (orders delayed, restarts), detection gap (no slope alert), root cause (unbounded static map), fix, 5 Whys, action items with owners/dates.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle Troubleshoot Memory Leaks (heap dump / MAT guidance): https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/memleaks001.html
- OpenJDK HotSpot GC tuning + G1 GC guide: https://openjdk.org/groups/hotspot/docs/RuntimeOverview.html
- Kubernetes OOMKilled / memory limits debugging: https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/

> Drill tip: run this with heap dumps from the MINI_PROJECT. The war room is won by whoever captures evidence before restarting.
