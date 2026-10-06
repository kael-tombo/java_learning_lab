# Model Serving with Docker - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab05  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `RSS = heap + metaspace + threads x stack + direct` | Memory model - all of it must fit the limit |
| `heap_max = 0.70 x container_limit` | Heap sizing - leaves headroom for the rest |
| `throughput = batch / (latency + window)` | Batching - amortised cost per example |
| `cold_start = jvm + load + warmup` | Startup budget - must fit the rollout window |
| `p99_batch = p99_infer / batch + window` | Latency with batching - the window is pure added latency |
| `image_size = base + jre + app` | Image budget - push time scales with size |

## Why the Math Matters

Serving is where a model meets a latency budget. The mathematics is memory partitioning, batching arithmetic and queueing behaviour; the engineering is making those numbers hold under a burst.


---

## 1. Container memory budget

```text
limit = heap + metaspace + threads x stack + code cache + direct
heap = MaxRAMPercentage x limit, typically 0.65-0.75
RSS must stay below limit under peak load
```

The heap is only part of the container's memory. Sizing the heap to the limit is the most common cause of OOMKilled pods with a healthy-looking heap.

**Worked example.** Limit 1 GiB: heap at 0.70 = 717 MB, leaving 307 MB for metaspace (~80 MB), 200 threads x 1 MB stacks (200 MB), and buffers. Tight; use 0.65 or fewer threads.


---

## 2. Batching latency and throughput

```text
p99_request = window + p99_infer(b) + overhead
throughput = b / p99_request
optimal b maximises throughput subject to p99_request <= budget
```

Batching increases throughput until queueing latency dominates. The optimal batch size is the largest that still fits the latency budget, which is why the window is derived rather than guessed.

**Worked example.** Budget 50 ms, single-inference p99 12 ms. Window 10 ms gives p99 22 ms at b=1; window 25 ms with b=8 gives p99 37 ms and roughly 6x the throughput. Window 40 ms would breach the budget.


---

## 3. Cold start budget

```text
cold_start = t_jvm + t_load + t_warmup
rollout_safe if cold_start < (maxUnavailable_budget)
for a rolling update, each pod must be ready within the readiness probe budget
```

A rolling update fails when pods take longer to become ready than the controller tolerates. Knowing the decomposition tells you whether to shrink the model, warm more, or raise the probe budget.

**Worked example.** JVM 0.6 s, model load 1.2 s, warm-up 3.0 s = 4.8 s. With a 5 s readiness period the rollout is marginal; trimming warm-up to 1.5 s gives 3.3 s and comfortable headroom.


---

## 4. Sizing requests from measurement

```text
requests.cpu = p99_cpu at target QPS
requests.memory = p99_rss
limits.memory = p99_rss x 1.3 (headroom for bursts)
limits.cpu > requests so throttling is bursty, not permanent
```

Requests drive scheduling; limits drive throttling and OOM. Setting them from measurement avoids both over-commitment and permanent throttling, which is the usual cause of mysterious p99 spikes.

**Worked example.** p99 CPU 0.4 cores at 500 QPS, p99 RSS 700 MB. Requests 0.4 CPU / 700 MB, limits 1 CPU / 950 MB: throttling only during bursts, and 250 MB of memory headroom for spikes.


---

## Cheat Sheet

- `RSS = heap + metaspace + threads x stack + direct` - Memory model
- `heap_max = 0.70 x container_limit` - Heap sizing
- `throughput = batch / (latency + window)` - Batching
- `cold_start = jvm + load + warmup` - Startup budget
- `p99_batch = p99_infer / batch + window` - Latency with batching
- `image_size = base + jre + app` - Image budget

## Numerical Traps

- Setting -Xmx equal to the container limit and then being OOMKilled by native memory.
- Adding a batch window without subtracting it from the latency budget.
- Requesting CPU from intuition, then watching the pod get permanently throttled.
- Doing model work inside a health check, turning a load spike into a restart storm.
- Treating a warm first request as acceptable because it only happens once per pod.

## Self-Check Problems

1. Compute a heap size for a 2 GiB limit with 300 threads, targeting 25% native headroom.
2. For a 50 ms budget and 12 ms single-inference p99, tabulate p99 and throughput for windows of 0, 5, 10, 25, 40 ms.
3. Measure and decompose cold start into JVM, load and warm-up; identify which stage to reduce.
4. Set requests and limits from a load test reporting p99 CPU 0.6 cores and p99 RSS 820 MB.
5. Design a readiness probe whose period and budget are consistent with a rolling update strategy.
