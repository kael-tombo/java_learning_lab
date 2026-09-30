# RUNBOOK: Production JVM Debugging & Systems Diagnostics
## Lab 03 | Production Engineering Academy — Top 0.0001% Engineering

---

## RUNBOOK 01: High CPU / 100% Core Pegging Incident

**Severity**: P1 / High  
**Target Mitigation Time**: $< 10$ minutes  
**Goal**: Pinpoint the exact line of code spinning CPU without restarting the JVM process.

### Phase 1: Identify Offending OS Native Thread
1. **Find Java Process PID and Inspect Thread Activity**:
   ```bash
   PID=$(pgrep -f java | head -n 1)
   top -b -n 1 -H -p $PID | head -n 25
   ```
   Or inside container:
   ```bash
   ps -eo pid,tid,%cpu,time,comm --sort=-%cpu | head -n 15
   ```
2. **Capture the Offending Thread ID (`TID`)**:
   Note the `TID` consuming the highest CPU percentage (e.g. `TID = 24195`).
3. **Convert TID to Hexadecimal (`nid`)**:
   ```bash
   printf "0x%x\n" 24195
   # Output: 0x5e83
   ```

---

### Phase 2: Capture JVM Thread Dump & Cross-Reference
1. **Capture Instantaneous Thread Dump via `jcmd`**:
   ```bash
   jcmd $PID Thread.print > /tmp/threaddump-$(date +%s).tdump
   ```
2. **Search for `nid` in Thread Dump**:
   ```bash
   grep -A 35 "nid=0x5e83" /tmp/threaddump-*.tdump
   ```

### Phase 3: Diagnostic Decision Matrix
| Stack Trace Signature | Root Cause | Immediate Action |
|---|---|---|
| `java.util.regex.Pattern$*` | Catastrophic Regex Backtracking | Deploy WAF rule blocking input pattern; hotfix regex |
| `java.util.HashMap.get` or `put` | Concurrent access to non-thread-safe HashMap (cyclic linked list) | Quarantine pod; deploy `ConcurrentHashMap` fix |
| `java.lang.Thread.State: RUNNABLE` in application loop | Infinite loop or unthrottled spin-lock | Roll back deployment or hotfix loop condition |
| `C2 CompilerThread0` | JIT Compilation Loop / Deoptimization Storm | Limit compiler threads: `-XX:CICompilerCount=2` |
| `VM Thread` | Stop-The-World GC or Safepoint Loop | Check GC logs: OldGen memory exhaustion |

---

## RUNBOOK 02: Flamegraph Generation via async-profiler (Non-Intrusive)

**Severity**: P1 / P2  
**Prerequisites**: `async-profiler` installed or mounted in container `/opt/async-profiler/bin/asprof`.

### Step 1: CPU Flamegraph (Pinpoint Method CPU Time)
```bash
/opt/async-profiler/bin/asprof -d 30 -f /tmp/cpu_profile.html $PID
```
- **Interpretation**: Flamegraph width is proportional to CPU time. Look for broad plateaus at the top of the towers.

### Step 2: Memory Allocation Profile (Identify GC Churn Sources)
```bash
/opt/async-profiler/bin/asprof -e alloc -d 30 -f /tmp/alloc_profile.html $PID
```
- **Interpretation**: Highlights the exact methods allocating the highest volume of temporary objects in Eden space, driving Minor GC frequency.

### Step 3: Lock Contention Profile (Find Synchronized / Lock Bottlenecks)
```bash
/opt/async-profiler/bin/asprof -e lock -d 30 -f /tmp/lock_profile.html $PID
```
- **Interpretation**: Measures thread wait time blocked on Java monitors (`synchronized`) or `ReentrantLock`.

### Step 4: Wall-Clock Profile (Identify I/O and Network Blocking)
```bash
/opt/async-profiler/bin/asprof -e wall -t -d 30 -f /tmp/wall_profile.html $PID
```
- **Critical Difference**: CPU profiling only samples active running threads; **Wall-Clock profiling** samples all threads regardless of state (`RUNNABLE`, `BLOCKED`, `WAITING`, `TIMED_WAITING`), revealing database, Redis, and downstream HTTP wait times.

---

## RUNBOOK 03: Safe Heap Dump Acquisition & Quarantine Protocol

**Severity**: P1  
**The Danger**: Running `jcmd <pid> GC.heap_dump` on a 16GB–32GB heap pauses the JVM for 15 to 45 seconds. Without quarantining, Kubernetes liveness probes will fail and kill the pod mid-dump, destroying the evidence!

### Step-by-Step Safe Execution:
1. **Remove Pod from Service Routing (Quarantine)**:
   ```bash
   # Change pod labels so Service/Ingress endpoint slices disconnect immediately:
   kubectl label pod order-service-7f89d4-x8k2 app=quarantine --overwrite -n production
   ```
2. **Verify Traffic Disconnection**:
   ```bash
   # Confirm endpoints controller removed pod from active pool:
   kubectl get endpoints order-service -n production
   ```
3. **Wait 10 Seconds for In-Flight Connections to Drain**:
   Allow active HTTP requests to complete cleanly.
4. **Trigger Heap Dump to Dedicated Persistent Volume**:
   ```bash
   jcmd $PID GC.heap_dump -all=true /dumps/heap-$(hostname)-$(date +%s).hprof
   ```
5. **Compress Dump with Zstandard**:
   ```bash
   zstd -3 /dumps/heap-*.hprof -o /dumps/heap-$(hostname).hprof.zst
   # Stream compressed archive to cloud object storage
   ```
6. **Terminate Quarantined Pod**:
   ```bash
   kubectl delete pod order-service-7f89d4-x8k2 -n production
   ```

---

## RUNBOOK 04: Native Memory Leak & Off-Heap Exhaustion Triage

**Severity**: P1  
**Trigger**: Alert `ContainerMemoryUtilization > 95%` while JVM Heap usage is low.

### Step 1: Establish NMT Baseline
```bash
jcmd $PID VM.native_memory baseline
```
Wait 5 to 10 minutes under steady-state traffic.

### Step 2: Compare Native Memory Growth
```bash
jcmd $PID VM.native_memory detail.diff
```
Analyze the diff output:
- **`Class (Metaspace)`**: Growing classes indicate dynamic class generation (CGLIB, proxy generators, reflection inflation).
- **`Thread`**: High thread count allocation (`committed = count * -Xss`).
- **`Internal`**: DirectByteBuffers allocated by Netty or NIO (`Unsafe.allocateMemory`).
- **`Arena Chunk`**: Native jemalloc memory blocks.

### Step 3: Inspect Netty Resource Leaks
Check application logs for Netty leak detector warnings:
```bash
grep -i "LEAK: ByteBuf.release() was not called" /var/log/app/*.log
```
If present: A network handler failed to call `ReferenceCountUtil.release(msg)` in an inbound channel pipeline.

---

## RUNBOOK 05: JVM Safepoint Stalls & CFS CPU Throttling Triage

**Severity**: P2  
**Symptom**: Intermittent P99 latency spikes (e.g. 2–4 seconds) while GC logs report $< 15\text{ms}$ pause times.

### Step 1: Inspect Safepoint Logs
Enable runtime safepoint tracing via `jcmd`:
```bash
jcmd $PID VM.log what="safepoint=debug"
```
Review logs in `/var/log/jvm/gc.log`:
- **`Time to safepoint (TTSP)`**: If TTSP is $> 1,000\text{ms}$ while `vmop` execution is only $5\text{ms}$, a user thread is failing to reach a safepoint poll.
- **Root Cause**: An unrolled counted loop compiled by C2.
- **Fix**: Apply `-XX:+UseCountedLoopSafepoints`.

### Step 2: Verify Linux CFS Scheduler Throttling
Check container cgroup metrics:
```bash
# Cgroup v2:
cat /sys/fs/cgroup/cpu.stat

# Cgroup v1:
cat /sys/fs/cgroup/cpu/cpu.stat
```
Look for:
- `nr_periods`: Total scheduling periods (100ms standard).
- `nr_throttled`: Periods where the container was forcibly frozen.
- `throttled_usec`: Microseconds threads were stalled.
- **Rule of Thumb**: If `nr_throttled / nr_periods > 10%`, the CPU limit is starving the JVM.
- **Remediation**: Increase or remove `resources.limits.cpu` in Kubernetes manifest.
