# RUNBOOK: Production Debugging & Incident Triage
## Lab 03 | Production Engineering Academy

---

## RUNBOOK 01: High CPU / 100% Core Pegging Incident

**Severity**: P1 / P2  
**Target Time to Mitigation**: < 15 minutes  

### Phase 1: Verify & Isolate
1. **Identify the offending process and container**:
   ```bash
   top -H -p $(pgrep -d',' -f java)
   # Or inside container:
   ps -eo pid,tid,%cpu,time,comm --sort=-%cpu | head -n 15
   ```
2. **Find the exact thread with highest CPU**:
   Note the `TID` (Thread ID). Convert to hexadecimal:
   ```bash
   printf "0x%x\n" <TID>
   # Example: TID 24195 -> 0x5e83
   ```
3. **Capture instantaneous thread dump with jcmd**:
   ```bash
   jcmd $(pgrep -f java) Thread.print > /tmp/threaddump-$(date +%s).tdump
   ```
4. **Search for the nid (native thread ID)**:
   ```bash
   grep -A 25 "nid=0x5e83" /tmp/threaddump-*.tdump
   ```
   *Actionable Finding*: This directly reveals the exact class and line number executing the CPU-spinning loop.

---

## RUNBOOK 02: Flamegraph Generation via async-profiler (Non-Intrusive)

### Prerequisites
`async-profiler` installed or mounted in container `/opt/async-profiler/bin/asprof`.

### Execution Steps
1. **Profile CPU for 30 seconds**:
   ```bash
   /opt/async-profiler/bin/asprof -d 30 -f /tmp/cpu_profile.html $(pgrep -f java)
   ```
2. **Profile Memory Allocations (detect GC churn sources)**:
   ```bash
   /opt/async-profiler/bin/asprof -e alloc -d 30 -f /tmp/alloc_profile.html $(pgrep -f java)
   ```
3. **Profile Lock Contention (detect synchronized/ReentrantLock bottlenecks)**:
   ```bash
   /opt/async-profiler/bin/asprof -e lock -d 30 -f /tmp/lock_profile.html $(pgrep -f java)
   ```
4. **Download and inspect**:
   Open the generated HTML flamegraph in any browser. Wider towers indicate code consuming the most CPU or allocating the most objects.

---

## RUNBOOK 03: Safe Heap Dump Acquisition in Production

### The Danger
Running `jcmd <pid> GC.heap_dump` on a 32 GB heap can freeze the JVM process for 15-45 seconds (Stop-The-World) while disk I/O writes out the file. In a Kubernetes cluster, this can trigger failed liveness probes and cause Kubernetes to restart the Pod mid-dump, corrupting the dump!

### Safe Production Protocol:
1. **Remove the Pod from traffic first**:
   ```bash
   # Remove label so Service/Ingress router stops sending requests:
   kubectl label pod <pod-name> app=quarantine --overwrite
   ```
2. **Wait 10 seconds** for active inflight requests to drain.
3. **Capture Heap Dump to persistent scratch volume**:
   ```bash
   jcmd $(pgrep -f java) GC.heap_dump -all=true /dumps/heap-$(hostname)-$(date +%s).hprof
   ```
4. **Compress and upload**:
   ```bash
   gzip -1 /dumps/heap-*.hprof
   # Upload to object storage (S3 / GCS)
   ```
5. **Delete Pod** to let Kubernetes spawn a clean replacement instance.
