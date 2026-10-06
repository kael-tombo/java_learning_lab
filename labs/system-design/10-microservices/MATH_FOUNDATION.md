# Microservices - Math Foundation

## Latency Compounding: Why Sync Chains Are Dangerous

Latency adds along a synchronous chain. This is the single most important
arithmetic in service design.

```
  T_total = sum over hops of (network_RTT_i + service_time_i)

  Example: checkout -> order -> inventory -> pricing -> payment
    5 hops, 2 ms intra-region RTT, 60 ms service each:
    T_total = 5 * (2 + 60) = 310 ms
```

### Tail Latency Multiplication (Far Worse Than the Sum)

```
  If each service has p99 = 100 ms and calls are SEQUENTIAL:
    P(all 5 under 100 ms) = 0.99^5 = 0.951
    so the chain's p95 is already a single service's p99
    and the chain's p99 corresponds to the 99.9th percentile of ONE service

  Realistic chain p99 with p50 = 60 ms, p99 = 100 ms per service:
    p50 chain ~= 310 ms
    p99 chain ~= 700-1200 ms   (3-4x the naive 500 ms)
```
The lesson: **p99 of a chain is much worse than N times p99 of one service**.
This is why:
- Parallelise independent calls (p99 of parallel = worst of the set).
- Cap chain depth at 2-3.
- Budget explicitly and shed load before exceeding it.

### Parallel Fan-Out

```
  serial   = sum(...)          = 310 ms
  parallel = max(...)          =  62 ms   -> 5x faster

  BUT: connections held = fanout * concurrent_requests
    1,000 concurrent, fanout 5 -> 5,000 connections
    Little's Law: concurrency = throughput * service_time * fanout
```
Parallelism trades latency for connection pressure. Often the right trade, but
it must be a decision with the number in it.

## Availability Compounding

```
  A_chain = product over i of A_i

  chain of 3 services at 99.9%:
    0.999^3 = 0.997 = 99.7%

  chain of 5: 0.995 = 99.5%
  chain of 10: 0.990 = 99.0%
```
Note how fast this erodes. **Three is about the practical maximum** for a
synchronous critical path, which is why architecture reviews question any
dependency chain deeper than that.

### Availability Is Multiplied, Not Added

```
  Independent services (parallel, optional):  A_platform ~= A_best_service
  Serial chain (all must succeed):           A_platform ~= product of all

  Adding a *replica* or *optional* service never reduces availability.
  Adding a *required* synchronous dependency always does.
```

### Degradation Restores Availability

```
  Optional recommendations service at 99% availability:
    if required:  A_checkout = 0.999 * 0.99 = 0.989
    if optional:  A_checkout = 0.999              (11x improvement)
```
Any dependency that can be made optional should be. Reclassify hard
dependencies as optional wherever product will tolerate a degraded response.

## Failure Probability and Blast Radius

```
  Independent failure probability p per service, S services:
    P(at least one fails in a window) = 1 - (1 - p)^S

    p = 0.001, S = 50 -> 1 - 0.999^50 = 4.9%   (almost 5% daily)

  Correlated failure (shared dependency: same DB, same deploy, same AZ):
    P(shared component fails) = p_shared, INDEPENDENT of S
```
This is why shared infrastructure dominates failure probability in a
microservices platform. Fifty services that each need 99.9% but share a
PostgreSQL instance have the availability of 99.9%, not better.

## Circuit Breaker Math

```
  Breaker states: CLOSED -> OPEN -> HALF_OPEN -> CLOSED

  window = 20 s, minimum_request_threshold = 20 requests
  failure_ratio_threshold = 0.5

  Failure rate from a leaking dependency:
    dependency p_fail = 0.3, breaker threshold 0.5 -> never opens (correct:
    it is degraded but not broken, and opening would remove real function)

    dependency p_fail = 0.8 -> opens, requests fail fast, dependency can
    recover instead of being hammered
```

### Hysteresis and Probe Rate

```
  half_open_probe_count = K
  Recovery time = open_interval + K * service_time

  K = 1, open_interval = 30 s -> ~30-31 s to recover
  K = 3, open_interval = 30 s -> ~30-31 s, faster confirmation, small risk
                                     of re-tripping under load
```

### Breaker Coordination Across the Fleet

```
  Per-instance breakers: S instances each open independently
  Time until the fleet stops calling B ~= S * request_interval  (fast)
  But: no single view; and probes from all instances arrive at once on
  half-open, which can re-break B.

  Shared/propagated breaker state:
    faster, consistent view, but adds a dependency and a propagation delay
    -> a shared store outage now affects the calling path
```
Start per-instance. It is local, free, and has no dependency. Only move to
propagation if you have measured a problem it solves.

## Bulkhead Sizing

```
  Bulkhead = dedicated resource pool per dependency, sized to that dependency's
             expected share of traffic.

  checkout calls: inventory 30%, payment 10%, pricing 20%, other 40%
  100 threads total:
    inventory pool = 30, payment pool = 10, pricing pool = 20, other = 40

  failure_mode without bulkheads:
    payment pool (10 threads) exhausts -> all 100 threads block on payment
    -> total checkout outage for a 10% dependency

  with bulkheads:
    payment pool exhausts -> 10 threads affected -> 90 still serve traffic,
    and payment failures are isolated and visible
```

### Pool Sizing from Little's Law

```
  concurrency_i = throughput_i * service_time_i * safety_factor

  checkout total 1,000 rps, payment 100 rps, payment p50 120 ms:
    100 * 0.12 = 12  ->  pool of 12-24 (safety 1.0-2.0)
```
**This is the number that must not be a guess.** An under-sized pool turns
traffic spikes into artificial latency; an over-sized pool lets a slow
dependency consume unbounded memory.

## Timeout Derivation

```
  Timeout at each hop must satisfy:
    own_timeout < caller's_remaining_budget

  Example: client 1,000 ms
    gateway self budget      50 ms  -> gives 950 ms
    checkout self budget    100 ms  -> gives 850 ms
    order self budget       100 ms  -> gives 750 ms
    inventory self budget    50 ms  -> gives 700 ms
    database query timeout  600 ms
    response shaping        100 ms
    ---------------------------------
    total                   1,000 ms  (never exceeded)

  Asymmetry matters: a dependency that is genuinely slower (reporting, export)
  gets a longer timeout than an interactive one. A global default timeout is
  either useless or harmful.
```

### Timeout Coordination Failure

```
  If downstream timeouts EXCEED the caller's:
    service does work nobody is waiting for  -> wasted capacity
    and under load, capacity waste becomes queueing becomes timeout

  P(work is wasted) = probability the caller times out first
  Under load this rises sharply, which is why wasted work worsens load.
```

## Retry Amplification and Duplication Rate

```
  amplification = client_retries * service_retries * gateway_retries

  3 * 3 = 9x
  5 * 3 = 15x

  retry_probability (retry budget, standard):
    retries <= 10% of total requests
  -> a system may retry at most 1 in 10 requests
  -> cap retries per request at 2-3, with jitter
```

### Retry Duplication Rate on Non-Idempotent Operations

```
  A POST /payments is sent once, times out at 800 ms of a 900 ms operation,
  and is retried.

  P(duplication) = P(timeout at client) * P(operation actually completed)

  If p99 of the operation is 1,500 ms and the client times out at 1,000 ms:
    a non-trivial fraction of timeouts correspond to COMPLETED operations
    -> each retry is a real duplicate charge
```
This is the arithmetic behind "never retry a non-idempotent request without an
idempotency key".

## Saga Compensation Probability

```
  n steps, per-step failure p, per-compensation failure q:

  P(any step fails)            = 1 - (1 - p)^n
  P(a compensation fails)      ~= 1 - (1 - p*q)^n

  n = 8, p = 0.01, q = 0.05:
    P(any failure)      = 7.7%
    P(compensation fails) = 1 - (1 - 0.0005)^8 = 0.4%
```
0.4% of sagas need human intervention. At 10,000 checkouts/day with a 4-step
saga, that is ~3 unrecoverable sagas per day. **You need a reconciliation
queue and someone who looks at it.** Design it in from the start.

## Partition Key and Hot Service Arithmetic

```
  Requests split across services by access frequency:
    catalog reads  60%
    order writes   20%
    payments       10%
    search          5%
    recommendations 5%

  scaling independently: catalog needs most capacity
  scaling as a monolith: sized for TOTAL throughput, so catalog is
                        over-provisioned relative to its share and
                        payments is under-provisioned

  cost saving from independent scaling:
    monolith: 100 capacity units for 100 rps
    microservices: 60 + 20 + 10 + 5 + 5 = 100 units
    -> no saving in THIS distribution!

  saving comes from different SCALING CURVES and from dev/staging parity,
  not from splitting a proportional load.
```
Be honest about this in a design review: independent scaling saves money only
when services have genuinely different resource profiles or scale schedules.
Otherwise you paid distributed-systems cost for nothing.

## Distributed Monolith Cost

```
  N services in a serial critical chain, each needing a deploy for a change:
    coupling probability ≈ 1 - (1 - 1/T)^N   for deploy interval T
    N = 20 services, T = 2 weeks:
      P(a change requires a coordinated multi-service deploy) is high
    effective deploy frequency drops toward:
      1 deploy / (N * T)  in the worst case = 1 per 20*2 weeks

  Rule of thumb: if a typical change touches more than 2-3 services,
  you have a distributed monolith.
```

## Data Ownership Test

```
  For each pair of services (A, B), count shared tables:

  shared_tables(A,B) = 0  ->  genuine boundary, independent deploy possible
  shared_tables(A,B) > 0  ->  distributed monolith; every schema change
                              becomes a coordinated release

  target: 0 everywhere. Measure this; do not assume it.
```

## Observability Cardinality Across Services

```
  Services S = 40, routes per service 20, statuses 5:
    series = 40 * 20 * 5 = 4,000   -- fine

  add instance_id (20 pods):
    80,000   -- high but manageable

  add request_id:
    80,000 * 100,000 rps  -> catastrophic; the metrics backend dies,
                             taking alerting for all 40 services with it
```
Request and user ids belong in logs and traces, never in metric labels.

## Migration Effort Per Capability

```
  Effort is dominated by data sharing, not by code.

  difficulty ranking:
    read-only table extraction          1x
    single-writer table extraction      3x
    dual-write + backfill + verify     6x
    shared table split across services  10x+

  A migration plan that does not name the tables it will move, in this order,
  is not a plan.
```

## Deployment Frequency and Change Failure Rate

```
  Monolith:   50 engineers, 1 deploy per 2 weeks, change failure rate ~15%
  Microservices: 7 services, each deploys 3x/week, CFR ~5%

  The win is 3*7 = 21 deploys/week vs 0.5/week = 42x deployment frequency
  IF the CFR improvement holds. It does not hold if the architecture is a
  distributed monolith, which is why CFR is the metric to watch alongside
  frequency.
```