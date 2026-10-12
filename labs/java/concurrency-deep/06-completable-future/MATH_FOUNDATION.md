# Math Foundation: Future Pipelines

## 1. Pipeline latency

Sequential stages with latencies `L1..Ln`:

```
T_seq = L1 + L2 + ... + Ln        (thenCompose chain)
T_fanout = max(L1, L2) + M        (thenCombine/allOf + merge M)
```

Numbers: profile 60ms + orders 90ms, merge 5ms → sequential 150ms,
`thenCombine` 95ms. Fan-out only pays when upstreams truly overlap — same-pool
blocking stages serialize and the `max` degrades to a sum.

## 2. Hedged race (`anyOf`) tail math

Two replicas with p99 latencies `P99a`, `P99b`, independent:

```
P99_hedged ≈ latency at which P(both slower than t) = 1%
```

Replica p99 = 200ms each, independent → hedged p99 ≈ 200ms × ~0.7 ≈ 140ms
(order-of-magnitude sketch; measure). Cost: 2× load always. Hedge only when
tail latency costs more than the duplicate requests.

## 3. Pool sizing for blocking stages

```text
threads ≈ targetConcurrency × (1 + waitTime / computeTime)
```

20 concurrent blocking calls, 90ms wait / 10ms compute → ~200 threads in the
dedicated pool. The common pool (CPUs−1, e.g. 7 on 8 CPUs) fits ~7 such tasks
before starving streams — the quantitative reason blocking stages never use
the default executor.

## 4. Timeout sizing

`orTimeout(t)` wins iff upstream exceeds `t`. With mean latency μ and stddev σ:

```
t ≈ μ + 3σ   (covers ~99.7% under normality; use measured p99 + margin)
```

μ = 120ms, σ = 30ms → t ≈ 210ms. Timeouts near μ amputate healthy tails;
timeouts at 10× μ barely bound anything. Set from the latency histogram, not
round numbers.

## 5. allOf barrier cost

`allOf` over N futures: O(N) completions tick one counter; value extraction is
N non-blocking `join()`s. Total = `max(Li)` + O(N) bookkeeping. No batching
benefit past overlap — 100 already-complete inputs complete the barrier inline
in microseconds.

## 6. First-completion-wins race probability

Two racers, exponential gaps with rates λ1, λ2: `P(1 wins) = λ1/(λ1+λ2)`.
Equal 50ms means → coin flip. `complete()`-racing threads follow the same law
— "reserve then confirm" patterns need an explicit atomic guard, not CF racing.
