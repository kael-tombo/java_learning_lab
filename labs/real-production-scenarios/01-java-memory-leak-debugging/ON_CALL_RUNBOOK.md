# On-Call Runbook: Java Memory Leak Debugging (Lab 01)

> Scope: JVM heap/Metaspace/native memory leaks in production Java services.
> Audience: on-call engineer responding to memory-related alerts.

## 1. Service Map & SLOs

| Component | SLO | Key Signal |
|---|---|---|
| JVM Heap | p99 GC pause < 200ms, Old Gen < 70% post-GC | `jstat -gcutil`, GC logs |
| Metaspace | Growth < 10MB/hr, ClassLoader count stable | `jcmd VM.native_memory`, `VM.classloader_stats` |
| Direct Memory | < 80% of `-XX:MaxDirectMemorySize` | `jcmd VM.native_memory` |
| Thread Count | < 80% of `-XX:MaxThreadCount` | `jcmd Thread.print` |

## 2. Triage Decision Tree (first 5 minutes)

```
alert: heap / metaspace / direct memory / thread count?
├─ Heap OOM or > 85% Old Gen → §3 Heap Exhaustion
├─ Metaspace OOM or growth > 50MB/hr → §4 Metaspace Leak
├─ Direct Buffer OOM → §5 Native Memory Leak
├─ Thread count > 80% limit → §6 Thread Leak
└─ GC overhead > 15% → §7 GC Thrashing
```

Always note: JVM flags (`-Xmx`, `-XX:MaxMetaspaceSize`), recent deployments, traffic changes.

## 3. Runbook: Heap Exhaustion / OOM: Java Heap Space

**Symptoms:** `OutOfMemoryError: Java heap space`, service crashes/restarts, Old Gen > 90% post-GC.

**Immediate Mitigation (0–5 min):**
```bash
# 1. Preserve evidence BEFORE restart
jcmd <pid> GC.heap_dump /tmp/heapdump-$(date +%Y%m%d-%H%M%S).hprof
jcmd <pid> Thread.print > /tmp/threaddump-$(date +%Y%m%d-%H%M%S).txt

# 2. Restore service
kubectl rollout restart deployment/<service>

# 3. Temporary capacity increase
kubectl set env deployment/<service> JAVA_OPTS="-Xmx4g -Xms4g"
```

**Root Cause Analysis (post-incident):**
1. Open heap dump in Eclipse MAT → **Leak Suspects** report
2. Check **Dominator Tree** for largest retained objects
3. Right-click suspect → **Path to GC Roots** → exclude weak/soft refs
4. Common patterns:
   - `static Map/List` growing unbounded → add eviction/TTL
   - `ThreadLocal` holding request objects → add `remove()` in `finally`
   - Unclosed `Connection`/`Statement`/`ResultSet` → fix try-with-resources
   - Cache without size limit → add `maximumSize()` + `expireAfterWrite()`

**Verification:** Soak test 1 hour, Old Gen post-GC < 60%.

## 4. Runbook: Metaspace Leak / OOM: Metaspace

**Symptoms:** `OutOfMemoryError: Metaspace`, ClassLoader count increasing, no class unloading in GC logs.

**Immediate Mitigation (0–5 min):**
```bash
# 1. Capture ClassLoader state
jcmd <pid> VM.classloader_stats > /tmp/cl-stats-$(date +%Y%m%d-%H%M%S).txt
jcmd <pid> VM.native_memory detail.diff > /tmp/nmt-diff.txt

# 2. Restart (only mitigation for active leak)
kubectl rollout restart deployment/<service>

# 3. Increase Metaspace temporarily
kubectl set env deployment/<service> JAVA_OPTS="... -XX:MaxMetaspaceSize=1g"
```

**Root Cause Analysis:**
1. **GC logs:** Confirm `Class unloading: 0 classes, 0 loaders` despite Metaspace churn
2. **Heap dump in MAT:** Find `URLClassLoader` with large retained heap
3. **Path to GC Roots:** Typically `ThreadLocalMap.Entry → [Framework Context] → ClassLoader`
4. **Common culprits:**
   - ThreadLocal in web filter/servlet not calling `remove()`
   - JDBC driver not deregistered on undeploy
   - Logging framework (Log4j) holding ClassLoader refs
   - Third-party library with ThreadLocal leak (see §8)

**Fix Patterns:**
```java
// ThreadLocal cleanup in filter
try {
    threadLocal.set(context);
    chain.doFilter(request, response);
} finally {
    threadLocal.remove();  // CRITICAL
}

// JDBC driver deregistration in ServletContextListener
@PreDestroy
public void destroy() {
    Enumeration<Driver> drivers = DriverManager.getDrivers();
    while (drivers.hasMoreElements()) {
        Driver d = drivers.nextElement();
        if (d.getClass().getClassLoader() == getClass().getClassLoader()) {
            DriverManager.deregisterDriver(d);
        }
    }
}
```

## 5. Runbook: Native Memory Leak (Direct Buffers / JNI)

**Symptoms:** `OutOfMemoryError: Direct buffer memory`, RSS growing beyond `-Xmx + MaxMetaspaceSize + MaxDirectMemorySize`.

**Diagnose:**
```bash
# Check direct buffer usage
jcmd <pid> VM.native_memory detail | grep -A5 "Direct"
jcmd <pid> GC.class_histogram | grep DirectByteBuffer

# Check JNI allocations
jcmd <pid> VM.native_memory detail | grep -A5 "Internal"
```

**Common Causes & Fixes:**
| Cause | Fix |
|---|---|
| `ByteBuffer.allocateDirect()` without cleanup | Use `Arena.ofConfined()` (Java 20+) or explicit `Cleaner.clean()` |
| Netty/PooledByteBufAllocator leak | Enable leak detection: `-Dio.netty.leakDetectionLevel=ADVANCED` |
| JNI library not freeing memory | Upgrade library, report bug, or wrap in `AutoCloseable` |
| MappedByteBuffer (file mapping) not cleaned | Use `MemorySegment` + `Arena` or `FileChannel.map` with cleanup |

## 6. Runbook: Thread Leak

**Symptoms:** Thread count growing, `OutOfMemoryError: unable to create new native thread`, thread dump shows many idle threads.

**Diagnose:**
```bash
# Thread count over time
watch -n5 "jcmd <pid> Thread.print | grep -c 'java.lang.Thread'"

# Thread dump analysis
jcmd <pid> Thread.print > /tmp/threads.txt
# Look for: thread names indicating source (e.g., "HikariPool-1", "grpc-default-executor")
```

**Common Causes & Fixes:**
| Cause | Fix |
|---|---|
| Unbounded thread pool (`Executors.newCachedThreadPool`) | Use fixed `ThreadPoolExecutor` with bounded queue |
| ThreadLocal preventing thread GC | Fix ThreadLocal leak (§4) |
| Grpc/Netty event loop group not shut down | Add shutdown hook: `eventLoopGroup.shutdownGracefully()` |
| Database connection pool leak → threads | Fix connection leak (§3) |

## 7. Runbook: GC Thrashing (High GC Overhead)

**Symptoms:** GC > 15% CPU time, frequent Full GCs, application throughput near zero.

**Diagnose:**
```bash
# Real-time GC
jstat -gcutil <pid> 1s 20

# GC log analysis
grep "Pause Full" /var/log/app/gc.log | tail -20
```

**Immediate Mitigation:**
```bash
# Rolling restart to clear heap
kubectl rollout restart deployment/<service>

# Tune G1 to start marking earlier
-XX:InitiatingHeapOccupancyPercent=35
-XX:G1ReservePercent=15
```

**Root Cause:**
- Memory leak (§3, §4) → fix leak first
- Heap too small for workload → increase `-Xmx`
- Allocation rate > GC throughput → reduce allocation (object pooling, primitives)
- Humongous objects (G1) → increase region size or use `-XX:G1HeapRegionSize`

## 8. Runbook: Third-Party Library ThreadLocal Leak (Cannot Modify Code)

**Scenario:** A library (e.g., old Spring, Netty, Kafka client) has a known ThreadLocal leak.

**Mitigations (in order of preference):**
1. **Upgrade library** — check release notes for "ThreadLocal leak fix"
2. **Servlet Filter reflection cleanup:**
   ```java
   @Component
   public class ThreadLocalCleanupFilter implements Filter {
       private static final Field THREAD_LOCAL_MAP_FIELD;
       static {
           THREAD_LOCAL_MAP_FIELD = Thread.class.getDeclaredField("threadLocals");
           THREAD_LOCAL_MAP_FIELD.setAccessible(true);
       }
       @Override
       public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
           try { chain.doFilter(req, res); }
           finally { clearThreadLocals(); }
       }
       private void clearThreadLocals() {
           ThreadLocalMap map = (ThreadLocalMap) THREAD_LOCAL_MAP_FIELD.get(Thread.currentThread());
           if (map != null) {
               // Clear entries from known leaking classes
               // Use reflection to call ThreadLocal.remove() on specific instances
           }
       }
   }
   ```
3. **Java Agent** — bytecode instrumentation to auto-insert `remove()` calls
4. **Scheduled restart** — cron job every 4 hours during low traffic
5. **Increase Metaspace** — `-XX:MaxMetaspaceSize=2g` as temporary buffer

## 9. Post-Incident Checklist

- [ ] Heap dump / thread dump / NMT capture preserved (uploaded to S3/GCS)
- [ ] Leak type identified: Heap / Metaspace / Direct / Thread / GC Thrashing
- [ ] Root cause code location found (class, method, line)
- [ ] Fix implemented and code-reviewed
- [ ] Load test validates fix (1 hour soak, memory stable)
- [ ] Monitoring improved: alert on growth rate, not just threshold
- [ ] Runbook updated if new pattern discovered
- [ ] Post-mortem scheduled within 5 business days

## 10. Key Dashboards & Alerts

| Alert | Query (Prometheus) | Severity |
|---|---|---|
| Heap Old Gen > 80% | `jvm_memory_bytes_used{area="old"} / jvm_memory_bytes_max{area="old"} > 0.8` | P1 |
| Metaspace growth > 50MB/hr | `rate(jvm_memory_bytes_used{area="nonheap"}[1h]) > 50e6` | P2 |
| ClassLoader count increasing | `increase(jvm_classes_loaded[4h]) > 100` | P2 |
| Direct memory > 80% | `jvm_memory_bytes_used{area="direct"} / jvm_memory_bytes_max{area="direct"} > 0.8` | P1 |
| Thread count > 80% | `jvm_threads_live / jvm_threads_max > 0.8` | P2 |
| GC overhead > 15% | `rate(jvm_gc_pause_seconds_sum[5m]) / 5m > 0.15` | P1 |

## 11. Useful Commands Quick Reference

```bash
# Full JVM snapshot
jcmd <pid> VM.info
jcmd <pid> VM.flags
jcmd <pid> GC.heap_info
jcmd <pid> VM.native_memory summary

# Heap dump (requires -XX:+UnlockDiagnosticVMOptions)
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Thread dump
jcmd <pid> Thread.print

# ClassLoader analysis
jcmd <pid> VM.classloader_stats
jcmd <pid> VM.native_memory detail | grep -A10 "Class"

# GC analysis
jstat -gcutil <pid> 1s 30
jcmd <pid> GC.run_finalization

# JFR for deep dive
jcmd <pid> JFR.start name=mem settings=profile duration=120s filename=/tmp/mem.jfr
jcmd <pid> JFR.dump name=mem filename=/tmp/mem.jfr

# Kubernetes
kubectl cp <ns>/<pod>:/tmp/heap.hprof ./heap-$(date +%Y%m%d).hprof
kubectl exec -it <pod> -- jcmd <pid> GC.heap_dump /tmp/heap.hprof
```