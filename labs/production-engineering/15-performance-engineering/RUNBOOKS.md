# RUNBOOKS: Hardware-Level Performance Triage, Profiling & Kernel Diagnostics
## Lab 15 | Production Engineering Academy — Top 0.0001% Engineering

---

## Runbook 01: Low-Level CPU Performance Counter & Hardware Cache Profiling (`perf stat` / `perf record`)

### 1. Objective & Symptoms
- **Alert**: P99 latency degrading by > 200% under high throughput while CPU utilization is nominally only 40–60%.
- **Symptom**: Threads appear active, but instructions per cycle (IPC) collapsed. The processor is stalled waiting on DRAM and cache hierarchy misses rather than executing computational instructions.

### 2. Immediate Diagnostic Workflow

#### Step 1: Collect Core Hardware Counters
Attach Linux `perf stat` directly to the target JVM process PID:
```bash
# Capture 15 seconds of hardware architecture metrics
PID=$(pgrep -f "java.*app.jar")
perf stat -p "$PID" \
  -e cycles,instructions,cache-references,cache-misses,branches,branch-misses,bus-cycles,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses \
  -- sleep 15
```

#### Step 2: Compute Architectural Health Ratios

1. **IPC (Instructions Per Cycle)**:
   $$\text{IPC} = \frac{\text{instructions}}{\text{cycles}}$$
   - **$\text{IPC} \ge 1.8$**: Excellent computational pipeline utilization; application is compute-bound or SIMD-accelerated.
   - **$1.0 \le \text{IPC} < 1.8$**: Typical enterprise Java business logic.
   - **$\text{IPC} < 0.6$**: Severe CPU stall! The pipeline spends > 65% of cycles waiting on Memory/L3 bus stalls.

2. **Last Level Cache (LLC) Miss Rate**:
   $$\text{LLC Miss Rate} = \frac{\text{LLC-load-misses}}{\text{LLC-loads}} \times 100\%$$
   - **Threshold**: If $> 15\%$, high probability of pointer chasing (`LinkedList`, sparse `HashMap`, node trees) or random DRAM addressing.

3. **Branch Misprediction Penalty**:
   $$\text{Branch Miss Rate} = \frac{\text{branch-misses}}{\text{branches}} \times 100\%$$
   - **Threshold**: If $> 5\%$, branch predictor thrashing occurs (megamorphic dispatch, unsorted loop comparisons, complex poly-trees). Each branch misprediction forces an 8–20 cycle pipeline flush.

#### Step 3: Pinpoint Exact Instruction Stalls with `perf record`
```bash
# Profile CPU cycle consumers with dwarf stack unwinding
perf record -F 99 -p "$PID" -g -- sleep 20
perf report --stdio --sort=comm,dso,symbol
```

---

## Runbook 02: Triage and Trace False Sharing with `perf c2c`

### 1. Context & Verification
When multiple cores write to separate variables residing on the same 64-byte physical cache line, the MESI hardware coherency protocol floods the interconnect bus with invalidation requests, generating extreme Hit-Modified (HITM) events.

### 2. Execution Runbook

#### Step 1: Record Cache-to-Cache Coherency Events
```bash
# Record cache lines experiencing cross-core contention
perf c2c record -p "$PID" --call-graph dwarf -- sleep 30
```

#### Step 2: Inspect Cache Lines with High HITM
```bash
# Output human-readable analysis to terminal
perf c2c report --stdio > /tmp/perf_c2c_report.txt
head -n 60 /tmp/perf_c2c_report.txt
```

**Key Metric Indicators in Report**:
- Look at the **"Shared Data Cache Line Table"**.
- Check **`Rmt HITM` (Remote Hit on Modified Cache Line)** and **`Lcl HITM` (Local Hit on Modified)**.
- If a single cache line address accounts for $> 30\%$ of total HITM events across the node, False Sharing is confirmed.

#### Step 3: Map Cache Line Offset to Java Field via JOL (Java Object Layout)
Run JOL against the suspected class:
```bash
java -cp "jol-cli.jar:app.jar" org.openjdk.jol.Main internals com.learning.production.lab15.WorkerCounters
```
*Output Analysis*:
```text
OFF  SZ   TYPE DESCRIPTION               VALUE
  0  12        (object header: mark)     0x0000000000000001
 12   4        (object header: class)    0x00010000
 16   8   long WorkerCounters.counterA   0
 24   8   long WorkerCounters.counterB   0
 32   8   long WorkerCounters.counterC   0
 40   8   long WorkerCounters.counterD   0
Instance size: 48 bytes (Space remaining in 64-byte cache line: 16 bytes!)
```
*Conclusion*: All 4 counters reside in bytes 16–47 of the exact same cache line!
*Resolution*: Apply `@jdk.internal.vm.annotation.Contended` or 56-byte dummy long arrays between fields.

---

## Runbook 03: Production Hotspot Analysis Without Safepoint Bias (`async-profiler`)

### 1. Context: Why Standard JVMTI Profiling Fails
Standard JVM sampling profilers (VisualVM, JProfiler in sampling mode) require threads to reach an engine **safepoint** before capturing a stack trace. This introduces **Safepoint Bias**:
- Counted loops without safepoints appear to consume 0% CPU.
- JNI/Syscall transitions appear artificially delayed.
- Allocation hot paths are distorted.

### 2. Execution Runbook

#### Step 1: Capture Async CPU Profile (FlameGraph)
```bash
# Download and execute async-profiler directly against PID
/opt/async-profiler/bin/asprof -d 60 -f /tmp/flamegraph_cpu.html \
  -e cpu \
  --all-user \
  "$PID"
```

#### Step 2: Capture Allocation FlameGraph (Zero-GC Verification)
Find the exact source code locations allocating byte streams and transient objects:
```bash
/opt/async-profiler/bin/asprof -d 60 -f /tmp/flamegraph_alloc.html \
  -e alloc \
  --total \
  "$PID"
```
*Triage Rules*:
1. Filter flame graph by `[alloc]` frames.
2. Locate the top 3 allocation call stacks:
   - If `java.lang.StringCoding` or `StringBuilder`: string concatenation inside hot loop.
   - If `java.lang.Long` / `java.lang.Integer`: generic collection boxing.
   - If byte arrays `byte[]`: unpooled network serialization buffers.

#### Step 3: Capture Thread Lock Contention
```bash
/opt/async-profiler/bin/asprof -d 45 -f /tmp/flamegraph_lock.html \
  -e lock \
  --reverse \
  "$PID"
```
Reveals total wall-clock duration threads spend waiting on `synchronized` monitors, `ReentrantLock`, and parked carriers.

---

## Runbook 04: JIT Compilation & Deoptimization Diagnostic Triage

### 1. Symptoms
- Application runs with stellar performance for 2 hours, then latency suddenly drops by 40% permanently without any code restart or traffic spike.
- Hot method compilation was thrown away due to uncommon traps.

### 2. Runtime JIT Inspection

#### Step 1: Dump Active JIT Compilation Queue
```bash
# Using jcmd to print Compiler state
jcmd "$PID" Compiler.directives_add /etc/jvm/compiler_directives.json
jcmd "$PID" Compiler.CodeList > /tmp/jit_codelist.txt
grep -E "PaymentProcessor|MatchingEngine" /tmp/jit_codelist.txt
```

#### Step 2: Trace Live Deoptimizations via Dynamic Log
Attach JIT diagnostic logging without service restart:
```bash
jcmd "$PID" VM.command_line
# If running with -XX:+UnlockDiagnosticVMOptions, dynamic logging can be piped
jcmd "$PID" Compiler.perfmap
```

#### Step 3: Offline JIT Log Analysis via JITWatch
If the JVM was launched with `-XX:+UnlockDiagnosticVMOptions -XX:+TraceClassLoading -XX:+LogCompilation -XX:LogFile=/var/log/jvm/jit.log`:
```bash
# Analyze compilation levels and deoptimization traps
grep -E "make_not_entrant|uncommon_trap" /var/log/jvm/jit.log | tail -n 50
```

**Common Trap Signatures**:
- `reason='class_check'`: Polymorphic call site turned megamorphic. JIT inlining revoked.
- `reason='null_check'`: JIT assumed parameter was never null, then a single null hit the path.
- `reason='predicate'`: Loop unrolling boundary assumption broken by sudden array size shift.

---

## Runbook 05: Linux Kernel I/O and Network Bypass Diagnostics (`ethtool`, `sysctl`, `irqbalance`)

### 1. Low-Latency Network Socket Tuning

#### Step 1: Verify Hardware Interrupt (IRQ) Balancing
High-throughput network applications must avoid processing all network card interrupts on Core 0:
```bash
# Check per-core network interface IRQ distributions
cat /proc/interrupts | grep -E "eth0|ens5|mlx5"
```
*Resolution*:
- Disable `irqbalance` daemon for pinned low-latency architectures.
- Manually bind NIC hardware ring queues to non-isolated CPUs:
```bash
# Bind IRQ 124 to CPU mask 0x0000000c (Cores 2 and 3)
echo "c" > /proc/irq/124/smp_affinity
```

#### Step 2: Inspect Socket Drop & Buffer Overflows
```bash
netstat -s | grep -E "buffer errors|pruned|overflowed"
ss -t -i -m
```
If `receive buffer errors` is climbing:
```bash
# Increase kernel max receive/send socket buffers
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
```
