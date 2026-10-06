# Lab 02: Concurrency in Production — Math Foundation

Concurrency tuning without numbers is superstition. These are the few formulas that actually decide pool sizes, back-pressure budgets, and contention diagnosis.

---

## 1. Little's Law — the master equation

```
L = λ · W
```

- `L` = in-flight work (concurrency)
- `λ` = arrival rate (req/s)
- `W` = average time to complete one item (s)

Solve for capacity: with `λ = 8000 req/s` and a latency budget of `W = 0.05 s`:

```
L = 8000 × 0.05 = 400 concurrent requests
```

**This is your thread-pool floor.** A pool of 100 threads cannot serve 8000 req/s at 50 ms — it can serve at most `100 / 0.05 = 2000 req/s`. That single equation explains most "thread pool exhausted" incidents.

The other direction is just as useful: with a fixed pool of `P` threads, the maximum sustainable rate is

```
λ_max = P / W
```

---

## 2. Pool sizing formulas

### CPU-bound (no blocking)

```
P = cores × CPU_util + 1        (≈ cores + 1 at ~100% utilization)
```

With 16 cores: `P = 17`. Adding more threads only steals CPU and inflates context switches.

### I/O-bound

```
P = cores × CPU_util × (1 + W_wait / W_cpu)
```

With 16 cores, 5% CPU utilization, a 100 ms DB call and 1 ms compute:

```
wait/service = 100/1 = 100
P = 16 × 0.05 × (1 + 100) ≈ 80.8  →  81 threads
```

Note the shape: **the ratio of wait to service time dominates**, not the core count. Double the DB latency and you roughly double the needed pool.

### With a target queueing delay

If you also want queueing under burst, target `W_q = W_s + W_queue` and iterate pool size until simulated throughput matches arrival rate (use the M/M/c model in §4).

---

## 3. Queue sizing (Kingman's formula)

Kingman's approximation for mean waiting time in a G/G/c queue with coefficient of variation `c_a²` (arrivals) and `c_s²` (service):

```
W_q ≈ [ c_a² + c_s² ] / 2 × W_s × C(c, a) / (c × ρ - 1)      for ρ > 1/c
```

where `ρ = λ / (c · μ)` is utilization, `c` = servers (threads), and `C(c,a)` is the Erlang-C delay probability.

Worked sanity check: `c = 80` threads, `W_s = 0.1 s`, `λ = 500 req/s`:

```
μ = 1/W_s = 10 per second per thread
capacity = 80 × 10 = 800 req/s
ρ = 500/800 = 0.625
```

At `ρ = 0.625` with `c_a² = c_s² = 1`, `C ≈ 0.11`:

```
W_q ≈ 1 × 0.1 × 0.11 / (80×0.625 − 1) ≈ 0.011/49 ≈ 0.2 ms
```

**Takeaway**: queueing delay is negligible until `ρ → 1`, then explodes. Design for `ρ ≤ 0.7`.

---

## 4. Erlang C — when do you need another thread?

Erlang-C gives the probability an arriving customer must wait:

```
C(c, a) =  [ a^c / (c! · (1−ρ)) ] / [ Σ_{k=0}^{c−1} a^k/k! + a^c/(c!·(1−ρ)) ],   ρ = a/c
```

Sweep `c` for `λ = 500 req/s`, `μ = 10/s`, target `W_q < 50 ms`:

| c | ρ | C(c,a) | W_q (approx) |
|---|---|---|---|
| 52 | 0.96 | 0.72 | ~2.5 s |
| 60 | 0.83 | 0.42 | ~180 ms |
| 70 | 0.71 | 0.20 | ~25 ms |
| 80 | 0.63 | 0.11 | ~2 ms |
| 100 | 0.50 | 0.03 | ~0.3 ms |

Going from 70 to 80 threads cuts queueing from 25 ms to 2 ms. Going from 80 to 100 buys almost nothing. **Diminishing returns are steep — sizing is a business decision, not a max-out.**

---

## 5. Back-pressure and buffer budgets

If a producer emits at `λ_p` and a consumer drains at `λ_c < λ_p`, the backlog grows:

```
backlog(t) = (λ_p − λ_c) · t
```

`λ_p = 1200 msg/s`, `λ_c = 900 msg/s` → backlog grows 300 msg/s → 18,000 messages per minute.

If each message costs 2 KB in memory, that's **36 MB/min of unavoidable retention**. Time to overload at a 512 MB buffer:

```
t = 512 MB / 36 MB·min⁻¹ ≈ 14 minutes
```

This is the number that justifies a bounded queue: either you shed load, or you degrade, and the math tells you how long you have to decide.

---

## 6. Contention and scalability

Amdahl's law with a parallel fraction `f` and infinite cores:

```
speedup_max = 1 / (1 − f)
```

But add serialization overhead `s` (locks, coherence traffic). A naive model of a shared counter with atomic increment across `P` threads on one cache line:

- At `P = 1`: throughput `T₁`
- At `P = 8`: each core's cache line ping-pongs; throughput often *drops*

**Coalesced work scales**; fine-grained contention does not. Measure with `perf c2c` (cache-to-cache) — it names the exact contended cache line.

Striped counter throughput model: `P` stripes → contention probability drops roughly as `1/P`:

```
P(contention at P threads) ≈ 1 − e^(−k·P/P_stripes)
```

---

## 7. Queue drain latency

A single-consumer queue with service rate `μ_c` must drain a burst `B` before it can catch up:

```
t_drain = B / (μ_c − λ_a)      when λ_a < μ_c
t_drain = ∞                   when λ_a ≥ μ_c
```

`B = 50,000` messages, `μ_c = 1000/s`, `λ_a = 200/s`:

```
t_drain = 50,000 / 800 = 62.5 s
```

A 62-second tail on a recovery storm is why you need **shed + shed priority**, not just a bigger buffer.

---

## 8. Availability math for concurrency limits

With `c` independent threads and per-call failure probability `p` (`p = 0.001`):

```
P(at least one success) = 1 − p^c
```

But if `c` threads all hit a rate-limited dependency that fails when overloaded, failures are **correlated** and independence is false — availability collapses together. This is why bulkheads (isolated pools per dependency) beat one big pool under partial dependency failure.

---

## 9. Timeouts and the deadline budget

A request with a 250 ms end-to-end budget and three sequential downstream calls:

```
t_db(1) + t_service(2) + t_db(3) + overhead ≤ 0.250 s
```

If each DB call is 50 ms, service is 20 ms → `0.05+0.02+0.05 = 0.12 s`, leaving 130 ms of slack for GC pauses and network. **Never let timeouts sum above the client-visible budget** — otherwise retries compound the overload.

Retry amplification with `r` retries:

```
worst_case_calls = (r+1)^depth
```

3 retries across 2 layers = 16 calls per user request. During an incident that *is* the outage.

---

## 10. Virtual-thread economics

Memory per platform thread: stack (`-Xss`, typically 512 KB–1 MB) + JVM bookkeeping.

```
platform_threads × 1 MB = memory
virtual_threads ≈ 1–2 KB each of heap/continuation structure
```

With a 4 GB budget: `≈ 4,000 platform threads` vs `≈ 2,000,000 virtual threads`. The scarce resource becomes **carrier CPU**, not thread count — hence semaphore-based concurrency limiting for expensive operations.

---

## 11. Queue fairness math

For a fair queue of `P` threads each with arrival rate `λ_i`, completion order is FIFO only if the service rates are equal. With heterogeneous service times `S_i`, the slowest worker becomes the pipeline bottleneck:

```
Throughput = 1 / max_i(S_i)   (for a shared queue)
```

A single 500 ms batch task in an otherwise 5 ms queue halves system throughput regardless of pool size.

---

## 12. Quick drills

1. `λ = 5000/s`, `W = 20 ms` → how many concurrent requests? **Answer: 100.**
2. Pool of 100, `W = 20 ms` → max throughput? **Answer: 5000/s. Anything more and the queue grows unboundedly.**
3. `λ = 200/s`, 100 ms DB calls, 8 cores → I/O pool size? **Answer: `8 × (1+100/1) ≈ 808`… in practice start at 60–100 and use a semaphore.**
4. Producer 1200/s, consumer 900/s, 2 KB messages, 512 MB buffer → time to OOM. **Answer: ~14 min.**
5. `ρ = 0.9` with `C ≈ 0.6`, service 10 ms → `W_q ≈ 0.6 × 0.01/(c·0.9−1)`; with `c = 100` → ~0.67 ms. **Takeaway: at ρ=0.9 with enough servers the delay is still small; the danger is ρ ≥ 1.**

---

## 13. Formulas worth memorizing

| Formula | Use |
|---|---|
| `L = λ·W` | pool floor / max sustainable rate |
| `P = cores(1 + wait/service)` | I/O pool sizing |
| `ρ = λ/(c·μ)`, keep ≤ 0.7 | capacity planning |
| `backlog = (λ_p − λ_c)·t` | "how long until we fall over" |
| `t_drain = B/(μ−λ)` | recovery time from a burst |
| `speedup ≤ 1/(1−f)` | Amdahl ceiling on scalability |
| `(r+1)^depth` | retry amplification |
