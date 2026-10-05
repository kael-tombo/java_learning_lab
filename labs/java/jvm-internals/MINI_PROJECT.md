# MINI_PROJECT — JVM Internals

## Project: JVM Diagnostic Toolkit

Build a comprehensive diagnostic toolkit that demonstrates deep JVM internals knowledge.

---

## Project Overview

**Duration:** 2-3 weeks (part-time)
**Complexity:** Advanced
**Prerequisites:** Complete THEORY, EXERCISES, CODE_DEEP_DIVE

---

## Deliverables

### 1. Object Layout Analyzer (`jol-analyzer`)
A CLI tool that visualizes object memory layout with annotations.

```bash
$ jol-analyzer com.example.MyClass
┌─────────────────────────────────────────────────────────────┐
│ com.example.MyClass (size: 32 bytes)                         │
├──────────────┬────────┬──────────────────────────────────────┤
│ Offset       │ Size   │ Field                                │
├──────────────┼────────┼──────────────────────────────────────┤
│ 0            │ 8      │ [HEADER] Mark Word                   │
│ 8            │ 4      │ [HEADER] Klass Pointer (compressed)  │
│ 12           │ 4      │ [PADDING]                            │
│ 16           │ 8      │ long id                              │
│ 24           │ 4      │ int status                           │
│ 28           │ 4      │ [PADDING]                            │
└──────────────┴────────┴──────────────────────────────────────┘
Instance size: 32 bytes (aligned to 8 bytes)
Fields: 2 (16 bytes data, 8 bytes padding = 66% efficiency)
```

**Requirements:**
- Parse class file using ASM or reflection
- Calculate field offsets per JVM spec
- Show padding and alignment
- Detect false sharing risk (fields near 64-byte boundaries)
- Support arrays, inheritance, compressed/uncompressed OOPs

---

### 2. Lock State Visualizer (`lock-viz`)
Real-time visualization of lock inflation states.

```bash
$ lock-viz --pid 12345 --duration 60s
[████████░░] Biased:     45% (2,341 locks)
[████░░░░░░] Lightweight: 22% (1,156 locks)
[██░░░░░░░░] Heavyweight: 11% (567 locks)
[░░░░░░░░░░] Unlocked:   22% (1,123 locks)

Inflation Events: 234
  Biased → Lightweight: 156
  Lightweight → Heavyweight: 78
Contention Hotspots:
  1. com.example.Cache.get() - 89 inflations
  2. com.example.Counter.increment() - 67 inflations
```

**Requirements:**
- Attach to running JVM via JVMTI or jcmd
- Sample lock states via JFR events (`jdk.JavaMonitorEnter`, `jdk.JavaMonitorWait`)
- Track inflation transitions
- Identify contention hotspots with stack traces
- Export to JSON for dashboarding

---

### 3. Safepoint Latency Analyzer (`safepoint-analyzer`)
Analyze safepoint logs and JFR recordings for latency outliers.

```bash
$ safepoint-analyzer gc.log --format unified
=== Safepoint Analysis ===
Total Safepoints: 1,247
Total Pause Time: 2.34s (0.23% of runtime)
Max Pause: 245ms at 2024-01-15 10:23:45.123
P99 Pause: 45ms
P99.9 Pause: 180ms

Top 5 Longest Safepoints:
1. 245ms - GC Pause (Young) - 1,203 threads blocked
2. 180ms - Thread Dump - 1,198 threads blocked  
3. 156ms - Deoptimization - 1,201 threads blocked
4. 98ms  - JFR Checkpoint - 1,199 threads blocked
5. 87ms  - Class Redefinition - 1,195 threads blocked

Thread Time-to-Safepoint (p99):
  Thread-42 (JNI): 230ms
  Thread-15 (Compiler): 45ms
  Thread-7 (GC): 12ms
```

**Requirements:**
- Parse unified GC logs (`-Xlog:safepoint*=info`)
- Parse JFR safepoint events (`jdk.SafepointBegin`, `jdk.SafepointEnd`)
- Correlate with thread states
- Identify threads consistently late to safepoint
- Generate HTML report with charts

---

### 4. Code Cache Monitor (`codecache-monitor`)
Monitor JIT compilation activity and code cache health.

```bash
$ codecache-monitor --pid 12345 --interval 5s
=== Code Cache Status ===
Reserved: 256 MB | Used: 187 MB (73%) | Free: 69 MB
Compilation Rate: 42 methods/sec
Tier Distribution:
  Tier 0 (Interpreter): 12%
  Tier 1 (C1): 28%
  Tier 2 (C1+Profile): 15%
  Tier 3 (C2): 35%
  Tier 4 (C2+Profile): 10%

Hot Methods (compiled this minute):
  1. com.example.Processor.process - Tier 3 - 2.3 KB
  2. java.util.HashMap.get - Tier 3 - 1.1 KB
  3. com.example.Validator.validate - Tier 1 - 0.8 KB

Deoptimization Events: 23 (last hour)
  Uncommon Trap: 18
  Class Load: 3
  OSR: 2
```

**Requirements:**
- Use `jcmd Compiler.codecache` or JFR compilation events
- Track tier transitions
- Alert on code cache > 90% usage
- Identify megamorphic call sites (via `jdk.InlineCache` events)
- Export Prometheus metrics

---

## Technical Requirements

### Core Libraries
```xml
<!-- pom.xml -->
<dependencies>
    <!-- JOL for object layout -->
    <dependency>
        <groupId>org.openjdk.jol</groupId>
        <artifactId>jol-core</artifactId>
        <version>0.16</version>
    </dependency>
    
    <!-- JFR parsing -->
    <dependency>
        <groupId>org.openjdk.jmc</groupId>
        <artifactId>jfr</artifactId>
        <version>8.3.0</version>
    </dependency>
    
    <!-- JVMTI attachment -->
    <dependency>
        <groupId>com.sun</groupId>
        <artifactId>tools</artifactId>
        <version>${java.version}</version>
        <scope>system</scope>
        <systemPath>${java.home}/../lib/tools.jar</systemPath>
    </dependency>
    
    <!-- JSON -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.15.0</version>
    </dependency>
    
    <!-- CLI -->
    <dependency>
        <groupId>picocli</groupId>
        <artifactId>picocli</artifactId>
        <version>4.7.0</version>
    </dependency>
</dependencies>
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up project structure (multi-module Maven/Gradle)
- [ ] Implement JOL-based object layout analyzer
- [ ] Add unit tests with known class layouts
- [ ] CLI with picocli

### Phase 2: Runtime Analysis (Week 2)
- [ ] JFR parsing for lock/safepoint/compilation events
- [ ] JVMTI attachment for live sampling
- [ ] Correlation engine (correlate locks with stacks)

### Phase 3: Visualization (Week 2-3)
- [ ] Terminal UI with charts (using `jansi` or `lanterna`)
- [ ] HTML report generation (Thymeleaf/FreeMarker)
- [ ] Prometheus/Grafana export

### Phase 4: Polish (Week 3)
- [ ] Integration tests with testcontainers
- [ ] Documentation and examples
- [ ] Performance optimization
- [ ] Release packaging (native image with GraalVM)

---

## Evaluation Criteria

| Criterion | Weight | Excellent (5) | Good (3) | Needs Work (1) |
|-----------|--------|---------------|----------|----------------|
| Technical Accuracy | 30% | Correctly implements JVM specs | Minor spec deviations | Major misunderstandings |
| Code Quality | 20% | Clean, tested, documented | Functional but messy | Buggy, untested |
| JVM Internals Depth | 25% | Uses advanced internals (JVMTI, JFR, HotSpot source) | Basic JMX/jcmd only | Only high-level APIs |
| Usability | 15% | Great CLI, clear output, good docs | Usable but rough | Hard to use |
| Innovation | 10% | Novel analysis/visualization | Standard features | Copy of existing tools |

---

## Stretch Goals

1. **GraalVM Native Image** - Compile toolkit itself to native image
2. **eBPF Integration** - Kernel-level profiling via `bcc`/`bpftrace`
3. **Real-time Dashboard** - WebSocket + React frontend
4. **JDK Patch** - Submit a bug fix to OpenJDK based on findings
5. **ML Anomaly Detection** - Train model on GC/safepoint patterns

---

## Learning Outcomes

Upon completion, you will have:

- [ ] Implemented object layout calculation from JVM spec
- [ ] Parsed and analyzed JFR event streams
- [ ] Used JVMTI for live JVM introspection
- [ ] Correlated multiple diagnostic data sources
- [ ] Built production-grade CLI tooling
- [ ] Deepened understanding of HotSpot internals
- [ ] Created portfolio project demonstrating expertise