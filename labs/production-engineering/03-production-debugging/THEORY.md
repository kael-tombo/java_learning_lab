# THEORY: Production Debugging & Profiling
## Lab 03 | Production Engineering Academy

---

## 1. The Production Debugging Mindset

**Rule 1**: Do no harm. Every action in production can make things worse.
**Rule 2**: Collect data before changing anything. Blind restarts lose evidence.
**Rule 3**: Form hypotheses, test one at a time. Changing 3 things at once means you don't know what fixed it.
**Rule 4**: Have an undo plan before every action.

### The Investigation Framework (USE Method)

For any performance problem:
- **U**tilization: How busy is each resource? (CPU, memory, disk, network)
- **S**aturation: Are any resources at capacity? (queue depth, wait time)
- **E**rrors: Are there error counts or log events?

```
Problem: p99 latency = 3000ms (was 50ms)

USE Analysis:
  CPU:      Utilization=75%, Saturation (run-queue)=0.2, Errors=0
  Memory:   Utilization=82%, Saturation (GC overhead)=15%(!), Errors=0
  Disk I/O: Utilization=5%,  Saturation=0,               Errors=0
  Network:  Utilization=30%, Saturation=0,               Errors=0

→ Memory saturation (high GC overhead) is suspect
→ Check GC logs, heap dump
```

---

## 2. JVM Diagnostic Tools — The Complete Arsenal

### 2.1 jcmd — Production's Best Friend

```bash
# List all JVM processes and PIDs
jcmd

# Full JVM info snapshot (version, flags, args)
jcmd <pid> VM.info

# Currently active JVM flags (some may differ from startup args)
jcmd <pid> VM.flags

# Top memory consumers by class (lightweight heap analysis)
jcmd <pid> GC.class_histogram | head -30

# Live heap statistics (no heap dump needed)
jcmd <pid> GC.heap_info

# Thread count and states
jcmd <pid> Thread.print | grep "java.lang.Thread.State:" | sort | uniq -c

# Full thread dump with locks
jcmd <pid> Thread.print

# Native memory breakdown (heap + metaspace + code cache + ...)
jcmd <pid> VM.native_memory summary
jcmd <pid> VM.native_memory detail  # Detailed (more overhead)

# Heap dump (use with care in production — pauses JVM)
jcmd <pid> GC.heap_dump /tmp/heap-$(date +%Y%m%d-%H%M%S).hprof

# Java Flight Recorder — low overhead continuous profiling
jcmd <pid> JFR.start name=prod duration=60s filename=/tmp/recording.jfr
jcmd <pid> JFR.check     # Check recording status
jcmd <pid> JFR.stop name=prod  # Stop and write

# Trigger GC (rarely useful, but exists)
jcmd <pid> GC.run

# System properties
jcmd <pid> VM.system_properties | grep -i "spring\|server\|db"
```

### 2.2 jstat — Real-Time GC Monitoring

```bash
# Print GC stats every 1 second for 60 iterations
jstat -gcutil <pid> 1000 60

# Output columns:
# S0    S1    E      O      M    CCS  YGC YGCT   FGC  FGCT   CGC CGCT   GCT
#  0.0  36.5  89.2   67.4  97.8  94.3  342  4.231   3  12.456   0  0.000  16.687
#
# S0/S1: Survivor space 0/1 utilization %
# E: Eden utilization %
# O: Old gen utilization %  ← Watch this! > 80% = danger zone
# M: Metaspace utilization %
# YGC: Young GC count | YGCT: Young GC time (seconds total)
# FGC: Full GC count | FGCT: Full GC time
# GCT: Total GC time

# GC overhead % = GCT / runtime × 100
# Alert if > 5%
```

### 2.3 jstack — Thread Dump Analysis

```bash
# Thread dump to file
jstack <pid> > /tmp/threads-$(date +%H%M%S).txt

# Include lock info (-l flag)
jstack -l <pid> > /tmp/threads-lock-$(date +%H%M%S).txt

# Analyze: count threads by state
grep "State:" /tmp/threads-*.txt | sort | uniq -c | sort -rn

# Find all threads waiting on DB connection
grep -B5 "hikari\|JDBC\|waiting for connection" /tmp/threads-*.txt

# Find deadlocks (jstack detects them)
grep -A10 "Found.*deadlock" /tmp/threads-*.txt
```

### 2.4 async-profiler — The Production Profiler

async-profiler uses Linux `perf_events` + `AsyncGetCallTrace` — no safepoint bias, minimal overhead (~1-2% CPU).

```bash
# Download
curl -L https://github.com/jvm-profiling-tools/async-profiler/releases/latest/download/async-profiler-linux-x64.tar.gz | tar xz

# CPU profiling (wall-clock — see where CPU time goes)
./profiler.sh -e cpu -d 60 -f /tmp/cpu-$(date +%Y%m%d-%H%M).html <pid>

# Allocation profiling (find what creates the most garbage)
./profiler.sh -e alloc -d 60 -f /tmp/alloc.html <pid>

# Wall-clock profiling (includes blocked/waiting time — good for I/O analysis)
./profiler.sh -e wall -d 60 -f /tmp/wall.html <pid>

# Lock profiling (find contended locks)
./profiler.sh -e lock -d 60 -f /tmp/lock.html <pid>

# Combined CPU + allocation
./profiler.sh start -e cpu,alloc <pid>
./profiler.sh stop -f /tmp/combined.html <pid>

# In K8s: run profiler inside container
kubectl exec -it <pod> -- /app/profiler.sh -e cpu -d 30 -f /tmp/flame.html 1
kubectl cp <namespace>/<pod>:/tmp/flame.html ./flame-$(date +%Y%m%d-%H%M).html
```

### 2.5 Java Flight Recorder (JFR) — Continuous Production Profiling

JFR has < 1% overhead and can run continuously in production.

```bash
# Start continuous recording
jcmd <pid> JFR.start \
  name=production-profile \
  settings=profile \          # default, profile, or custom .jfc file
  maxage=2h \                 # Keep last 2 hours of data
  maxsize=512m \              # Max disk usage
  filename=/tmp/jfr/recording.jfr

# Check status
jcmd <pid> JFR.check

# Dump current data (snapshot without stopping)
jcmd <pid> JFR.dump name=production-profile filename=/tmp/snapshot-$(date +%H%M).jfr

# Stop when done
jcmd <pid> JFR.stop name=production-profile

# Always-on JFR (startup flag):
-XX:StartFlightRecording=name=startup,maxsize=512m,maxage=2h,dumponexit=true,filename=/tmp/jfr/recording.jfr
```

Open JFR files in **JDK Mission Control** (JMC) for analysis.

---

## 3. Heap Dump Analysis with Eclipse MAT

### 3.1 Capture Without Pausing (Low Impact)

```bash
# Method 1: jcmd (pauses JVM briefly)
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Method 2: Java startup flags (auto on OOM — recommended)
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/heap/

# Method 3: Programmatic (emergency admin endpoint)
import com.sun.management.HotSpotDiagnosticMXBean;
ManagementFactory.getPlatformMXBean(HotSpotDiagnosticMXBean.class)
    .dumpHeap("/tmp/heap.hprof", true);  // true = live objects only
```

### 3.2 MAT Analysis Workflow

```
1. Open Eclipse MAT
2. File → Open Heap Dump → select .hprof
3. Run "Leak Suspects" report
   → Shows top memory consumers and who references them
   
4. Dominator Tree tab
   → Objects sorted by retained heap size
   → "Retained heap" = all memory freed if this object GC'd
   → Find the biggest retainer — that's your leak
   
5. Histogram tab
   → All classes sorted by instance count / heap size
   → Look for unexpectedly large counts
   
6. Path to GC Roots
   → Right-click suspicious object → "Path to GC Roots"
   → Shows the reference chain keeping it alive
   → This tells you WHERE the reference is held

Common findings:
  - ArrayList<Order> in a static field = no bound on size
  - HashMap<String, Session> in application context = session leak
  - byte[] in cache = too much data cached
  - Thread stack holding request reference = ThreadLocal leak
```

### 3.3 Interpreting OQL (Object Query Language)

```sql
-- Find all HttpServletRequest objects in heap (potential request leak)
SELECT * FROM javax.servlet.http.HttpServletRequest

-- Find strings > 1MB
SELECT s, s.count, s.@retainedHeapSize FROM java.lang.String s
WHERE s.@retainedHeapSize > 1048576

-- Count instances by class prefix
SELECT classof(s).name, count(*) FROM java.lang.Object s
WHERE classof(s).name LIKE "com.company.*"
```

---

## 4. Distributed Tracing

### 4.1 The Three Pillars

```
Logs   → What happened (discrete events)
Metrics → How much (aggregated numbers)
Traces  → Why it was slow (end-to-end request journey)
```

### 4.2 Trace Anatomy

```
Trace ID: abc123
  │
  ├─ Span: api-gateway (2ms)
  │         Root span: request enters here
  │
  ├─ Span: payment-service.processPayment (185ms)
  │    ├─ Span: validate (1ms)
  │    ├─ Span: db.findOrder (50ms)     ← Slow!
  │    ├─ Span: fraud-check (30ms)
  │    └─ Span: banking-api (95ms)      ← Very slow!
  │
  └─ Span: notification-service (5ms)
```

### 4.3 OpenTelemetry Java Agent (Zero Code Changes)

```bash
java -javaagent:opentelemetry-javaagent.jar \
  -Dotel.service.name=payment-service \
  -Dotel.exporter.otlp.endpoint=http://jaeger-collector:4317 \
  -Dotel.traces.sampler=parentbased_traceidratio \
  -Dotel.traces.sampler.arg=0.05 \  # Sample 5% of traces
  -jar payment-service.jar
```

### 4.4 Manual Span with Business Context

```java
@Autowired Tracer tracer;

public PaymentResult processPayment(PaymentRequest req) {
    Span span = tracer.spanBuilder("processPayment")
        .setAttribute("payment.amount", req.getAmount().toPlainString())
        .setAttribute("payment.currency", req.getCurrency())
        .setAttribute("payment.method", req.getMethod())
        .startSpan();

    try (Scope scope = span.makeCurrent()) {
        // All nested spans automatically become children of this span
        PaymentResult result = doProcess(req);
        span.setAttribute("payment.result", result.getStatus());
        return result;
    } catch (Exception e) {
        span.setStatus(StatusCode.ERROR, e.getMessage());
        span.recordException(e);
        throw e;
    } finally {
        span.end();
    }
}
```

---

## 5. Structured Logging for Debugging

```java
// WRONG — unstructured, hard to search/alert on
log.error("Payment failed for user " + userId + ": " + e.getMessage());

// RIGHT — structured (searchable in Kibana, alertable in Grafana)
log.atError()
   .addKeyValue("event", "payment_failed")
   .addKeyValue("userId", userId)
   .addKeyValue("amount", amount)
   .addKeyValue("errorCode", e.getErrorCode())
   .addKeyValue("traceId", MDC.get("traceId"))  // Auto-set by OTel
   .setCause(e)
   .log("Payment processing failed");

// JSON output:
// {"timestamp":"...","level":"ERROR","event":"payment_failed",
//  "userId":"usr-123","amount":"99.99","errorCode":"CARD_DECLINED",
//  "traceId":"abc123","message":"Payment processing failed","exception":"..."}
```
