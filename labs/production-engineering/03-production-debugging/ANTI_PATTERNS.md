# ANTI-PATTERNS: Production Debugging & Diagnostics
## Lab 03 | Production Engineering Academy

---

## Anti-Pattern 1: The Observer Effect — Sampling Bias & Profiler Distortion

### The Mistake
Using traditional JVM-level sampling profilers that rely on JVM TI `GetAllStackTraces` or safepoints to measure CPU latency.

### Why It Fails
1. **Safepoint Bias**: The JVM can only halt threads to sample stack traces at specific "safepoints" (e.g. method returns, loop back-edges, allocation sites).
2. Counted loops and uncounted loops compiled by JIT C2 often omit safepoint checks.
3. As a result, the profiler reports high CPU usage on whatever method executes immediately *after* the heavy loop finishes when reaching a safepoint, completely misleading engineers about the actual bottleneck!
4. Traditional profilers can also add 10-30% CPU overhead, compounding production incidents.

### The Correct Production Solution
Use **async-profiler** or **Java Flight Recorder (JFR)**:
- `async-profiler` uses OS signals (`SIGPROF`) and AsyncGetCallTrace, capturing stack traces regardless of whether the thread is at a safepoint.
- Overhead is typically $< 1-2\%$, safe to run directly in live production traffic.

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
Enabling `-XX:+HeapDumpOnOutOfMemoryError` pointing to container root filesystem (`/tmp` or `/app`).

### Why It Fails
1. A container typically has a root ephemeral storage limit of 5-10 GB.
2. An 8 GB JVM heap dump will completely exhaust container ephemeral storage.
3. Linux disk writes fail midway; the heap dump becomes corrupt and unreadable.
4. Kubernetes evicts the pod due to `The node was low on resource: ephemeral-storage`, destroying the half-written dump before engineers can retrieve it.

### The Correct Production Solution
Mount a dedicated high-throughput, persistent, or auto-syncing scratch volume:
```yaml
volumeMounts:
  - name: heap-dump-volume
    mountPath: /dumps
volumes:
  - name: heap-dump-volume
    emptyDir:
      sizeLimit: 20Gi
```
Combine with an OOM exit script that uploads the dump to object storage (S3/GCS) on crash.
