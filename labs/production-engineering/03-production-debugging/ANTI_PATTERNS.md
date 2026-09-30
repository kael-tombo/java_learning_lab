# ANTI-PATTERNS: Production Debugging & Diagnostics
## Lab 03 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: Safepoint Bias & Profiler Distortion

### The Mistake
Using traditional JVM-level sampling profilers (e.g., standard VisualVM, older YourKit/JProfiler sampling modes) that rely on JVM TI `GetAllStackTraces` or safepoints to measure CPU latency and method execution time.

### Why It Fails
1. **Safepoint Bias**: The JVM can only halt threads to sample stack traces at specific "safepoints" (e.g., method returns, loop back-edges, allocation sites).
2. Counted loops and uncounted loops compiled by JIT C2 often omit safepoint checks.
3. As a result, the profiler reports high CPU usage on whatever method executes immediately *after* the heavy loop finishes when reaching a safepoint, completely misleading engineers about the actual bottleneck!
4. Traditional profilers can also add 10-30% CPU overhead, compounding production incidents.

### The Correct Production Solution
Use **async-profiler** or **Java Flight Recorder (JFR)**:
- `async-profiler` uses OS signals (`SIGPROF`) and AsyncGetCallTrace, capturing stack traces regardless of whether the thread is at a safepoint.
- Overhead is typically $< 1-2\%$, safe to run directly in live production traffic.
- Collect both CPU and allocation profiles:
  ```bash
  ./asprof -d 30 -f /tmp/profile.html -e cpu <pid>
  ./asprof -d 30 -f /tmp/alloc.html -e alloc <pid>
  ```

---

## Anti-Pattern 2: Attaching Interactive Remote Debuggers (JDWP) in Production

### The Mistake
Opening port 5005 with `-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005` in production and setting a breakpoint in IntelliJ/Eclipse.

### Why It Fails
1. Setting a breakpoint suspends either the target thread or the entire JVM (`SUSPEND_ALL`).
2. Downstream calls time out; health check probes (`/actuator/health`, Kubernetes liveness probes) fail.
3. Kubernetes kills the container and initiates cascading restarts.
4. JDWP communication is unencrypted and unauthenticated by default; exposing port 5005 allows arbitrary remote code execution (RCE).

### The Correct Production Solution
- **Dynamic Logging**: Adjust log levels at runtime via Spring Boot Actuator:
  `POST /actuator/loggers/com.learning.order {"configuredLevel": "DEBUG"}`
- **Continuous Profiling / JFR**: Collect call traces without halting threads.
- **eBPF Tracing**: Trace function arguments dynamically using `bpftrace` or `bcc-tools` without JVM agent overhead.

---

## Anti-Pattern 3: Inadequate Disk Space for Emergency Heap Dumps

### The Mistake
Enabling `-XX:+HeapDumpOnOutOfMemoryError` pointing to the container root filesystem (`/tmp` or `/app`).

### Why It Fails
1. A container typically has a root ephemeral storage limit of 5-10 GB.
2. An 8 GB JVM heap dump will completely exhaust container ephemeral storage.
3. Linux disk writes fail midway; the heap dump becomes corrupt and unreadable.
4. Kubernetes evicts the pod due to `The node was low on resource: ephemeral-storage`, destroying the half-written dump before engineers can retrieve it.

### The Correct Production Solution
Mount a dedicated high-throughput, persistent, or auto-syncing scratch volume or execute a streaming dump script:
```yaml
volumeMounts:
  - name: heap-dump-volume
    mountPath: /dumps
volumes:
  - name: heap-dump-volume
    emptyDir:
      sizeLimit: 30Gi
```
Or execute a shell script upon OOM that compresses and streams directly to Cloud Storage:
```bash
-XX:OnOutOfMemoryError="/scripts/stream_dump_to_s3.sh %p"
```

---

## Anti-Pattern 4: The Blind Pod Restart (Destruction of Forensic Evidence)

### The Mistake
When an incident occurs (P99 latency spikes or CPU reaches 100%), on-call engineers immediately execute `kubectl rollout restart deployment/<app>` or kill the container without capturing forensic artifacts.

### Why It Fails
1. Restarting temporarily relieves symptoms (e.g., clears leaking memory or thread pools), but provides zero root cause data.
2. The incident recurs within hours or days, often during higher-traffic peak periods.
3. All volatile diagnostic telemetry (thread stacks, JIT compilation logs, socket queues, heap state) is permanently destroyed.

### The Correct Production Solution
Execute an **Automated Forensic Capture Pre-Stop Hook** or on-call snapshot script *before* killing the pod:
```bash
# Capture diagnostic triage snapshot in < 15 seconds:
PID=$(jcmd | grep -v JCmd | awk '{print $1}')
jcmd $PID Thread.print > /dumps/thread_dump_$(date +%s).tdump
jcmd $PID GC.heap_info > /dumps/heap_info_$(date +%s).txt
jcmd $PID VM.flags > /dumps/vm_flags.txt
top -b -n 1 -H -p $PID > /dumps/top_threads.txt
```
Then proceed with automated rolling restart.

---

## Anti-Pattern 5: Using `jstack -F` or `jmap -dump:live` on Large Heaps During Peak Traffic

### The Mistake
Running `jmap -dump:live,format=b,file=heap.hprof <pid>` or `jstack -F <pid>` against a live 32GB production JVM heap to inspect memory or locked threads.

### Why It Fails
1. The `-dump:live` flag forces a **Full Stop-The-World (STW) Garbage Collection** before dumping the heap to count only live objects. On a 32GB heap, this can pause the JVM for 15 to 45 seconds!
2. The `-F` (force) flag attaches via the Serviceability Agent (ptrace), which suspends all OS threads immediately, bypassing JVM safepoints.
3. Upstream load balancers detect health check timeouts, declare all pods dead, and drop the entire cluster offline.

### The Correct Production Solution
- **Never use `live` during peak production**:
  Omit `:live` to skip the mandatory STW collection:
  `jcmd <pid> GC.heap_dump /dumps/heap.hprof`
- **Use Class Histograms for Instant Triage**:
  `jcmd <pid> GC.class_histogram` inspects object counts and byte footprint in milliseconds without taking a full multi-gigabyte heap dump.
- **Use `jcmd <pid> Thread.print`** instead of `jstack -F`.

---

## Anti-Pattern 6: Thread Dump Misinterpretation: The "BLOCKED" Red Herring

### The Mistake
Opening a thread dump, filtering strictly for threads in `BLOCKED` state, and assuming the method holding the lock is the root cause of high CPU utilization.

### Why It Fails
1. **Blocked Threads Consume 0% CPU**: A `BLOCKED` or `WAITING` thread is parked by the OS scheduler; it consumes zero CPU cycles.
2. The true culprit consuming 100% CPU is almost always a thread in `RUNNABLE` state executing an infinite loop, regex catastrophic backtracking, un-indexed collection scan, or JIT deoptimization loop.
3. Focusing exclusively on `BLOCKED` locks treats the symptom (lock queues backing up because the CPU-hog thread isn't releasing its monitor) rather than the root cause.

### The Correct Production Solution
Correlate thread dumps with OS-level per-thread CPU consumption:
1. Run `top -H -p <pid>` to find the Thread ID (TID) consuming $> 90\%$ CPU (e.g. TID `14290`).
2. Convert TID to hexadecimal: `printf "%x\n" 14290` $\to$ `0x37d2`.
3. Search the thread dump for `nid=0x37d2`:
   ```bash
   grep -A 30 "nid=0x37d2" thread_dump.txt
   ```
4. This identifies the exact method and line of code executing the CPU-spinning work!

---

## Anti-Pattern 7: Enabling Fleet-Wide Trace/Debug Logging During High Load

### The Mistake
To investigate a localized production error, an engineer changes the root logger level to `DEBUG` or `TRACE` across all 50 production pods.

### Why It Fails
1. **Synchronous File/Socket I/O Saturation**: Log output increases by $100\times$, saturating container disk IOPS and causing thread blocking on Logback/Log4j2 appenders.
2. **String Allocation & GC Storm**: Millions of string concatenations and parameter formatting objects flood Eden space, driving Minor GC frequency from 1/min to 10/second.
3. **Log Storage Cost Explosion**: Ingestion quotas in Datadog/Splunk/CloudWatch are exhausted within minutes, triggering massive overage charges or dropping logs.

### The Correct Production Solution
1. **Surgically Scope Log Changes**: Change log levels only on the specific package or class, on a single canary pod:
   ```bash
   curl -X POST http://pod-01:8080/actuator/loggers/com.learning.payment.StripeClient \
     -H 'Content-Type: application/json' \
     -d '{"configuredLevel": "DEBUG"}'
   ```
2. **Use Conditional & Mapped Diagnostic Context (MDC)**:
   Log debug data only for specific tenant IDs or test accounts using dynamic filters.

---

## Anti-Pattern 8: Neglecting Native Memory Tracking (NMT) and Off-Heap Leaks

### The Mistake
Assuming all JVM memory consumption is bounded by `-Xmx` (heap size). When container RSS memory exceeds limits and the pod is OOMKilled, engineers examine heap dumps and find the heap only 30% full.

### Why It Fails
Heap dumps **ONLY inspect the JVM garbage-collected heap**. They are completely blind to off-heap native memory:
- Direct ByteBuffers (`ByteBuffer.allocateDirect()`).
- Netty ByteBuf pools and Jemalloc native arenas.
- Metaspace, JIT CodeCache, and Thread Stacks (`-Xss1m` $\times 2,000$ threads = 2GB native memory!).
- JNI native libraries (e.g. RocksDB, snappy, zstandard).

### The Correct Production Solution
1. **Always Enable Native Memory Tracking in Production**:
   Add JVM flag: `-XX:NativeMemoryTracking=summary` (negligible $< 1\%$ overhead).
2. **Inspect Native Memory Breakdown**:
   ```bash
   jcmd <pid> VM.native_memory baseline
   # After traffic run:
   jcmd <pid> VM.native_memory detail.diff
   ```
3. Look specifically for growth in `Internal`, `Thread`, `Arena`, and `DirectByteBuffer` allocations.
