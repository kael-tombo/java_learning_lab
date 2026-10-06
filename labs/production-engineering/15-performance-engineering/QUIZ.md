# Lab 15: Performance Engineering & Load Testing & QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. Little's Law: what does `L = λ × W` actually tell you, and what does it not?**
- A) That a slow system has many users
- B) In a stable system, the number of requests in flight equals arrival rate × time spent. It lets you convert latency into concurrency, size pools and thread counts, and reason about what happens when latency rises — and it is invalid during a transient or when arrival rate is not independent of service time
- C) That throughput is proportional to latency
- D) That the system is stable

**Answer: B** — The classic failure mode is applying it during overload, where latency and arrival rate are coupled (the system slows, requests pile up, arrival rate effectively rises), which is why the formula's predictions break exactly when you need them.

---

**Q2. Why must a load test model the arrival process, not just the request rate?**
- A) Because tools require it
- B) A constant arrival rate hides queueing (closed-loop testing lets concurrency collapse when latency rises, so you never see the queue); a bursty or ramped profile reveals saturation, and a closed loop measures service time rather than the system under load
- C) Because HTTP is stateful
- D) To test correctness

**Answer: B** — Open-loop (constant arrival) testing is the honest one. Closed-loop testing with N users measures "how fast N users finish", which understates the queue and overstates stability.

---

**Q3. What is the difference between a latency SLO at the mean and at p99, and why does the load test need the tail?**
- A) Means are enough
- B) Averages hide the queue: latency is highly skewed, and p99/p999 is where saturation shows first. A test that passes on the mean can be failing users by 20×
- C) p99 is easier to measure
- D) Means are cheaper

**Answer: B** — Also: p99 of a *closed-loop* test is a property of the load generator's concurrency, not of your service's offered load. Measure the distribution, not a summary.

---

**Q4. What is coordinated omission, and why does it make latency look better than it is?**
- A) A JMeter configuration error
- B) The load generator stops sending while it waits, so the requests it *should* have sent during a stall are never recorded; measured percentiles then exclude exactly the slow period. The fix is to measure the latency from *intended* send time, or to use an open-loop generator that records scheduled-vs-actual
- C) A JVM effect
- D) Network buffering

**Answer: B** — This is why a benchmark reporting p99 can show 5 ms while users report timeouts: the generator silently absorbed the stall.

---

**Q5. Why must the test environment match production's ratios, not just its throughput?**
- A) It does not need to
- B) CPU-per-request, memory-per-request, connection counts, and payload sizes determine the bottleneck; matching only request rate on much stronger hardware produces a test that passes and a system that fails. Match the ratio `offered load : capacity` to production
- C) For cost reasons
- D) Only database size matters

**Answer: B** — Include realistic data volumes (indexes only help if the indexes exist), realistic cache hit ratios, and realistic concurrency per user.

---

**Q6. What does a saturation point look like in the data?**
- A) Latency increases while throughput increases
- B) Throughput stops increasing (or starts decreasing) while latency rises non-linearly, queue depth grows, and utilization approaches 100%. Beyond it, adding load reduces completed work
- C) CPU hits 100% with no latency change
- D) Errors appear immediately

**Answer: B** — CPU hitting 100% is a symptom; the *throughput plateau with rising latency* is the definition. Record both, and identify which resource plateaus first.

---

**Q7. How do you tell a CPU-bound service from an I/O-bound one?**
- A) By CPU percentage
- B) By the relationship between concurrency and throughput: CPU-bound services stop gaining throughput as concurrency rises and CPU saturates; I/O-bound services keep gaining until the bottleneck (pool, connection, lock, or downstream) saturates while CPU stays low. Profile under load to confirm
- C) By heap size
- D) By response time

**Answer: B** — The practical discriminator is whether adding threads helps. If more concurrency does not increase throughput, you are bound by CPU or a serialized resource.

---

**Q8. Why does a micro-benchmark mislead about tail latency?**
- A) It is too fast
- B) A micro-benchmark runs in isolation with a hot cache, a single thread, and no contention, so it measures the median code path while omitting lock contention, GC pauses, page faults, and scheduling delay — all of which dominate p999
- C) It measures the wrong unit
- D) It ignores I/O

**Answer: B** — Micro-benchmarks are for finding *where* time goes in a code path; the SLO must be validated by a load test with realistic concurrency.

---

**Q9. What should you profile with, and when?**
- A) Only when performance is bad
- B) Always during load testing, not just on an idle system: async-profiler for CPU/alloc/lock/IO wall-clock at low overhead, JFR for long-running JVMs with low overhead and event-driven analysis. Idle profiles mislead because contention and GC behaviour appear only under load
- C) Only in development
- D) Profilers change behaviour too much to be safe

**Answer: B** — Sample profilers add single-digit-percent overhead, which is acceptable; the alternative (guessing) is far more expensive.

---

**Q10. Why does GC pause appear in p999 but not in the mean, and what do you tune?**
- A) GC is unpredictable
- B) Short, sharp pauses are invisible in a mean across thousands of requests but dominate the tail. Tune by measuring allocation rate and live-set size: reduce allocation first (the only durable fix), then choose a collector whose pause targets fit your budget (ZGC/Shenandoah for large heaps and low pauses, G1 as a general default)
- C) GC only affects throughput
- D) Increase heap

**Answer: B** — Allocation rate is the primary lever. Verify with an allocation profile, not intuition.

---

**Q11. What is the right way to size a thread pool from a load test?**
- A) Use the framework default
- B) From the measured service time: `threads ≈ λ × W_cpu_target / U_target` for CPU-bound work, or bounded by the downstream's capacity for I/O-bound work. Then verify that the measured throughput at that size matches your SLO
- C) 2× CPU count
- D) As many as the machine allows

**Answer: B** — For blocking I/O services, more threads help until the dependency saturates; the correct ceiling is the dependency's capacity, and exceeding it just moves the queue.

---

**Q12. Why does a load test that uses a mock everything give a false pass?**
- A) Mocks are faster, which is the point
- B) Mocks remove the very costs you are trying to find: real connection-pool waits, serialization to a wire format, network latency, downstream queueing, and lock contention. A test that mocks every dependency measures your own CPU
- C) Mocks are unreliable
- D) Mocks cannot be load tested

**Answer: B** — Stub at the network boundary, not inside the application. Model the dependency's latency and capacity explicitly, and make the stub rate-limited so it can saturate.

---

**Q13. What is the difference between a load test, a stress test, and a soak test?**
- A) They are synonyms
- B) Load: expected peak, verify SLOs. Stress: beyond peak, find the saturation point and the failure modes. Soak: sustained at peak for hours, find leaks, cache/connection-pool drift, log-volume growth, and slow degradation
- C) Stress is a longer load test
- D) Soak is for memory only

**Answer: B** — Most teams only run load tests, which is why they discover the leak during a four-day holiday and the saturation point during a promotion.

---

**Q14. What must be in the test report for a decision to be actionable?**
- A) Pass/fail
- B) The measured latency distribution with the load profile and environment ratio, the saturation point and which resource plateaued, the profiling evidence (flame graph or allocation profile), the identified bottleneck, the proposed fix, and the projected post-fix capacity — plus the confidence limits from a repeated run
- C) A chart
- D) The tool's HTML report

**Answer: B** — A report that does not name the bottleneck and the fix is a data-dump. And a single run has no error bars: run it three times.

---

**Q15. The single most common reason performance work fails to deliver is?**
- A) Wrong tooling
- B) The bottleneck is a shared dependency or an unmeasured layer (a database query plan, a lock, an external rate limit) that the application-level profile cannot see, so the team optimises Java code that was not the constraint
- C) Not enough tests
- D) Bad luck

**Answer: B** — Always establish where the time goes end to end, including the dependency, before optimising anything. Application profiles are blind to query time and to the queue in front of you.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and profile a real service under load.
- 12–10: revisit Little's Law, saturation detection, and coordinated omission; redo EXERCISES 2–5.
- <10: re-read THEORY + `PROJECT_PANAMA_ZERO_GC` cold and retake in 48 hours.
