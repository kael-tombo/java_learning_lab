# VISION — Profiling & Observability (JFR, JMC, async-profiler)

## Vision Statement
**No guessing in prod** — continuous JFR + targeted async-profiler +
metrics/traces turn "slow" into a named frame, allocation site, and
lock with a flame graph attached.

---
## Mental Models
### 1. Always-On vs Deep-Dive
JFR (1–2% overhead) runs always; async-profiler (cpu/alloc/lock/wall)
answers specific questions; debuggers answer none in prod.
### 2. Four Profilers, Four Truths
CPU (what burns), allocation (what churns), lock (what waits), wall
(what the user feels). One view lies; four agree.
### 3. Events Beat Logs
`jdk.ObjectAllocation`, `JavaMonitorEnter`, `SocketRead`,
`Compilation` are structured, sampled, and cheap — grep is last resort.
### 4. Cardinality Kills Dashboards
Tag with service/version/az/endpoint; never user-id. Histograms +
exemplars, not averages.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Slow endpoint? | Wall + CPU flame first, then alloc |
| GC pressure? | Alloc flame + TLAB events, not heap size |
| Stalls no CPU? | Lock/wall + Thread.print + monitor events |
| In prod always? | JFR continuous + alerts on top frames |

---
## Career Trajectory
- **L1:** JFR record + JMC open, flame-graph reading.
- **L2:** async-profiler modes, Micrometer/Prometheus wiring.
- **L3:** Continuous profiling, tail-latency attribution, SLO linkage.
- **L4:** Org observability standards, sampling budgets, incident science.

---
## 4-Week Path
```
W1: JFR + JMC kata — record, open, rank hottest events/stacks.
W2: async-profiler quad (cpu/alloc/lock/wall) on one service.
W3: Metrics + traces — RED/USE dashboards, exemplar linkage.
W4: Continuous-profiling pilot + slow-endpoint postmortem with proof.
```
## Success Metrics
- [ ] Attribute any p99 regression to frame/site/lock in <30 min
- [ ] JFR continuous on with <2% overhead measured
- [ ] Dashboards: RED per endpoint + JVM (GC/threads/pools)
- [ ] One incident closed with flame + event evidence

## What This Is Not
Dashboard wallpaper. Every chart must answer "so what do we change."

> Mantra: **Profile in production, decide with flames.**
