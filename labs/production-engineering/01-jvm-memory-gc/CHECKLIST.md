# PRODUCTION CHECKLIST: JVM Memory & GC
## Lab 01 | Go-Live Checklist | Production Engineering Academy

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
