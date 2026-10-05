# VISION — Garbage Collection Deep Dive

## Vision Statement
**Pauses are a budget, not a surprise** — choose G1/ZGC/Shenandoah by
measured pause/throughput/footprint, then prove the choice with logs,
JFR, and heap-after-GC math under real allocation pressure.

---
## Mental Models
### 1. Trilemma: Latency × Throughput × Footprint
Sub-10ms (ZGC) costs CPU/footprint; G1 balances; Parallel maximizes
throughput. No collector wins all three.
### 2. Generations + Regions
Eden/survivor/old (G1 regions/humongous) explain promotion failure
and mixed-GC timing. `Xlog:gc*` narrates every phase.
### 3. Safepoints & Barriers
STW pauses, load/store barriers (colored pointers in ZGC/Shenandoah)
are the real pause tax. JFR `GarbageCollection` + `Safepoint` split it.
### 4. Allocation Rate Rules All
GB/s allocated + promotion rate predict GC fate better than heap
size. Fix churn (boxing, giant arrays) before flag-tuning.

---
## Decision Framework
| Question | Rule |
|----------|------|
| p99 <10ms, heap >8GB? | ZGC (generational) |
| Balanced service 2–8GB? | G1, pause goal 100–200ms |
| Max batch throughput? | Parallel GC |
| Humongous allocs? | Split/pool; watch G1 humongous |

---
## Career Trajectory
- **L1:** Generations, `-Xlog:gc*`, heap dumps, promotion basics.
- **L2:** G1 regions/phases, ZGC/Shenandoah selection, JFR GC events.
- **L3:** Allocation profiling, weak/soft/phantom discipline, NMT.
- **L4:** Fleet GC policy, pause budgets per tier, capacity models.

---
## 4-Week Path
```
W1: GC log reading (G1 vs ZGC) + JFR GarbageCollection drill.
W2: Allocation profiler — kill top 3 churn sources (boxing/dup strings).
W3: Collector bake-off on same workload; pause/throughput table.
W4: Production-grade GC runbook (flags, alerts, heap-sizing math).
```
## Success Metrics
- [ ] Read an `Xlog:gc*` pause chain and name the phase
- [ ] Allocation rate cut with profiler proof
- [ ] Bake-off table with p50/p99/max pause + CPU overhead
- [ ] Runbook: flags + alerts + rollback for one service

## What This Is Not
Flag bingo. Most GC wins are allocation wins.

> Mantra: **Measure allocation first, tune collectors second.**
