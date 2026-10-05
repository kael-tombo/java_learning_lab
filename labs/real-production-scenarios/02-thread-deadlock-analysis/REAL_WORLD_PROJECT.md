# REAL_WORLD_PROJECT — War Room: Checkout Hangs, CPU Idle

## 1. Scenario
Payments service (Java 17, Tomcat 200 threads) p99 hits 30s timeouts at peak. CPU 25%, no OOM, DB healthy. On-call suspects "slow downstream" but downstream p99 is fine. You take the war room.

## 2. Timeline
| T | Event |
|---|---|
| T+0 | Page: p99 breach + Tomcat queue exploding, CPU flat |
| T+5m | Rule out downstream: trace shows threads parked in app code, not I/O |
| T+8m | Capture dump #1: `jstack -l` shows 40 BLOCKED on `InventoryLock`, cycle hint |
| T+12m | Dumps #2/#3 confirm identical stacks → stuck, not slow |
| T+15m | Mitigate: drain stuck pod from LB, restart it; p99 partially recovers |
| T+30m | Cycle mapped: `OrderService` L1→L2 vs `RefundService` L2→L1 on same SKU locks |
| T+60m | Hotfix: global SKU-id ordering + `tryLock(2s)` fallback; canary + soak |
| T+90m | Rollout, pool busy drops 95%→40%, p99 back to 250ms |
| T+24h | Postmortem + lock-order doc + inversion test in CI |

## 3. Runbook
```bash
PID=$(pgrep -f payments | head -1)
for i in 1 2 3; do jstack -l $PID > /tmp/pay-$i.txt; sleep 30; done
grep -B2 -A8 "deadlock\|waiting to lock" /tmp/pay-1.txt | head -60
jcmd $PID Thread.print | grep -c BLOCKED
curl -s localhost:8080/actuator/metrics/tomcat.threads.busy
curl -s localhost:8080/actuator/metrics/tomcat.threads.config.max
kubectl cordon <stuck-node> && kubectl delete pod <stuck-pod>  # mitigation
```

## 4. Metrics
- `jvm_threads_states{state="BLOCKED"}` count + `jvm_threads_deadlocked`.
- Tomcat busy vs max, accept-queue depth, p99/p999, throughput per pod.
- Success: BLOCKED→baseline, queue drains, p99 < SLO for 1h.

## 5. Log Snippets
```
Found one Java-level deadlock:
"order-44": waiting to lock monitor 0xSkuLock-B held by "refund-9"
"refund-9": waiting to lock monitor 0xSkuLock-A held by "order-44"
[tomcat] threads.busy=198/200 queue=1500 cpu=25%  # flat CPU + full pool
```

## 6. Prevention
Lock-order registry, ban nested sync without review, `tryLock` timeouts on cross-service locks, inversion soak test, auto-dump on pool>90% 5m, isolated health-check executor.

## 7. Postmortem Outline
Impact (failed checkouts), detection gap (no BLOCKED alert), root cause (inconsistent SKU lock order from two PRs), fix, 5 Whys, owners/dates.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle `jstack` / troubleshooting hanging processes: https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/tooldescr006.html
- OpenJDK `jcmd` Thread.print reference: https://openjdk.org/groups/hotspot/docs/Serviceability.html
- Kubernetes liveness/readiness probe separation (avoid stuck-pool health lies): https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
