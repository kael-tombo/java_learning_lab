# VISION — JVM Internals

## Vision Statement
**The JVM is an observable machine, not magic** — read classloading, JIT,
and GC as first-class inputs so you size heaps, tame pauses, and diagnose
prod with `jcmd` + JFR instead of guessing flags.

---

## Mental Models
### 1. Load → Verify → Link → Init
Classloaders delegate parent-first; leaks come from holding loaders (hot
redeploys). `NoClassDefFoundError` = present at compile, absent at runtime.
### 2. JIT Rewards Hot, Stable Shapes
C1 then C2 compile hot methods; inlining + monomorphic calls win.
Megamorphic/interface storms and huge methods deopt — keep hot paths small.
### 3. GC Trades Throughput for Pauses
G1/ZGC/Shenandoah differ on pause goals; heap = Eden + Survivor + Old +
Metaspace + off-heap. Size to live-set, not traffic; watch promotion rate.
### 4. Everything Emits Events
JFR (`jdk.GCHeapSummary`, `jdk.Compilation`, `jdk.ClassLoading`) + `jcmd`
(`GC.heap_dump`, `Thread.print`, `VM.flags`) make prod legible without
agents.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Which GC? | Latency SLO -> ZGC/Shenandoah; throughput -> G1/Parallel |
| Heap size? | 2–3x live set; cap containers (`-XX:MaxRAMPercentage`) |
| Slow warmup? | TieredCompilation + warmup traffic, not disabled JIT |
| Leak or churn? | Heap dump + JFR alloc: growth = leak, churn = GC load |
| Which flags? | Measure with JFR; never copy-paste flag soup |

---

## Career Trajectory
- **L1:** Heap/stack, `jcmd`, JFR basics, read a GC log.
- **L2:** GC selection + sizing, JIT logs, classloader debugging.
- **L3:** Pause tuning, allocation profiling, container-aware config.
- **L4:** Fleet-wide runtime policy (images, flags, upgrade trains).

---

## 4-Week Path
```
W1: Classloading, heap layout, jcmd (Thread.print, heap_dump).
W2: JIT tiers, -Xlog:jit, warmup experiments.
W3: G1 vs ZGC labs, GC-log reading, heap sizing kata.
W4: JFR-driven tuning capstone (pause + alloc memo).
```
## Success Metrics
- [ ] Diagnose OOM/pause from JFR + heap dump unaided
- [ ] Justify GC + heap flags with numbers
- [ ] jcmd fluency: 5 commands from memory
