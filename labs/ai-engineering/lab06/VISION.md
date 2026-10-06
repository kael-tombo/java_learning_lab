# Lab 06: AI Pipeline Orchestration — Vision

## Anatomy of a Pipeline

```
  input
    |
  +-v-----------+  policy: FAIL on policy/permanent
  |  ingest     |  idempotent: yes  timeout: 2s  cache: by content hash
  +-----+-------+
        |
  +-----v------+  policy: DEGRADE on data problems
  |  validate  |  emits rejected items to a dead letter queue
  +-----+------+
        |
  +-----v------+  policy: RETRY on transient
  |  transform  |  idempotent: yes  CACHEABLE (deterministic)
  +-----+------+                          \
  +-----v------+                           \  parallel branches
  |  feature   |  CACHEABLE (deterministic)  \ both must finish before infer
  +-----+------+                             /
  |  embed     |  CACHEABLE  BATCHABLE        /
  +-----+------+                            /
        |                                   /
  +-----v------+  policy: FAIL  bounded concurrency  MOST EXPENSIVE
  |  infer     |  batched, no cache unless seeded
  +-----+------+                            \
        |                                   \  both must finish before emit
  +-----v------+  policy: FAIL  parse errors are recoverable
  |  post-     |                            /
  +-----+------+                           /
  +-----v------+                           /
  |  validate  |                           /
  +-----v------+                           /
        |                                  /
        +--------------+------------------+
                       v
                    output
                       |
              [PipelineSpec hash recorded here]
```

## Critical Path vs Per-Stage Time

```
  ingest 50 -> validate 20 -> { transform 200 || embed 300 } -> infer 800 -> emit 30

  sum of all stages      = 1400 ms      <- NOT the latency
  critical path          = 1200 ms      <- the latency

  halving transform 200 -> 100:
     sum  = 1300, path = 1200      NO CHANGE. it was off the path.

  halving embed 300 -> 150:
     sum  = 1250, path = 1050      1.14x speedup.

  halving infer 800 -> 400:
     sum  = 1000, path =  800      1.50x speedup.

  => profile the critical path. optimizing a parallel branch is the
     single most common wasted optimization in pipeline work.
```

## Bottleneck Analysis

```
  throughput_i = concurrency_i / T_i

  stage        T_i      c_i     throughput
  ingest       50 ms     4        80/s
  validate     20 ms     4       200/s
  transform   200 ms     8        40/s
  embed       300 ms     8        26.7/s
  infer       800 ms    16        20/s    <- BOTTLENECK
  emit         30 ms     8       267/s

  pipeline throughput = min = 20/s
  adding concurrency to ingest changes nothing.

  OPTIMIZATION TARGET = high utilization ON THE CRITICAL PATH
  (embed at 26.7/20 = 1.33 utilization, on the path -> target)
```

## Error Policy Matrix

```
  failure class        | policy   | effect
  --------------------+----------+----------------------------------------
  transient (timeout,  | RETRY    | bounded attempts with backoff + jitter;
   5xx, connection)    |          | harmless if idempotent
  --------------------+----------+----------------------------------------
  data (bad row,       | DEGRADE  | emit a fallback value; count it; the
   malformed record)    |          | partial result is usable
  --------------------+----------+----------------------------------------
  permanent (schema    | FAIL     | stop the chain; dead-letter the item
   mismatch, auth)      |          |
  --------------------+----------+----------------------------------------
  policy (blocked      | FAIL     | never degrade a policy violation into a
   content)             |          | silent success

  the non-obvious one: a non-idempotent stage declaring RETRY.
  if it sends an email and times out, a retry sends it twice.
  => retry only idempotent stages; others verify state before retrying.
```

## Backpressure

```
  arrival 25 rps, service 20/s

  UNBOUNDED QUEUE
     queue grows -> memory grows -> GC pressure -> OOM
     all requests time out together
     retries pile on -> 25 * 1.4 = 35 rps offered
     collapse is not gradual

  BOUNDED + SHED AT 18/s
     18 requests served at 100% success
     7 rejected immediately with 429 + Retry-After
     goodput = 18/s
     latency stays inside SLO for the requests that matter

  goodput = min(1, k/service_rate) * service_rate * success_rate
     k=18, service=20:  18/s * 1.0   = 18
     k=20, service=20:  20/s * ~0.65 = 13   (timeouts + retries)

  SHEDDING EARLY IS STRICTLY BETTER.
```

## Retry Amplification Across Stages

```
  per stage: p_retry = 0.30, max 3 attempts  ->  E[attempts] = 1.43x

  stage 1 fails -> 1.43x load on stage 2
  stage 2 fails -> 1.43x load on stage 3
  ...
  4 stages      ->  1.43^4 = 4.2x load on the deepest stage

  during an incident, the pipeline generates 4x the traffic it received.
  the original failure looks like a traffic spike.

  FIXES
    - global retry budget (a shared token bucket across stages)
    - circuit breaker per stage: open on sustained failure, fall back
    - exponential backoff with FULL JITTER (not fixed)
    - fail fast on the deepest/most expensive stage
```

## Cache Placement

```
  stage         T_i     cacheable?            why
  ------------------------------------------------------------------
  ingest       50 ms    yes (content hash)    cheap anyway
  validate     20 ms    no                    trivial
  transform   200 ms    yes                   deterministic, moderate cost
  feature     150 ms    yes                   deterministic
  embed       300 ms    yes                   EXPENSIVE + deterministic
  infer       800 ms    only if seeded        sampling makes it impure
  emit         30 ms    no                    trivial

  speedup with h=0.7 and a 5x cheaper recompute:
     1/(0.3 + 0.7/5) = 2.27x on that stage

  configHash in the key:
     change embed chunk_size 512 -> 256
     configHash changes -> every embed key misses -> downstream invalidates too
     NO MANUAL CACHE CLEAR REQUIRED
```

## PipelineSpec Diff

```
  v1: ingest@2#a1  validate@1#b2  transform@3#c9  embed@2#d4  infer@5#e1
  v2: ingest@2#a1  validate@1#b2  transform@4#f7  embed@2#d4  infer@5#e1
                    transform bumped

  PipelineSpec.diff -> ["~transform (3 -> 4)"]

  "answers got worse since Tuesday"
    -> ONE stage changed
    -> canary the transform stage alone
    -> 10 minute experiment instead of a 2 hour investigation

  spec hash recorded with every result makes this possible for any
  response, retrospectively.
```

## Metrics That Matter

```
  PER STAGE:  latency p50/p95/p99 | errors by class | retries | cache hit
              | items in/out | queue depth | rejections

  DERIVED:    critical path              (which stages are serializing)
              utilization                (c_i / T_i vs bottleneck)
              targets = high utilization AND on the critical path
              cost share per stage
              residency (Little's law)  -> memory pressure

  SANITY:     sum(stage latency) ~= wall clock (within tolerance)
              if not, the instrumentation is lying and every
              dashboard built on it is wrong.
```

## Self-Check

- [ ] Every stage declares inputs, outputs, policy, timeout, retry, limits.
- [ ] Errors typed by recoverability; policy declared per class.
- [ ] Retries only on idempotent stages.
- [ ] Queue depth bounded; rejection explicit.
- [ ] Cache keys include config hash.
- [ ] Critical path identified before optimizing anything.
- [ ] Per-stage metrics from day one; sum verified against wall clock.
- [ ] `PipelineSpec` recorded with every result and diffable.