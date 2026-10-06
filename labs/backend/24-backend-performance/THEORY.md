# Theory: Backend Performance

## The Metrics That Matter

Throughput (requests/second) and latency (ms/request) trade against each
other, and the mean lies. Report distributions: p50 paints the happy path,
p95/p99 expose queueing, GC pauses, and upstream retries. A p99 of 2 s on a
service with a 5 s client timeout is worse than it looks, because those
requests consume every pooled resource while the client gives up and the
caller retries — the retry amplifies load onto an already-saturated service.
This is why production performance discussions start with tail latency and
error rate, not averages.

## Where Time Goes

Every backend request spends time in: network hops, serialization, the
framework pipeline, business logic, and data access. Profiling usually
reveals the same suspects:

- **N+1 queries**: ORM touches one row then lazy-loads a collection per row —
  the classic JPA trap fixed with `JOIN FETCH`/entity graphs/`@EntityGraph`.
- **Connection pool exhaustion**: HikariCP sized smaller than the working set
  serializes requests; sized larger than the database, it overloads the DB.
- **Lock contention**: a single `synchronized` cache, a hot DB row, or a
  config refresh that stalls all request threads.
- **Serialization**: Jackson with deep graphs and `FAIL_ON_UNKNOWN` retries;
  replacing with a flatter DTO often buys 2–5x.
- **GC pauses**: allocation churn in hot paths — boxing, stream intermediates,
  string concatenation — surfaces as multi-hundred-ms p99 spikes on small
  heaps.

## Caching

Caching is the highest-leverage optimization and the most error-prone.
Layers: HTTP/CDN, in-process (Caffeine), distributed (Redis), and database
buffer pool. Rules that keep it safe: TTLs plus explicit invalidation on
write, never cache error responses, don't let the cache become a second
source of truth (it must be rebuildable), and watch for stampedes — a popular
key expiring under load triggers 10k concurrent misses against the database;
jitted TTLs and single-flight/request coalescing fix it.

## Concurrency and Backpressure

Latency under load is governed by queueing theory: a service at 80% CPU has
2x the awaiting at 90%. Beyond Little's law constraints, the practical
levers: bounded thread pools per dependency (not one global pool), async
I/O for fan-out calls, and explicit backpressure — bounded queues that
shed load fast rather than unbounded ones that OOM slowly. Timeouts on every
downstream call, with retries only for idempotent operations and only with
jitter + budgets.

## JVM Tuning

- G1GC is the production default; watch `Pause Young`/`Pause Full` metrics.
  A service with a stable p99 until memory crosses a threshold is almost
  always promotion-rate-driven, fixed by reducing allocation, not heap size.
- `-Xms == -Xmx` avoids resize pauses.
- Patterns that look like performance: pre-size collections, primitive
  collections (fastutil) in hot loops, avoid `Optional`/streams on per-row
  paths — but measure first; premature allocation tweaks cost readability
  for single-digit percentages.

## Measurement Discipline

Optimize in this order: fix the algorithm (O(n²) → O(n log n)), remove the
N+1, cache, then tune the runtime. Profile with async-profiler/honest
flamegraphs rather than `System.nanoTime` soup. Benchmark with
JMH + profilers. A microbenchmark without `@BenchmarkMode(Mode.AverageTime)`,
warmup, and dead-code elimination guards is noise.

## Failure Modes in Production

- **Retry storms**: no client deadline or retry budget; a slow dependency
  turns into self-inflicted DDoS.
- **Cache avalanche**: a Redis failover drops all entries; every request
  hits the database; the DB falls over too.
- **Thread pool mismatch**: Tomcat accepts 200 threads, HikariCP hands out
  10 connections — 190 threads park waiting on the pool, inflating latency
  and memory.
- **Metric blindness**: dashboards tracking CPU but not allocation rate,
  or p99 but not the deploy that correlates with the regression.

## References

- "Java Performance: The Definitive Guide" — Scott Oaks
- HikariCP, G1GC, and JMH official documentation
