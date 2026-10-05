# REAL_WORLD_PROJECT — JVM Internals

## Project: Production JVM Performance Engineering

A comprehensive real-world scenario simulating production JVM performance engineering at scale.

---

## Scenario Overview

**Company:** FinTech Platform processing $50B/day in transactions
**Stack:** Java 21, Spring Boot 3.2, PostgreSQL, Kafka, Kubernetes
**Scale:** 200 pods, 16 vCPU / 32 GB RAM each, 2 TB heap total
**SLA:** p99 latency < 50ms, 99.99% availability, zero data loss

---

## Incident 1: "The 2 AM GC Storm"

### Symptom
```
02:13:45 ALERT: p99 latency 2,847ms (SLA: 50ms)
02:13:47 ALERT: Pod evictions - OOMKilled
02:14:12 ALERT: Kafka consumer lag 2.3M messages
```

### Given Artifacts
- GC logs (unified format, 6 hours)
- JFR recording (continuous, 4 hours)
- Thread dumps (every 30s during incident)
- Kubernetes events and metrics
- Application logs (structured JSON)

### Investigation Tasks

#### Task 1: GC Log Analysis
```bash
# Parse GC logs
gceasy gc.log --output report.html

# Key questions:
1. What GC algorithm? (G1/ZGC/Parallel)
2. Young GC frequency before/during incident?
3. Old GC frequency and duration?
4. Heap occupancy trend?
5. Promotion rate spike?
6. Humongous object allocation?
```

**Expected Findings:**
- G1 with default settings
- Young GC every 2s → every 200ms (10x increase)
- Mixed GC every 5min → every 30s
- Promotion rate: 50 MB/s → 800 MB/s
- Humongous objects: 15% of allocations (large DTOs)

#### Task 2: JFR Deep Dive
```bash
# Analyze allocation
jfr print --events jdk.ObjectAllocationInNewTLAB recording.jfr | head -50

# Analyze lock contention
jfr print --events jdk.JavaMonitorEnter recording.jfr

# Analyze safepoints
jfr print --events jdk.SafepointBegin,jdk.SafepointEnd recording.jfr
```

**Expected Findings:**
- Top allocation: `TransactionDTO` (2.4KB, 1.2M/sec)
- Lock contention: `AccountService.balance` (ReentrantReadWriteLock)
- Safepoint storms: 47 safepoints in 60s during peak (normal: 2/min)

#### Task 3: Root Cause Identification

**Primary Cause:** 
New feature deployed at 02:00 - "Bulk Transaction Export" creates massive `TransactionDTO` objects with nested collections, triggering:
1. Humongous object allocation in G1 (direct to old gen)
2. Premature promotion (survivor spaces overwhelmed)
3. Remembered set explosion (cross-region refs)
4. Mixed GC cascade (old gen fill → full GC → compaction)

**Contributing Factors:**
- `-XX:MaxGCPauseMillis=200` too aggressive for workload
- No `-XX:G1HeapRegionSize` tuning (default 1MB, too small for humongous)
- Missing `-XX:G1MixedGCLiveThresholdPercent` tuning

### Resolution Plan

#### Immediate (Hotfix - 30 min)
```bash
# Rolling restart with tuned flags
-XX:+UseG1GC
-XX:MaxGCPauseMillis=500
-XX:G1HeapRegionSize=16m
-XX:InitiatingHeapOccupancyPercent=35
-XX:G1MixedGCLiveThresholdPercent=75
-XX:G1MixedGCCountTarget=4
```

#### Short-term (Sprint 1)
- Refactor `TransactionDTO` to use streaming (avoid materializing full object)
- Implement object pooling for frequent DTOs
- Add allocation rate monitoring alert

#### Long-term (Quarter)
- Evaluate ZGC for this workload
- Implement CRaC for faster startup after restarts
- Chaos engineering: GC stress testing in CI

---

## Incident 2: "The Virtual Thread Pinning Mystery"

### Symptom
```
Virtual thread count: 45,000 (expected: 500)
Carrier thread CPU: 95% (expected: 40%)
Thread dumps show: RUNNABLE in java.net.SocketInputStream.read
```

### Investigation

#### Task 1: Identify Pinning Sources
```bash
# JFR pinning events (Java 21+)
jfr print --events jdk.VirtualThreadPinned recording.jfr

# Or async-profiler
./profiler.sh -e wall -d 60 -f profile.html <pid>
```

#### Task 2: Code Analysis
```java
// PROBLEM: synchronized in virtual thread
@GetMapping("/accounts/{id}")
public Account getAccount(@PathVariable String id) {
    return accountService.getAccount(id); // synchronized inside!
}

// PROBLEM: Native call in virtual thread
public byte[] encrypt(byte[] data) {
    return nativeCrypto.encrypt(data); // JNI pins carrier
}

// PROBLEM: File I/O in virtual thread
public String readConfig() {
    return Files.readString(Path.of("config.yaml")); // blocking I/O
}
```

#### Task 3: Fix Validation
```java
// FIX 1: ReentrantLock instead of synchronized
private final Lock lock = new ReentrantLock();
public Account getAccount(String id) {
    lock.lock();
    try { return repo.find(id); } finally { lock.unlock(); }
}

// FIX 2: Offload native to platform thread pool
private final ExecutorService nativePool = Executors.newFixedThreadPool(8);
public CompletableFuture<byte[]> encryptAsync(byte[] data) {
    return CompletableFuture.supplyAsync(() -> nativeCrypto.encrypt(data), nativePool);
}

// FIX 3: Use NIO.2 async I/O
public CompletableFuture<String> readConfigAsync() {
    return CompletableFuture.supplyAsync(() -> {
        try { return Files.readString(Path.of("config.yaml")); }
        catch (IOException e) { throw new UncheckedIOException(e); }
    });
}
```

### Monitoring Dashboard
```promql
# Virtual thread pinning rate
rate(jvm_virtual_threads_pinned_total[5m])

# Carrier thread utilization
jvm_threads_states{state="RUNNABLE"} / jvm_threads_peak_threads

# Virtual thread count
jvm_threads_virtual_threads
```

---

## Incident 3: "The Metaspace Leak"

### Symptom
```
04:00:00 Metaspace: 1.2 GB / 1.5 GB (80%)
06:00:00 Metaspace: 1.4 GB / 1.5 GB (93%)
08:00:00 ALERT: Metaspace OOM - ClassLoader.defineClass failed
```

### Investigation

#### Task 1: Class Histogram Analysis
```bash
jcmd <pid> GC.class_histogram | head -30

# Expected output:
# 1. 50,000  com.example.generated.ReportGenerator$1 (dynamic proxies)
# 2. 30,000  com.example.generated.QueryExecutor$2 (bytecode generation)
# 3. 15,000  org.springframework.cglib.proxy.Enhancer$3 (Spring proxies)
```

#### Task 2: ClassLoader Leak Detection
```bash
# Find classloaders
jcmd <pid> GC.class_histogram | grep ClassLoader

# Check for unreachable classloaders
# Use Eclipse MAT: "Class Loader Explorer" → "Find Leaking Class Loaders"
```

#### Task 3: Root Cause
Dynamic report generation using **Janino** / **Spring Expression Language** creates new classes per request:
```java
// LEAK: New class per evaluation
ExpressionParser parser = new SpelExpressionParser();
Expression exp = parser.parseExpression(userInput);
Object result = exp.getValue(); // Generates class, ClassLoader never GC'd
```

### Resolution

#### Immediate
```bash
# Increase Metaspace (buy time)
-XX:MaxMetaspaceSize=2g
-XX:+ClassUnloadingWithConcurrentMark
```

#### Code Fix
```java
// Use compiled expressions (cached)
private final Map<String, Expression> expressionCache = new ConcurrentHashMap<>();

public Object evaluate(String expression, Object context) {
    Expression exp = expressionCache.computeIfAbsent(expression, 
        k -> parser.parseExpression(k));
    return exp.getValue(context);
}

// Or use interpreted mode
StandardEvaluationContext ctx = new StandardEvaluationContext();
ctx.setBeanResolver(new BeanFactoryResolver(beanFactory));
// No class generation
```

---

## Capacity Planning Exercise

### Current State
- 200 pods × 16 vCPU × 32 GB = 3,200 vCPU, 6.4 TB RAM
- Heap: 24 GB/pod = 4.8 TB total
- Current utilization: 65% CPU, 70% heap
- Growth: 15% MoM transaction volume

### 6-Month Projection

| Metric | Current | +6 Months | Required |
|--------|---------|-----------|----------|
| TPS | 50,000 | 115,000 | 2.3x |
| Heap/pod | 24 GB | 32 GB | +8 GB |
| Pods | 200 | 350 | +150 |
| vCPU | 3,200 | 5,600 | +2,400 |

### JVM Tuning for Scale

```bash
# Large heap optimizations
-XX:+UseZGC
-XX:+ZGenerational
-Xms32g -Xmx32g
-XX:ZCollectionInterval=20
-XX:ZAllocationSpikeTolerance=3.0

# Thread optimization
-XX:ActiveProcessorCount=16  # Container-aware
-Djdk.virtualThreadScheduler.parallelism=32

# Startup optimization
-XX:+UseContainerSupport
-XX:InitialRAMPercentage=75.0
-XX:MaxRAMPercentage=75.0

# CDS for faster startup
-XX:SharedArchiveFile=app.jsa
-Xshare:on
```

---

## Performance Engineering Playbook

### Daily
- [ ] Review GC dashboard (pause times, allocation rate, promotion rate)
- [ ] Check JFR continuous recordings for anomalies
- [ ] Verify virtual thread health (pinning rate < 1%)

### Weekly
- [ ] Analyze allocation profiles (top 10 allocation sites)
- [ ] Review lock contention hotspots
- [ ] Capacity planning update

### Monthly
- [ ] JVM upgrade evaluation (security + performance)
- [ ] GC algorithm benchmark (G1 vs ZGC vs Shenandoah)
- [ ] Chaos experiment: GC stress, OOM injection

### Quarterly
- [ ] JDK version upgrade (test in staging)
- [ ] Architecture review: JVM-aware design patterns
- [ ] Knowledge sharing: incident retrospectives

---

## Tooling Inventory

### Production
| Tool | Purpose | Frequency |
|------|---------|-----------|
| JFR (continuous) | Always-on profiling | 24/7 |
| async-profiler | On-demand CPU/alloc/lock | Incident |
| jcmd | Live diagnostics | Incident |
| GC logs (CloudWatch) | Long-term trends | Daily |
| Prometheus/Grafana | Metrics & alerting | Real-time |

### Development
| Tool | Purpose |
|------|---------|
| JMH | Microbenchmarks |
| JOL | Object layout |
| JFR + JMC | Deep analysis |
| JCStress | Concurrency testing |
| Chaos Mesh | Fault injection |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| GC Pause p99 | < 50ms | JFR / GC logs |
| Allocation Rate | < 500 MB/s/pod | JFR / Micrometer |
| Virtual Thread Pinning | < 0.1% | JFR / Custom metric |
| Metaspace Growth | < 10 MB/hour | jcmd / Prometheus |
| Code Cache Usage | < 70% | jcmd |
| Safepoint Frequency | < 1/sec | JFR |
| Startup Time (w/ CDS) | < 10s | Kubernetes probe |

---

## Knowledge Transfer

### Runbook Template
```markdown
## Incident: [Title]
### Symptoms
### Diagnosis Commands
### Root Cause
### Resolution
### Prevention
### Related Incidents
```

### Training Program
1. **JVM Fundamentals** (2 days) - Memory, GC, JIT
2. **Diagnostics Workshop** (1 day) - JFR, async-profiler, jcmd
3. **Incident Simulation** (4 hours) - Real scenarios
4. **Advanced Topics** (1 day) - ZGC, Virtual Threads, FFI

---

## Deliverables Checklist

- [ ] Incident 1: GC Storm - Full RCA document
- [ ] Incident 2: Virtual Thread Pinning - Fix + monitoring
- [ ] Incident 3: Metaspace Leak - Fix + prevention
- [ ] Capacity Plan - 6-month projection with JVM tuning
- [ ] Playbook - Daily/Weekly/Monthly/Quarterly tasks
- [ ] Runbooks - 3 incident-specific runbooks
- [ ] Dashboard - Grafana JVM internals dashboard
- [ ] Alerts - Prometheus rules for all key metrics
- [ ] Presentation - 30-min executive summary

---

## Evaluation Rubric

| Area | Weight | Criteria |
|------|--------|----------|
| Technical Depth | 30% | Correct root cause analysis, proper tool usage |
| Production Readiness | 25% | Actionable runbooks, monitoring, alerting |
| Communication | 20% | Clear RCA, stakeholder-appropriate detail |
| Prevention | 15% | Systemic fixes, not just workarounds |
| Innovation | 10% | Novel approaches, tooling improvements |