# VISION — Lab 15: Performance Engineering & Load Testing

> From "the service feels slow" to "here is the bottleneck, the fix, and the projected capacity after it."

---

## The Arc

1. **Estimation before measurement** — Little's Law, queueing intuition, the utilization knee, and Amdahl.
2. **Test methodology** — open vs closed loop, coordinated omission, ramp profiles, warm-up policy, repetition.
3. **Environment fidelity** — matching utilisation ratios on every resource, realistic data, network shaping, stubbing at the boundary.
4. **Finding the saturation point** — the throughput plateau, which resource plateaus, and headroom policy.
5. **CPU-bound vs I/O-bound** — concurrency as the discriminator, and pool sizing from measured service time.
6. **Profiling under load** — async-profiler and JFR, reading flame graphs, and knowing what a JVM profile cannot see.
7. **The dependency problem** — database plans, N+1, pool saturation, lock waits; usually the real bottleneck.
8. **JVM performance** — allocation rate as the first lever, collector selection, and why the mean hides pauses.
9. **Test types beyond load** — stress, soak, spike; leaks and drift.
10. **Delivering the result** — report format, statistical honesty, CI perf gates, and the fix as a cost argument.

---

## Why this lab exists

Performance is where engineering is most often done by intuition, and where the measurement is most often wrong in a way that hides the answer. Closed-loop generators report beautiful percentiles for services that are timing out; environment mismatch hides bottlenecks that only appear in production.

The specific goal here: **you can size a service from first principles, verify with a methodologically sound test, find the bottleneck with evidence, and quantify the capacity and cost impact of the fix.**

---

## Milestones (checkable)

- [ ] M1: Compute a service's safe capacity from Little's Law, queueing, and a measured utilization target — before running a test.
- [ ] M2: Build a load test that is open-loop (arrival-rate), warm, repeated three times, and reports the full distribution plus coordinated-omission-safe latency.
- [ ] M3: Demonstrate coordinated omission on a stalled service and show a closed-loop tool reporting a good p99 while the service is failing.
- [ ] M4: Find the saturation point by ramping, identify which resource plateaus, and derive headroom policy from the knee.
- [ ] M5: Profile under load with async-profiler and JFR, identify the bottleneck, and show the fix's effect on throughput, p99, and CPU-per-request.
- [ ] M6: Find a real N+1 or unindexed query in a service and quantify the DB-load reduction.
- [ ] M7: Produce a performance report with the bottleneck, the fix, the projected capacity, and a CI perf gate.

---

## Anti-Goals

- Trusting a closed-loop tool's percentiles.
- Matching request rate but not utilisation ratios.
- Profiling on an idle system only.
- Optimising a 5% fraction of a request path.
- Sizing a pool larger than the dependency's capacity.
- Reporting a mean latency, or a single run.
- Claiming an improvement smaller than the run-to-run spread.
- Treating the database as "someone else's problem".
- Adding GC flags before measuring allocation rate.
- A performance report with no bottleneck named.

---

## Interview Lens

- "How do you know where the bottleneck is?"
- "What is coordinated omission and how do you avoid it?"
- "A service is slow at peak. Walk me through your first hour."
- "How do you size a thread pool?"
- "How do you know a load test is trustworthy?"

---

## 30-Day Plan

- **Week 1** — THEORY + `PROJECT_PANAMA_ZERO_GC`: Little's Law, queueing, test methodology; hands-on with a load generator and an open-loop profile. M1–M3.
- **Week 2** — EXERCISES: saturation math, pool sizing, N+1 arithmetic, statistical honesty; QUIZ to 13/15; FLASHCARDS daily. M4.
- **Week 3** — MINI_PROJECT: profile a real service under load, find and fix the bottleneck, publish the report. M5–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a capacity model for a real service; teach-back: "our bottleneck and our headroom, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A capacity model: `λ_peak`, utilization target, `L`, safe capacity, replicas with failure tolerance.
2. A load test whose methodology is defensible (profile, warm-up, runs, environment ratio table).
3. A saturation curve with the knee marked and the limiting resource named.
4. A flame graph / allocation profile that identifies the bottleneck, with the fix's before/after.
5. A performance report including the cost of the fix.

---

## Done = You Can

- Say whether a test result can be trusted, and why.
- Find the bottleneck with evidence rather than intuition.
- Compute safe capacity and explain the headroom policy.
- Quantify a fix in throughput, latency, and dollars.
