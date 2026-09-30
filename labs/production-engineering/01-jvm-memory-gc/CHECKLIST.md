# PRODUCTION CHECKLIST: JVM Memory & GC
## Lab 01 | Go-Live Checklist | Production Engineering Academy — Top 0.0001% Engineering

---

## ✅ Section 1: JVM Memory Sizing (Math Required)

### Heap Sizing Formula
```
Container Memory Limit = JVM Heap + Metaspace + Native Memory (threads + NIO + code cache)

Conservative budget (4 GB container):
  -Xmx              = 2,700m  (67% of container — leaves 1,300m for off-heap)
  -Xms              = 2,700m  (= Xmx: eliminates heap resize GC pauses)
  MaxMetaspaceSize  = 512m
  MaxDirectMemorySize = 256m  (if using Netty or NIO)
  Thread stacks     ≈ 200 threads × 512KB = ~100m
  JIT code cache    ≈ 240m (ReservedCodeCacheSize default)
  Total off-heap    ≈ 1,108m ✅ fits within 1,300m budget
```

### Checklist
- [ ] `-Xmx` ≤ 70% of container memory limit (leave 30% for off-heap)
- [ ] `-Xms` = `-Xmx` (no heap resize at runtime — resizing triggers Full GC on some GCs)
- [ ] `-XX:MetaspaceSize=256m` (pre-size initial metaspace, prevents early resize pauses)
- [ ] `-XX:MaxMetaspaceSize=512m` (cap Metaspace — prevents OOM from class loader leaks)
- [ ] `-XX:MaxDirectMemorySize` explicitly set if using Netty, NIO, or off-heap buffers
- [ ] `-XX:ReservedCodeCacheSize=256m` (JIT compiled code — default 240m is often too small)
- [ ] `-XX:+AlwaysPreTouch` (pre-warm heap pages at JVM startup — eliminates page-fault latency spikes under first load)
- [ ] Container memory `requests` = `limits` in Kubernetes (prevents OOM eviction on noisy neighbor)
- [ ] `-XX:+ExitOnOutOfMemoryError` set (fast-fail → pod restart vs hanging → K8s restarts it)

---

## ✅ Section 2: GC Algorithm Selection Tree

```
Workload profile:
    │
    ├── Latency SLO p99 < 5ms?
    │       └── YES → ZGC   (-XX:+UseZGC -XX:+ZGenerational [Java 21])
    │                        Concurrent, sub-millisecond pauses, scales to TB heaps
    │                        COST: 5–15% throughput vs G1. Set -XX:SoftMaxHeapSize=Xmx×0.9
    │
    ├── Latency SLO p99 < 50ms, heap < 32 GB?
    │       └── YES → G1GC  (-XX:+UseG1GC)
    │                        Well-balanced. Default since Java 9.
    │                        Tune: -XX:MaxGCPauseMillis=20 (target, not guarantee)
    │                              -XX:InitiatingHeapOccupancyPercent=35 (trigger mixed GC earlier)
    │                              -XX:G1ReservePercent=15 (headroom for evacuation)
    │
    ├── Batch/offline processing, throughput > latency?
    │       └── YES → ParallelGC  (-XX:+UseParallelGC)
    │                              Stop-the-world but highest raw throughput
    │                              Tune: -XX:GCTimeRatio=19 (max 5% GC overhead)
    │
    └── Low-latency, heap < 4 GB, single-digit ms p99?
            └── CONSIDER → Shenandoah (-XX:+UseShenandoahGC)
                           Concurrent compaction, lower memory overhead than ZGC
                           Best for: cloud cost-sensitive + latency-sensitive (middle ground)
```

### Per-GC Tuning Checklist
- [ ] **ZGC**: `-XX:+ZGenerational` enabled (Java 21+, 10–40% better throughput vs classic ZGC)
- [ ] **ZGC**: `-XX:SoftMaxHeapSize` = 90% of Xmx (leaves room for allocation spikes)
- [ ] **G1**: `-XX:MaxGCPauseMillis` ≤ 50% of p99 SLO (e.g., SLO=100ms → target=50ms)
- [ ] **G1**: `-XX:InitiatingHeapOccupancyPercent=35` (default 45% often triggers late mixed GC)
- [ ] **G1**: `-XX:G1ReservePercent=15` (prevents "to-space exhausted" Full GC)
- [ ] **All**: `-XX:MaxGCPauseMillis` validated against actual p99 under load — it's a TARGET, not a hard guarantee

---

## ✅ Section 3: Native Memory & Container Accounting

Modern JVM memory is NOT just heap. Failure to account for all regions causes container OOM kills:

| Region | Controlled By | Typical Size |
|---|---|---|
| Java Heap | `-Xmx` | ~2.7 GB (in 4 GB container) |
| Metaspace | `-XX:MaxMetaspaceSize` | 256–512 MB |
| JIT Code Cache | `-XX:ReservedCodeCacheSize` | 256 MB |
| Thread Stacks | `-Xss` × thread count | 200 threads × 512KB = 100 MB |
| Direct ByteBuffers | `-XX:MaxDirectMemorySize` | 256 MB (if used) |
| JVM internal (GC bitmaps, etc.) | Not configurable | ~100–300 MB |
| Loaded native libs (glibc, etc.) | OS | ~50–100 MB |

```bash
# Verify actual native memory breakdown at runtime
jcmd <PID> VM.native_memory summary scale=MB

# In containers, compare RSS vs Xmx to estimate off-heap usage
cat /proc/<PID>/status | grep -E "VmRSS|VmPeak|VmSize"
```

- [ ] `VM.native_memory` run in staging under peak load — total confirmed < container limit
- [ ] `-Xss512k` set (reduce thread stack from 1MB default → half the stack waste for thread pools)
- [ ] glibc `MALLOC_ARENA_MAX=2` set to reduce native heap fragmentation from glibc's per-core arenas

---

## ✅ Section 4: Observability & Diagnostics Pre-Flight

### GC Logging (Zero-Overhead Structured Format)
```bash
-Xlog:gc*:file=/var/log/gc/gc-%t.log:time,uptime,level,tags:filecount=10,filesize=50m
```
- [ ] GC log rotation configured (`filecount=10,filesize=50m`)
- [ ] GC log directory has sufficient disk space (10 × 50 MB = 500 MB reserved)
- [ ] GC logs mounted to persistent volume in K8s (not ephemeral pod storage)

### Heap Dump on OOM
```bash
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/heap/
# CRITICAL: ensure enough disk space (heap dump = Xmx × 1.5 on disk)
# For -Xmx=2700m → reserve at minimum 4 GB on the dump path
```
- [ ] Heap dump directory exists and has write permissions
- [ ] Disk space reserved: at least `Xmx × 1.5` on dump path
- [ ] Heap dumps uploaded to S3/GCS automatically (post-dump hook or init container watcher)
- [ ] `-XX:+ExitOnOutOfMemoryError` paired with heap dump (dump written THEN JVM exits)

### JFR Continuous Profiling
```bash
-XX:StartFlightRecording=name=continuous,settings=profile,maxage=5m,maxsize=256m,dumponexit=true,filename=/var/log/jfr/continuous.jfr
```
- [ ] JFR continuous recording enabled with ≤ 1% overhead (`settings=profile`)
- [ ] `maxage=5m` circular buffer (last 5 minutes always available)
- [ ] `dumponexit=true` (captures final state on crash for post-mortem)

### Native Memory Tracking
```bash
-XX:NativeMemoryTracking=summary   # Low overhead: summary only
# -XX:NativeMemoryTracking=detail  # Higher overhead: use only for investigation
```
- [ ] NMT enabled (summary mode) on all production JVMs

---

## ✅ Section 5: JVM Flags — Security & Correctness

- [ ] `-XX:+DisableExplicitGC` (blocks `System.gc()` calls from third-party libs — can cause stop-the-world Full GC)
- [ ] `-Djava.security.egd=file:/dev/./urandom` (prevents SecureRandom blocking on `/dev/random` at startup)
- [ ] `-Dfile.encoding=UTF-8` explicitly set (container default encoding may differ from build environment)
- [ ] `-Djava.awt.headless=true` (prevents AWT toolkit initialization in server JVMs)
- [ ] Tiered compilation: `-XX:+TieredCompilation` (default on, verify not accidentally disabled)
- [ ] `-XX:+UseStringDeduplication` with G1 (deduplicates String objects in Old Gen — saves 10–25% heap for string-heavy apps)

---

## ✅ Section 6: Application-Level Memory Safety

- [ ] No `finalize()` methods (deprecated Java 9+, blocks GC — migrate to `Cleaner` API or `try-with-resources`)
- [ ] All `static` collections (maps, lists, sets) have bounded size or eviction policy
- [ ] All caches use Caffeine (with `maximumSize` + `expireAfterWrite`) — NOT `HashMap` with no eviction
- [ ] All `Closeable` / `AutoCloseable` resources (streams, connections, channels) in `try-with-resources`
- [ ] No `System.gc()` calls anywhere in production code (grep check in CI)
- [ ] Thread pools use bounded queues: `new ThreadPoolExecutor(core, max, keepAlive, unit, new ArrayBlockingQueue<>(1000))` — NOT `Executors.newCachedThreadPool()` (unbounded)
- [ ] `ThreadLocal` variables explicitly `remove()`d in pool-reused threads (prevents class loader leaks)
- [ ] No `ClassLoader` references stored in static fields (causes metaspace class loader leaks in hot-reload)
- [ ] `String.intern()` not used in hot paths (fills the JVM string table — not GC'd under normal GC)
- [ ] `ObjectInputStream` never deserializes untrusted data (Java deserialization RCE vector)
- [ ] All byte array buffers bounded: `ByteArrayOutputStream` avoided for streaming data (use streaming APIs)

---

## ✅ Section 7: Load Test Acceptance Criteria (Pre-Production Gate)

Must run for **minimum 30 minutes at 110% of expected peak load** before promotion to production.

| Metric | Pass Criteria | Failure Action |
|---|---|---|
| GC pause p99 | ≤ 50% of latency SLO | Tune GC or increase heap |
| GC pause p99.9 | ≤ 80% of latency SLO | Escalate to architect |
| Full GC count | 0 during steady state | Investigate Old Gen growth |
| Old Gen growth rate | Stable (flat line) after 10min warmup | Suspect memory leak — heap dump required |
| Young GC frequency | < 1 per second (too frequent = heap too small) | Increase Xmx or reduce allocation rate |
| Young GC frequency | > 5 minutes between GCs (too infrequent = heap too large) | Reduce Xmx to save container cost |
| Heap usage at steady state | < 70% of Xmx | If > 80%: increase heap or add pods |
| Native memory (RSS) | < container limit × 0.85 | Investigate off-heap allocations |
| Thread count | Stable (not growing) | Thread leak investigation required |

```bash
# Monitor live GC during load test
jcmd <PID> GC.heap_info

# Watch thread count trend
watch -n 5 'jcmd <PID> Thread.print | grep -c "java.lang.Thread"'

# Verify Old Gen stability
jstat -gcold <PID> 5000 60   # 60 samples × 5s = 5 minutes of Old Gen tracking
```

---

## ✅ Section 8: Prometheus / Alerting Requirements

| Alert | Threshold | Severity | Action |
|---|---|---|---|
| JVM Heap Usage | > 70% | Warning | Investigate, prepare to scale |
| JVM Heap Usage | > 85% | Critical | Page on-call — OOM imminent |
| Old Gen Usage | > 60% | Warning | Heap dump + leak investigation |
| Old Gen Usage | > 80% | Critical | Immediate action — possible memory leak |
| GC Full GC Count | > 0 in 5 min | Critical | Investigate immediately |
| GC Pause p99 | > 500ms | Warning | Tune or scale |
| GC Pause p99 | > 2000ms | Critical | SLA breach — escalate |
| Thread Count | > 500 | Warning | Check thread pool sizing |
| Thread Count | > 1000 | Critical | Thread leak — OOM kill likely |
| Metaspace Usage | > 80% of MaxMetaspaceSize | Warning | Class loader leak suspected |

### Micrometer / JVM Actuator Setup
```java
// application.yaml
management:
  metrics:
    enable:
      jvm: true
    tags:
      application: ${spring.application.name}
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
```

---

## ❌ Section 9: Anti-Patterns — Verify These Are ABSENT

- [ ] `-Xmx` = container limit (leaves zero room for off-heap → guaranteed OOM kill)
- [ ] `-Xms` < `-Xmx` (JVM shrinks/expands heap → triggers GC on resize)
- [ ] `System.gc()` in any `@Scheduled` or batch job (triggers Full GC, stops the world)
- [ ] `Executors.newCachedThreadPool()` (unbounded → OOM under load)
- [ ] `new Thread()` in request handlers (thread-per-request = OOM at 50K concurrent users)
- [ ] `ByteArrayOutputStream` accumulating large streaming response bodies (copies full body to heap)
- [ ] `String.intern()` in loops (fills JVM internal string table, not freed by GC)
- [ ] `ObjectInputStream` deserializing messages from untrusted Kafka topics (RCE vulnerability)
- [ ] Static `Map<K,V>` caching session data (grows forever, causes Old Gen OOM)
- [ ] `finalize()` methods on any domain object (GC must run finalizers in dedicated thread — pauses safepoint)
- [ ] `ThreadLocal` set in servlet filter without `remove()` in `finally` (context leaks between requests)
- [ ] `-server` flag absent on Java < 11 (client JIT mode = 5× slower startup JIT, lower peak throughput)


---

## ✅ Pre-Launch JVM Configuration Checklist

### Heap & Memory
- [ ] `-Xmx` set to 70-80% of container memory limit
- [ ] `-Xms` = `-Xmx` (no heap resizing at runtime)
- [ ] `-XX:MetaspaceSize=256m` set (prevent early resizing)
- [ ] `-XX:MaxMetaspaceSize=512m` set (cap Metaspace growth)
- [ ] `-XX:MaxDirectMemorySize` set if using NIO/Netty
- [ ] Container memory limit > JVM total memory (heap + metaspace + stack + code cache)

### GC Selection & Tuning
- [ ] GC algorithm chosen based on workload profile
  - [ ] Latency-sensitive API → ZGC (`-XX:+UseZGC -XX:+ZGenerational` on Java 21)
  - [ ] General microservice → G1GC (`-XX:+UseG1GC`)
  - [ ] Batch processing → ParallelGC
- [ ] `-XX:MaxGCPauseMillis` set to realistic target (< SLO p99)
- [ ] G1: `-XX:InitiatingHeapOccupancyPercent=35` (lower than default 45%)
- [ ] G1: `-XX:G1ReservePercent=15` set for evacuation buffer

### Observability
- [ ] GC logging enabled: `-Xlog:gc*:file=/var/log/gc.log:time,uptime,level,tags:filecount=10,filesize=50m`
- [ ] Heap dump on OOM: `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/heap/`
- [ ] `-XX:+ExitOnOutOfMemoryError` set (fast-fail for K8s restart)
- [ ] JMX enabled for local diagnostic tools (localhost only, no remote!)
- [ ] Native Memory Tracking: `-XX:NativeMemoryTracking=summary`

### JVM Flags
- [ ] `-XX:+DisableExplicitGC` set (prevent `System.gc()` abuse)
- [ ] `-XX:+AlwaysPreTouch` set (pre-warm heap pages at startup)
- [ ] `-server` flag set or confirmed (usually default)
- [ ] Startup args documented in runbook

### Application-Level
- [ ] No `finalize()` methods (deprecated, use Cleaner API)
- [ ] No static collections that grow without bound
- [ ] Large caches have eviction policy (Caffeine, etc.)
- [ ] All `Closeable`/`AutoCloseable` resources in try-with-resources
- [ ] No `System.gc()` calls in production code
- [ ] Thread pools bounded (no unbounded `newCachedThreadPool`)
- [ ] No class loader leaks in hot-reload or plugin systems

### Load Testing
- [ ] Load test run for 30+ minutes at expected peak load
- [ ] GC pause p99 < SLO under load
- [ ] No Full GC during load test
- [ ] Old Gen stabilizes (doesn't grow continuously) under steady load
- [ ] Memory usage steady-state verified

### Monitoring & Alerting
- [ ] Heap usage alert at 70% (warning) and 85% (critical)
- [ ] Old Gen usage alert at 60% (warning) and 80% (critical)
- [ ] Full GC alert configured
- [ ] GC pause time p99 tracked in dashboards
- [ ] OOM events trigger PagerDuty/on-call notification

---

## ❌ Common Anti-Patterns to Verify Are Absent

- [ ] No `-Xmx` equal to container limit (leaves no off-heap room)
- [ ] No `-Xms` smaller than `-Xmx` (heap resize overhead)
- [ ] No `System.gc()` in scheduled jobs
- [ ] No unlimited `new Thread()` creation
- [ ] No `ByteArrayOutputStream` used for large streaming data
- [ ] No `String.intern()` abuse (fills string table)
- [ ] No `ObjectInputStream` deserializing untrusted data
