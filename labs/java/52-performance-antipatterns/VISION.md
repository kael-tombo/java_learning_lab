# VISION — Performance Antipatterns & Debugging

## Vision Statement
**Speed is the absence of waste** — N+1s, boxing, string churn, and
chatty I/O are line items on a budget: find them with a profiler,
price them in ms and MB/s, delete them with prejudice.

---
## Mental Models
### 1. Budget Every Millisecond
p99 = sum of stages. Attribute first (flame + trace), then optimize
the biggest bar — never the most interesting code.
### 2. Allocations Are Latency Later
Boxing, `String.format` in loops, regex recompile, copying streams:
JFR TLAB events convert style into GB/s.
### 3. Round Trips Dominate
N+1, unbatched RPCs, row-by-row JDBC, missing cache: count calls per
request before touching algorithms.
### 4. Cleverness Is Overhead
Reflection-per-call, synchronized logging, exceptions-as-control-flow,
regex-for-equals — each has a profiler signature. Learn the shapes.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Slow? | Calls/request + flame + alloc, in that order |
| Fix what? | Biggest bar with cheapest fix first |
| Cache? | Bound + TTL + invalidation test, else a leak |
| Prove it? | Before/after JFR + load numbers or it didn't happen |

---
## Career Trajectory
- **L1:** N+1, string/boxing basics, log-cost awareness.
- **L2:** JDBC batching, cache discipline, regex/parse hygiene.
- **L3:** Alloc-rate budgets, tail-latency attribution, perf CI gates.
- **L4:** Org antipattern lint + perf budgets per endpoint.

---
## 4-Week Path
```
W1: Rogues' gallery kata — fix 10 planted antipatterns with proof.
W2: Call-count audit — batch the N+1s, cache the hot reads.
W3: Alloc-rate sprint — cut MB/s 50%+ on one endpoint.
W4: Perf-gate install — JMH + alloc + call-count checks in CI.
```
## Success Metrics
- [ ] Name the top-3 antipatterns from any flame in 10 min
- [ ] Calls/request cut with trace proof on one endpoint
- [ ] Alloc rate halved with JFR proof
- [ ] CI fails on N+1/alloc regression

## What This Is Not
Premature optimization. Measure, then delete waste — in that order.

> Mantra: **Count calls, weigh bytes, flame everything.**
