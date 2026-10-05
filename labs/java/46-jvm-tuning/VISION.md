# VISION — JVM Tuning & Optimization

## Vision Statement
**Flags follow facts** — heap, collectors, and container limits tuned
from GC logs, JFR, and NMT — never copied from a blog — so the JVM
fits its cgroup and meets its SLO with headroom to spare.

---
## Mental Models
### 1. Container Is the Machine
cgroup `memory.max` + `cpu.max` define reality. `UseContainerSupport`
+ `MaxRAMPercentage` translate it; `Xmx` hard-codes ignore it at peril.
### 2. Heap Sizing Is Arithmetic
Live-set × 3–4 + headroom for spikes + metaspace/NMT/direct. Heap
after full GC is the anchor, not the limit.
### 3. Every Flag Has a Bill
Throughput/CPU/footprint tradeoffs are conservation laws. A pause
fix that doubles CPU is a capacity purchase.
### 4. Baseline → Change → Diff
One variable per experiment, same seed/load, JFR + gc.log diff.
Otherwise tuning is superstition.

---
## Decision Framework
| Question | Rule |
|----------|------|
| OOMKilled but heap free? | NMT + direct/metaspace, lower Xmx % |
| Long pauses? | Collector + allocation fix before heap grow |
| CPU throttle? | Quota vs usage; trim threads/GC workers |
| Which first? | Size heap → pick collector → trim alloc → flags |

---
## Career Trajectory
- **L1:** Xms/Xmx, container flags, gc.log reading.
- **L2:** G1/ZGC selection, thread-stack math, NMT basics.
- **L3:** Full tuning loop (JFR + bake-off + runbook), CDS/startup.
- **L4:** Fleet right-sizing, SLO-based capacity, cost governance.

---
## 4-Week Path
```
W1: Container math lab — NMT + heap_info vs cgroup limits.
W2: GC-log-driven heap sizing on a leaky-ish service.
W3: Collector + thread + code-cache experiment matrix.
W4: Tuning runbook + dashboard + rollback drill for one service.
```
## Success Metrics
- [ ] Heap sized from measured live-set (math shown)
- [ ] Zero OOMKills 30d with 40% headroom at p99 load
- [ ] One-variable experiments with JFR diffs archived
- [ ] Runbook: flags + alerts + rollback tested

## What This Is Not
A golden flags list. It is a repeatable sizing method.

> Mantra: **Fit the cgroup, fund the pause, prove the diff.**
