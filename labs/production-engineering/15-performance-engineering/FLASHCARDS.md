# Lab 15: Performance Engineering & Load Testing — Flashcards

~60 cards. Most answers are a formula, a tool, or a threshold.

---

## Little's Law & queues

Q: Little's Law?
A: `L = λ × W`. In a stable system, in-flight requests = arrival rate × time in system.

Q: Valid when?
A: When the system is in steady state and arrival rate is independent of service time. Invalid during overload (the regime where you most want it).

Q: Use cases?
A: Convert latency → concurrency, size pools/threads, predict the effect of a latency regression, decide whether a queue is growing.

Q: What does a growing queue look like?
A: `L` rising while `λ` is constant → `W` rising. That is saturation, and it is visible before the CPU does.

Q: Utilization → latency knee?
A: Queueing delay grows non-linearly as utilization approaches 1. Rule of thumb: keep steady-state utilization ≤ 60–70% for latency-sensitive paths (a common "multiplication of 2 at 70%" rule of thumb — verify for your service shape).

Q: M/M/1 intuition?
A: Waiting time rises roughly proportionally to `ρ/(1−ρ)`, where ρ is utilization. At ρ=0.5 the wait is ~1× service time; at 0.9 it is ~9×.

Q: Queue theory's first rule?
A: Queueing delay is negligible at low utilization and dominates at high utilization. Design for the knee, not for the theoretical maximum.

---

## Load test types

Q: Load / stress / soak / spike?
A: Load = expected peak, verify SLOs. Stress = beyond peak, find saturation. Soak = sustained hours, find leaks and drift. Spike = sudden burst, test resilience.

Q: Open-loop vs closed-loop?
A: Open-loop sends at a fixed arrival rate regardless of latency (honest queueing); closed-loop keeps N users looping (throttles itself, hides the queue, measures service time not system behaviour).

Q: Which do you want?
A: Open-loop for SLO validation and saturation discovery; closed-loop is useful for steady-state throughput at fixed concurrency.

Q: Coordinated omission?
A: A closed-loop generator that pauses during a stall, never recording the requests it should have sent — excluding the slow period from the percentiles. Fix: measure from intended send time.

Q: Ramping profile?
A: Step or linear increase until throughput plateaus. This is how you *find* the knee rather than assume it.

Q: Warm-up?
A: JIT compilation, class loading, and cache fills mean the first minutes are not representative. Warm with realistic traffic before measuring, and state your warm-up policy.

---

## Environments

Q: What must match production?
A: The *ratio* of offered load to capacity (CPU/request, memory/request, connections, payload size), realistic data volumes and indexes, realistic cache hit ratio, realistic concurrency per user, and the real dependency (stubbed at the network, rate-limited).

Q: Why does only matching rps fail?
A: A test box 4× faster than production passes at production rps and fails at production load, because CPU/request is 4× lower.

Q: Production-shaped data?
A: A table with 1M rows has different index behaviour than 10k. Load data at realistic size and skew (hot keys, long-tailed).

Q: Network shaping?
A: Add realistic RTT and jitter (e.g. 2 ms ± 0.5 ms within a region, 40 ms cross-region). Loss and reordering are worth a smaller test.

Q: Stub the dependency or mock in-process?
A: Stub at the network with a rate limit and realistic latency. In-process mocks remove connection pools, serialization, network, and the dependency queue — the things you are trying to measure.

---

## Measurement

Q: Which percentiles?
A: p50, p95, p99, p99.9 — and max as a smell. Averages hide everything.

Q: Report what alongside percentiles?
A: Offered rate, achieved rate, error rate, concurrency, per-phase timing, and the environment ratio. Percentiles without offered load are meaningless.

Q: How many runs?
A: Three. Report median and spread — otherwise you cannot tell an improvement from a run-to-run variance.

Q: Warm-up excluded?
A: Yes, and state the exclusion window. Steady-state means matter more than transient warm-up for capacity.

Q: Coordinated-omission-safe tools?
A: Any tool that can report "intended send time" latency or use a constant-arrival-rate scheduler (k6 has arrival-rate executors; Gatling has open models with `constantArrivalRate`). Verify the specific executor semantics for your version.

---

## CPU-bound vs I/O-bound

Q: How do you tell?
A: Increase concurrency. If throughput stops rising and CPU saturates, you are CPU-bound. If throughput rises until a pool/connection/lock/downstream saturates while CPU stays low, you are I/O-bound.

Q: CPU-bound thread pool sizing?
A: `threads ≈ λ × W_cpu / U_target`, roughly cores for pure CPU work with a small queue.

Q: I/O-bound thread pool sizing?
A: Bounded by the *dependency's* capacity, not by CPU. More threads past that just move the queue into the pool.

Q: What is the right pool size for a blocking downstream?
A: `pool ≈ λ × W_downstream × safety`, capped by the downstream's concurrency capacity. Sizing it larger than the dependency's capacity is a self-inflicted queue.

Q: Amdahl's Law relevance?
A: If a fraction `f` is optimised to zero time, speedup `= 1/((1−f) + f/s)`. 5% of a request path being slow means a 20× max speedup no matter what you do to it — find the fraction first.

---

## Profiling

Q: Tools?
A: async-profiler (CPU, allocation, lock, io, wall-clock) at low overhead; JFR for long-running, event-driven analysis; `perf`/eBPF for kernel-level; database-side plans.

Q: When?
A: Under load, always. Idle profiles omit contention, GC interaction, and page faults.

Q: async-profiler modes?
A: `-e cpu`, `-e alloc`, `-e lock` (with `--cstack` for the blocking frame), `-e wall`, `-e itimer`. Output as a flame graph + collapsed stacks for further analysis.

Q: Read a flame graph how?
A: Width = samples on stack = time. Find the *widest* frame (not the deepest); look for wide frames under a lock or a blocking call; ignore narrow stacks (they are noise).

Q: Alloc vs GC?
A: Reduce allocation rate first — it is the durable fix. Then tune pause target/collector. `-XX:+UseZGC` for large heaps and low pause needs; G1 as the general default.

Q: JFR vs async-profiler?
A: JFR: near-zero overhead, continuous, event-driven — good for production capture. async-profiler: more precise for specific questions (lock contention, allocation hot spots).

Q: Where does the flame graph not look?
A: Inside the database and the network. Correlate wall-clock per phase (`W_total` vs Σ `W_dep`) to allocate time to the dependency before optimising your code.

---

## JVM performance knobs

Q: GC selection heuristic?
A: Large heap, tight tail → ZGC/Shenandoah (sub-ms pauses, more CPU). General default → G1. Small heaps → Parallel.

Q: `MaxGCPauseMillis`?
A: A soft target; the collector sizes generations to approach it, at the cost of throughput/CPU. Verify actual pause percentiles — the target is not a guarantee.

Q: `-Xms == -Xmx`?
A: Avoids resize pauses and makes RSS predictable for the scheduler; costs committed memory up front.

Q: `AlwaysPreTouch`?
A: Faster warm-up (pages resident), higher startup RSS. Worth it for short-lived processes and predictable latency.

Q: Object allocation is the first target?
A: Yes. Allocation rate drives GC frequency; escape analysis, reusing buffers, avoiding autoboxing, and immutable value objects all reduce it.

Q: String concatenation in a loop?
A: Allocates repeatedly. Prefer `StringBuilder` (or, better, avoid the loop). This is a real source of measurable allocation rate.

Q: Lock contention symptom?
A: Flat throughput, rising p99, high thread count, low CPU — threads parked in a lock. Fix with finer-grained or lock-free structures, or sharding.

---

## Databases

Q: The most common bottleneck?
A: The database. A missing index, a query plan change, or N+1 will dominate everything else.

Q: Verify the plan?
A: `EXPLAIN (ANALYZE, BUFFERS)` on the real statement with realistic parameters. A sequential scan on a large table is the usual finding.

Q: N+1?
A: 1 + N queries for N returned rows. Fix with a join/projection/batch fetch. Load tests catch this dramatically: a list endpoint with N+1 at limit=100 generates 101 queries per request.

Q: Connection pool saturation?
A) Watch `pending` threads, acquire latency p99, and the pool's active/idle counts. Saturation shows as rising acquire latency, not as a database problem.

Q: Lock waits?
A: A read-heavy service blocked by a writer. Measure `pg_locks` waiting queries and lock-wait time; the fix is to shorten the transaction.

---

## Testing hygiene

Q: Isolate variables?
A: One change per run. Otherwise you cannot attribute the delta.

Q: Compare like with like?
A: Same commit, same data, same warm-up, same profile, three runs, report median and range.

Q: Where do you measure?
A: Client-side latency includes the network and the load generator; server-side (a histogram in the app) isolates the service. Report both, and know which question each answers.

Q: What is a realistic "peak"?
A: Peak plus headroom for growth and for failure-domain reduction (N+1 capacity planning). Capacity for peak alone means failure takes you over the edge.

Q: What does "done" look like?
A: A report naming the bottleneck, the fix, the projected post-fix capacity, and the residual risk — plus a CI/perf-regression gate so it stays fixed.

---

## Numbers to memorize

Q: Little's Law?
A: `L = λ × W`.

Q: Utilization target for latency-critical paths?
A: ≤ 60–70% steady state.

Q: Pool size rule (blocking downstream)?
A: `λ × W_downstream × safety`, capped at the dependency's capacity.

Q: `maxPoolSize` vs `minimumIdle`?
A: `maxPoolSize` bounds concurrency to protect the DB; `minimumIdle` keeps warm connections but is not a warm-up target — verify against your HikariCP version's semantics.

Q: GC pause target?
A: For a 200 ms SLO, sub-10 ms p99 pauses leave headroom. ZGC/Shenandoah achieve sub-ms at large heaps.

Q: Load profile steps?
A: Ramp in ~10% steps with 2–5 min each until throughput plateaus.

Q: Runs per configuration?
A: Three, report median and spread.

Q: Warm-up duration?
A: Until JIT has compiled and caches are at steady state — often 5–15 min for a JVM service; state the policy.

Q: Amdahl: 5% serial fraction, 20× speedup of that part?
A: `1/(0.95 + 0.05/20) = 1.05` → 5% overall. Optimise the dominant fraction.
