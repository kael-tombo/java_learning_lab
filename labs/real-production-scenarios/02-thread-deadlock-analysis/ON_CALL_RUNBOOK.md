# On-Call Runbook: Thread Deadlock Analysis (Lab 02)

> Scope: Java thread deadlocks, livelocks, and thread pool exhaustion in production services.
> Audience: on-call engineer responding to hung requests, thread pool saturation, or deadlock alerts.

## 1. Service Map & SLOs

| Component | SLO | Key Signal |
|---|---|---|
| Request latency (p99) | < 500 ms | HTTP latency histogram |
| Thread pool utilization | < 70% | `ThreadPoolExecutor` active/queue |
| Deadlock count | 0 | `ThreadMXBean.findDeadlockedThreads()` |
| Thread count | < 80% max | `jcmd Thread.print` count |

## 2. Triage Decision Tree (first 5 minutes)

```
alert: high latency / thread pool full / deadlock detected?
├─ Requests timing out, threads not CPU-bound → §3 Thread Pool Exhaustion
├─ Deadlock alert / "Found deadlock" in logs → §4 Confirmed Deadlock
├─ CPU 100%, threads RUNNABLE, no progress → §5 Livelock / Spin Lock
├─ Thread count growing unbounded → §6 Thread Leak
└─ DB pool exhausted, threads WAITING on getConnection → §7 Resource Deadlock
```

Always note: recent deploy, traffic pattern, thread pool config, lock usage in changed code.

## 3. Runbook: Thread Pool Exhaustion (Requests Queuing)

**Symptoms:** Latency spike, queue depth growing, thread pool at max, threads mostly `WAITING`/`BLOCKED`.

**Immediate Mitigation (0–5 min):**
```bash
# 1. Scale out (add capacity)
kubectl scale deployment/<service> --replicas=<current+3>

# 2. Increase pool size temporarily
kubectl set env deployment/<service> THREAD_POOL_MAX=100

# 3. If queue-based: reject new requests fast (fail-fast)
#    Set queue capacity lower or use CallerRunsPolicy
```

**Diagnose (5–15 min):**
1. **Thread dump:** `jcmd <pid> Thread.print > threads.txt`
2. **Categorize threads:**
   ```bash
   grep -c "BLOCKED" threads.txt
   grep -c "WAITING" threads.txt
   grep -c "TIMED_WAITING" threads.txt
   grep -c "RUNNABLE" threads.txt
   ```
3. **Top blockers:** `grep -A5 "BLOCKED" threads.txt | head -50`
4. **Common causes:**
   - Downstream service slow → threads `WAITING` on HTTP client
   - DB pool exhausted → `WAITING` on `HikariPool.getConnection()`
   - Lock contention → `BLOCKED` on same monitor
   - GC pause → `RUNNABLE` but actually in safepoint

**Fix Patterns:**
| Cause | Fix |
|---|---|
| Downstream slow | Add timeout + circuit breaker, bulkhead thread pool |
| DB pool exhausted | Fix connection leak, increase pool, optimize queries |
| Lock contention | Reduce lock scope, use striped locks, `StampedLock` |
| GC pause | Tune heap/GC, reduce allocation rate |

## 4. Runbook: Confirmed Deadlock

**Symptoms:** "Found one Java-level deadlock" in thread dump, threads stuck indefinitely.

**Immediate Mitigation (0–5 min):**
```bash
# 1. Capture thread dump FOR ROOT CAUSE
jcmd <pid> Thread.print > /tmp/deadlock-$(date +%Y%m%d-%H%M%S).txt

# 2. Restart affected pods (only way to unblock)
kubectl delete pod -l app=<service>  # Let K8s recreate

# 3. If only subset affected: kill specific threads (NOT recommended)
#    Use Arthas: `thread -b` to find blocked, `stop <thread-id>`
```

**Root Cause Analysis (post-incident):**
1. **Open thread dump:** Find "Found one Java-level deadlock" section
2. **Identify cycle:** Thread-1 → Lock-A → Thread-2 → Lock-B → Thread-1
3. **Map to code:** Stack traces show exact lines holding/waiting for locks
4. **Classify deadlock type:**
   - **Monitor (synchronized):** Detected by `findDeadlockedThreads()`
   - **ReentrantLock:** NOT detected — manual analysis required
   - **Distributed:** Across services — need distributed traces
3. **Apply fix:**
   - **Inconsistent lock ordering:** Enforce global order (by ID, hash, etc.)
   - **Callback with lock held:** Release lock before calling foreign code
   - **Multi-lock acquisition:** Use `tryLock(timeout)` with backoff
   - **ReentrantLock deadlock:** Same fixes, but use `tryLock` not `lock()`

**Verification:** Load test with concurrent conflicting operations, confirm no deadlock.

## 5. Runbook: Livelock / Spin Lock

**Symptoms:** CPU 100%, threads `RUNNABLE`, high throughput but no business progress.

**Diagnose:**
```bash
# 1. Confirm CPU usage
top -H -p <pid>  # Per-thread CPU

# 2. Thread dump — all RUNNABLE, similar stacks
jcmd <pid> Thread.print > threads.txt

# 3. Look for spin loops:
#    while (!cas(...)) { }
#    while (queue.isEmpty()) { }
#    for (;;) { tryLock(); }
```

**Common Causes & Fixes:**
| Pattern | Fix |
|---|---|
| CAS retry no backoff | Add exponential backoff + jitter |
| Busy-wait on queue | Use `BlockingQueue.take()` or `Condition.await()` |
| `tryLock()` loop no delay | `tryLock(timeout)` or `lock()` with ordering |
| Optimistic locking conflict | Reduce contention, batch updates, or accept retry |

**Fix Template (backoff):**
```java
long backoff = 1; // ms
while (!compareAndSet(key, oldVal, newVal)) {
    Thread.sleep(ThreadLocalRandom.current().nextLong(backoff));
    backoff = Math.min(backoff * 2, MAX_BACKOFF_MS);
}
```

## 6. Runbook: Thread Leak (Unbounded Thread Growth)

**Symptoms:** Thread count increases over time, `OutOfMemoryError: unable to create new native thread`.

**Diagnose:**
```bash
# Thread count trend
watch -n30 "jcmd <pid> Thread.print | grep -c 'java.lang.Thread'"

# Thread dump analysis
jcmd <pid> Thread.print > threads.txt
# Group by thread name prefix:
awk '/^"/ {name=$2} /java.lang.Thread.State/ {print name}' threads.txt | sort | uniq -c | sort -rn
```

**Common Leak Sources:**
| Thread Name Pattern | Likely Cause |
|---|---|
| `pool-*-thread-*` | Unshutdown `ExecutorService` |
| `HikariPool-*` | Connection pool not closed |
| `grpc-default-executor-*` | gRPC channel not shutdown |
| `netty-event-loop-*` | `EventLoopGroup` not shutdown |
| `Thread-*` (unnamed) | `new Thread()` without pool |

**Fix:** Implement `Closeable`/`AutoCloseable`, shutdown in `@PreDestroy`/JVM shutdown hook.

## 7. Runbook: Resource Deadlock (DB Pool / Connection Exhaustion)

**Symptoms:** Threads `WAITING` on `HikariPool.getConnection()`, pool exhausted, no DB errors.

**Diagnose:**
```bash
# Pool metrics
curl localhost:8080/actuator/metrics/hikaricp.connections.active
curl localhost:8080/actuator/metrics/hikaricp.connections.pending

# Thread dump: all threads at HikariPool.getConnection()
grep -A10 "HikariPool" threads.txt
```

**Root Causes:**
1. **Connection leak:** Code path doesn't return connection (exception path)
2. **Task needs N connections, pool size < N × concurrency** (Exercise 4 pattern)
3. **Long-running queries hold connections** → increase pool or optimize queries

**Fix:**
```java
// Enable leak detection
spring.datasource.hikari.leak-detection-threshold=30000

// Fix leak: always close in finally or use @Transactional
@Transactional
public void update() {
    // Single connection per transaction
}
```

## 8. Runbook: Distributed Deadlock (Cross-Service)

**Symptoms:** Multiple services show thread pool exhaustion, synchronous call cycle.

**Diagnose:**
1. **Distributed trace:** Look for cycle: Service-A → Service-B → Service-C → Service-A
2. **Each service:** Threads `WAITING` on HTTP client response
3. **Correlate:** Same trace ID across all services in cycle

**Immediate Mitigation:**
```bash
# 1. Break cycle: disable non-critical downstream call via feature flag
kubectl set env deployment/<service> FEATURE_INVENTORY_VALIDATION=false

# 2. Add timeouts + circuit breakers (if not present)
#    Deploy config: resilience4j.circuitbreaker.registerHealthIndicator=true
```

**Long-term Fix:**
- Make validation async (event-driven)
- Add `@CircuitBreaker` + `@Bulkhead` (Resilience4j) on all outbound calls
- Implement timeout budgets: total < 3s, per-hop < 1s

## 9. Post-Incident Checklist

- [ ] Thread dump captured and preserved (S3/GCS)
- [ ] Deadlock type classified: Monitor / ReentrantLock / Distributed / Resource / Livelock
- [ ] Root cause code location identified (class, method, line)
- [ ] Fix applied: lock ordering / tryLock / circuit breaker / async / pool sizing
- [ ] Load test validates: concurrent conflicting ops complete, no stuck threads
- [ ] Monitoring improved: alert on thread pool queue depth, deadlock detection
- [ ] Runbook updated if new pattern
- [ ] Post-mortem within 5 business days

## 10. Key Dashboards & Alerts

| Alert | Query (Prometheus) | Severity |
|---|---|---|
| Thread pool queue > 80% | `threadpool_queue_size / threadpool_queue_capacity > 0.8` | P1 |
| Deadlock detected | `jvm_threads_deadlocked > 0` | P1 |
| Thread count > 80% max | `jvm_threads_live / jvm_threads_max > 0.8` | P2 |
| Thread pool rejected tasks | `rate(threadpool_rejected_total[5m]) > 0` | P2 |
| CPU high, low throughput | `cpu_usage > 0.9 and rate(http_requests_total[5m]) < baseline*0.5` | P2 |

## 11. Useful Commands Quick Reference

```bash
# Thread dump with deadlock detection
jcmd <pid> Thread.print -deadlock > threads.txt

# jstack with locks
jstack -l <pid> > threads.txt

# Thread CPU (Linux)
top -H -p <pid>

# Find blocked threads (Arthas)
arthas: thread -b

# Thread stack (Arthas)
arthas: thread <thread-id>

# JFR for lock contention
jcmd <pid> JFR.start name=lock settings=profile duration=120s filename=/tmp/lock.jfr

# HikariCP metrics
curl -s localhost:8080/actuator/metrics/hikaricp.connections.active

# Kubernetes thread dump
kubectl exec <pod> -- jcmd <pid> Thread.print > threads.txt

# Preserve dump
kubectl cp <ns>/<pod>:/tmp/threads.txt ./threads-$(date +%Y%m%d).txt
```

## 12. Emergency: Force Thread Dump on Unresponsive JVM

```bash
# If jcmd hangs, use jstack (may need -F force)
jstack -F <pid> > threads.txt

# Or send SIGQUIT (Linux)
kill -3 <pid>  # Writes to stdout/stderr of JVM process

# In container: check docker logs / kubectl logs
kubectl logs <pod> --previous | tail -2000
```