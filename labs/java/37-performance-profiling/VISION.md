# VISION — Performance Profiling (JMH, JFR, async-profiler)

## Vision Statement
**Performance is measured, not intuited** — profile wall/CPU/alloc/lock in
prod-like conditions, fix the top frame, and lock the gain with a benchmark
gate so regressions page before customers feel them.

---

## Mental Models
### 1. Profile Before Optimizing
Flame graphs (CPU/wall/alloc) name the top frame; intuition names the wrong
one. `async-profiler` + JFR beat `System.nanoTime` spot-checks.
### 2. Three Costs, Three Views
CPU (hot methods), allocation (GC pressure), lock (contention). A "slow"
endpoint is often alloc+lock, not CPU — check all three views.
### 3. JMH or It Didn't Happen
Microbenchmarks need warmup, forks, blackholes; loop-DCE and dead-code make
naive timers lies. Macro (k6/Gatling) proves user impact.
### 4. Baselines Are Code
`main` vs PR bench diff in CI; JFR `profile` recording per release; heap +
GC-log artifacts make regressions bisectable.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Slow endpoint? | Wall flame first, then CPU/alloc/lock split |
| Optimize what? | Top frame only; 80/20, re-profile after |
| Micro-opt claim? | JMH with forks + CI gate, not one laptop run |
| Cache it? | Measure hit rate + invalidation cost first |
| Ship it? | Macro p99 + alloc delta within budget |

---

## Career Trajectory
- **L1:** JFR recordings, async-profiler flames, read top frames.
- **L2:** JMH harness, alloc/lock profiling, GC-log correlation.
- **L3:** Perf gates in CI, capacity modeling, tail-latency analysis.
- **L4:** Org perf strategy (budgets, SLOs, profiling platform).

---

## 4-Week Path
```
W1: JFR + async-profiler, flame-graph reading, top-frame drill.
W2: JMH anatomy (warmup/forks/blackhole), benchmark 3 string idioms.
W3: Alloc + lock profiling, contented-map fix kata.
W4: API p99 capstone (profile → fix → gate).
```
## Success Metrics
- [ ] Top frame named from flame, not guessed
- [ ] JMH + macro numbers agree on the win
- [ ] CI bench gate blocks a planted regression
