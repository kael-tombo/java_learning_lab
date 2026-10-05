# VISION — JVM Internals

## Vision Statement

**Master the JVM from the metal up** — understand not just *how* to tune the JVM, but *why* it behaves the way it does, by connecting observable behavior to source-code-level implementation.

---

## Learning Philosophy

### From Symptoms to Root Cause

```
Symptom: "High CPU" 
    ↓
Profile: async-profiler shows 40% in `Thread.sleep`
    ↓
Insight: Park/unpark syscalls, safepoint polling, or spin loops
    ↓
Root Cause: Biased locking contention, safepoint storms, or busy-wait
    ↓
Fix: `-XX:-UseBiasedLocking`, larger TLABs, or algorithmic change
```

### From Configuration to Mechanism

```
Flag: -XX:+UseZGC
    ↓
Mechanism: Colored pointers + load/store barriers + concurrent relocation
    ↓
Trade-off: <1ms pauses, but 10-15% throughput cost, no compressed OOPs
    ↓
Decision: Use when latency > throughput, heap > 4GB, allocation rate high
```

---

## Mental Models to Build

### 1. The Memory Hierarchy Model

```
L1 Cache (64B line, 4 cycles) ←→ L2 (12 cycles) ←→ L3 (40 cycles) ←→ DRAM (100+ cycles)
                    ↑
         Object layout determines cache behavior
         False sharing = 50-300 cycles per bounce
         Prefetching works on sequential access
```

### 2. The Compilation Pipeline Model

```
Bytecode → Interpreter (profiling) → C1 (simple opts) → C2 (aggressive opts)
              ↑                        ↑                    ↑
         Tier 0                   Tier 1-2             Tier 3-4
         Counter: 1K             Counter: 5K           Counter: 10K
         No inlining             Inlining < 35B        Full inlining
         No escape analysis      Basic EA              Full EA + scalar replace
```

### 3. The GC Generational Model

```
Young Gen (Eden + S0 + S1)          Old Gen
     ↑                                    ↑
  Copying GC                         Mark-Compact / Concurrent
  ~ms pauses                         ~ms to s pauses
  High allocation rate               Long-lived objects
  TLABs for fast alloc               Humongous objects
```

### 4. The Synchronization Model

```
Unlocked → Lightweight (CAS on stack) → Heavyweight (ObjectMonitor)
    ↑              ↑                        ↑
  Biased          Fast path              wait/notify
  (deprecated)    No contention          OS mutex/futex
```

---

## Architectural Decision Framework

### When to Choose Which GC

| Requirement | Recommended | Reasoning |
|-------------|-------------|-----------|
| Max throughput, batch | Parallel | No concurrent overhead |
| Low latency, < 4GB heap | G1 | Balanced, generational |
| Low latency, > 4GB heap | ZGC | Concurrent, scalable |
| Ultra-low latency, huge heap | Shenandoah | Concurrent, no load barriers |
| Predictable pauses | ZGC/Shenandoah | Bounded worst-case |

### When to Tune What

| Symptom | First Tuning Target |
|---------|---------------------|
| Frequent young GC | Increase Eden (`-XX:NewRatio`, `-XX:SurvivorRatio`) |
| Long old GC pauses | Switch collector (G1→ZGC), increase heap |
| High allocation rate | Larger TLABs, escape analysis, object pooling |
| Safepoint storms | Reduce thread count, check JNI, `-XX:+UseCountedLoopSafepoints` |
| Code cache full | Increase `-XX:ReservedCodeCacheSize` |
| Metaspace OOM | Fix classloader leak, increase `-XX:MaxMetaspaceSize` |

---

## Career Trajectory

### Level 1: Operator (0-2 years)
- Run applications, read GC logs
- Adjust heap size, basic GC flags
- Use VisualVM/JConsole

### Level 2: Tuner (2-5 years)
- Profile with async-profiler/JFR
- Understand tiered compilation
- Tune GC for specific workloads
- Diagnose safepoint issues

### Level 3: Internals Expert (5-10 years)
- Read HotSpot source for root cause
- Custom JFR events, JDK patches
- Contribute to OpenJDK
- Design JVM-aware architectures

### Level 4: Platform Architect (10+ years)
- Influence JVM roadmap
- Build custom runtimes (GraalVM, CRaC)
- Define organizational JVM standards
- Cross-language runtime integration

---

## Technology Evolution Radar

### Current (Java 21 LTS)
- ✅ Virtual threads (mainstream)
- ✅ Generational ZGC (preview)
- ✅ Foreign Function & Memory API (final)
- ✅ String templates (preview)

### Near Future (Java 22-24)
- 🔄 Structured concurrency (final)
- 🔄 Stream gatherers (preview)
- 🔄 Module import declarations (preview)
- 🔄 Vector API (6th incubating)

### Horizon (Java 25 LTS+)
- 🔮 Project Leyden (AOT, CDS improvements)
- 🔮 Project Babylon (GPU/accelerator)
- 🔮 Project Valhalla (value types, primitive classes)
- 🔮 Project Loom continuations (beyond virtual threads)

---

## Skills Matrix

| Skill | Beginner | Intermediate | Advanced | Expert |
|-------|----------|--------------|----------|--------|
| GC Log Analysis | Read basic logs | Correlate with app metrics | Predict GC behavior | Design custom GC policies |
| Profiling | Run async-profiler | Interpret flame graphs | JFR event programming | eBPF/perf integration |
| JIT Understanding | Know tiers exist | Explain inlining/EA | Read C2 IR graphs | Modify compiler heuristics |
| Memory Layout | Know header exists | Calculate object size | Detect false sharing | Design cache-friendly DS |
| Synchronization | Use ReentrantLock | Understand lock inflation | Diagnose park/unpark | Implement custom synchronizers |
| Class Loading | Fix ClassNotFound | Module system | Custom classloaders | Module layer architecture |
| Diagnostics | jstack, jmap | jcmd, JFR, NMT | HotSpot source diving | JVM crash analysis (hs_err) |

---

## Learning Path Recommendation

```
Month 1-2:  Fundamentals (THEORY + EXERCISES)
    - Object layout, memory areas, GC basics
    - Run exercises with JOL, jstat, jcmd

Month 3-4:  JIT & Compilation (CODE_DEEP_DIVE)
    - Tiered compilation, inlining, escape analysis
    - PrintCompilation, PrintInlining, PrintEscapeAnalysis

Month 5-6:  Advanced GC (MATH_FOUNDATION + REAL_WORLD)
    - G1/ZGC internals, queueing theory
    - Production GC tuning case studies

Month 7-8:  Concurrency & Synchronization (MINI_PROJECT)
    - Lock inflation, biased locking, virtual threads
    - Build custom synchronizer, benchmark

Month 9-10: Diagnostics & Production (REAL_WORLD_PROJECT)
    - JFR, async-profiler, hs_err analysis
    - Incident response simulations

Month 11-12: Mastery (VISION + CONTRIBUTION)
    - Read HotSpot source weekly
    - File JDK bugs, contribute fixes
    - Mentor others
```

---

## Success Metrics

You've mastered JVM Internals when you can:

- [ ] Explain any GC log line in terms of source code
- [ ] Predict compilation behavior from bytecode patterns
- [ ] Diagnose a production incident using only `jcmd` and `jstack`
- [ ] Design a data structure that avoids false sharing without `@Contended`
- [ ] Choose and defend a GC algorithm for a new service
- [ ] Write a JFR event to capture a custom application metric
- [ ] Read and understand a HotSpot C++ source file in 15 minutes
- [ ] Teach these concepts to a junior engineer effectively