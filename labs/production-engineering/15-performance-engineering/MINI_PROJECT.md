# Lab 15: Performance Engineering & Load Testing — Mini Project

## Project: `PerfLab` — Profile a Service Under Load, Find the Bottleneck, Fix It, Prove the Capacity

**Time**: 12–16 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, k6 (open-loop) or Gatling, async-profiler, JFR/VisualVM, PostgreSQL (with `pg_stat_statements`), Docker Compose, Prometheus + Grafana, JMH for micro-benchmarks

Take one service with several realistic performance defects, measure it correctly, find each defect with evidence, fix them, and publish a report with capacity numbers and a CI gate.

---

## Part 1 — The service

```
[k6 open-loop] → [catalog-api:8080] ──JDBC──→ [postgres:5432]
                        │
                        └──HTTP──→ [recommendations (WireMock, rate-limited)]
```

Deliberate defects, none of them obvious from reading the code:

| # | Defect | Where |
|---|---|---|
| 1 | N+1 on the list endpoint (lazy-loaded category per row) | `CatalogService.list` |
| 2 | String concatenation in a loop in the response mapper | `ProductMapper` |
| 3 | Un-indexed `WHERE status = ?` filter | migration |
| 4 | Connection pool sized at 200 against a downstream with 50 capacity | `application.yml` |
| 5 | Log statement formatting an entire object at INFO | `CatalogService` |
| 6 | Retry loop around the recommendations call with no budget | `RecommendationClient` |

**Deliverable**: `DEFECTS_HYPOTHESIS.md` — before measuring anything, list your six hypotheses with the metric that would confirm each one. Then measure and mark each confirmed/refuted. (This exercises the discipline; the hypothesis list will not be perfect, which is the point.)

---

## Part 2 — A load test you can defend

### 2.1 Open-loop profile (k6)

```javascript
// load.js — arrival rate, NOT per-virtual-user iteration
import { check } from 'k6';
import http from 'k6/http';

export const options = {
  scenarios: {
    catalog: {
      executor: 'ramping-arrival-rate',   // constant arrival rate = open loop
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 300,
      maxVUs: 1500,
      stages: [
        { target: 200,  duration: '3m' },   // warm-up + ramp
        { target: 500,  duration: '5m' },
        { target: 800,  duration: '5m' },
        { target: 1200, duration: '5m' },
        { target: 1600, duration: '5m' },   // expect the plateau here
        { target: 2000, duration: '5m' },   // expect degradation past it
      ],
      gracefulStop: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(99)<300', 'p(99.9)<800'],
    http_req_failed:   ['rate<0.01'],
    dropped_iterations: ['count==0'],       // open loop: dropped iterations = requests we could not send
  },
  summaryTrendStats: ['min','med','avg','p(90)','p(95)','p(99)','p(99.9)','max'],
};

const BASE = __ENV.BASE_URL || 'http://catalog-api:8080';
export default function () {
  const res = http.get(`${BASE}/api/v1/products?status=ACTIVE&limit=100`, {
    tags: { endpoint: 'list' },
    timeout: '10s',
  });
  check(res, { 'status 200': (r) => r.status === 200 });
}
```

Two things to get right and to state in the report:
- `ramping-arrival-rate` keeps the *arrival rate* fixed regardless of latency, so a stall does not reduce load — coordinated omission is avoided by construction.
- `dropped_iterations` counts requests the generator could not issue on time. Any non-zero value is a capacity signal in its own right.

### 2.2 Environment ratio table

```markdown
| Resource | Production | Test | Ratio matched? |
|---|---|---|---|
| CPU cores | 8 | 16 | ✅ utilisation target matched |
| CPU per request | 4 ms | ? | measured in step 3 |
| Memory per request | ~1 KB | ? | measured |
| DB connections | 100 (5 services) | ? | capped to match |
| Network RTT to app | 1.5 ms | 0.1 ms | ⚠ shape with `tc netem` |
| Network RTT to DB | 1.0 ms | 0.1 ms | ⚠ shape |
| Data volume | 8M products | 800k products | ⚠ load real volume |
| Cache hit ratio | 0.82 | ? | measured, tune to match |
```

Add network shaping so the environment ratio is honest:

```bash
# inside the container, add realistic RTT and jitter
tc qdisc add dev eth0 root netem delay 1.5ms 0.4ms distribution normal
```

And load realistic data (a scaled copy of production's size and skew), including hot keys:

```bash
python3 generate_data.py --rows 8_000_000 --hot-keys 50 --skew zipf
```

### 2.3 Warm-up and repetition

```bash
k6 run --out json=results-1.json load.js   # 5 min warm-up at target, discarded
k6 run --out json=results-1.json load.js   # measured run 1
k6 run --out json=results-2.json load.js   # measured run 2
k6 run --out json=results-3.json load.js   # measured run 3
```

Report median and spread. A claimed improvement smaller than the spread is not an improvement.

**Deliverable**: `TEST_METHODOLOGY.md` — the profile, the arrival-rate semantics, the warm-up policy and how you justified it, the environment ratio table with the two shape fixes, the three runs with median and spread, and a statement of what this test can and cannot tell you.

---

## Part 3 — Establish the baseline

Record per load level:

```markdown
| Offered rps | Achieved rps | p50 | p99 | p99.9 | errors | dropped | DB queries/s | CPU (app) | CPU (db) | pool pending |
|---|---|---|---|---|---|---|---|---|---|---|
```

Then compute:

```
knee = smallest level where Δthroughput/Δload < 0.2
safe_capacity = 0.7 × peak_throughput
L = λ × W  at the target operating point
```

**Deliverable**: `BASELINE.md` — the table, the knee, the peak, the safe capacity, and the concurrency at the target.

---

## Part 4 — Profiling under load

### 4.1 async-profiler

```bash
PID=$(pgrep -f catalog-api)

# CPU: where is the time going at 70% of the safe capacity?
asprof -d 120 -e cpu -f /tmp/cpu.html  --traces 20  "$PID"
asprof -d 120 -e alloc -f /tmp/alloc.html "$PID"     # allocation rate
asprof -d 120 -e lock -f /tmp/lock.html --cstack 20 "$PID"
asprof -d 120 -e wall -f /tmp/wall.html "$PID"      # where threads actually wait
```

Fold the output and read it properly:

```bash
asprof -d 120 -e cpu -o collapsed --traces 20 "$PID" > cpu.collapsed
flamegraph.pl > cpu.svg cpu.collapsed        # flamegraph.pl from Brendan Gregg's FlameGraph repo
```

Reading rules you write down and follow:
- **Width = time.** Find the widest frame, not the deepest.
- Wide frames *under* a blocking call or a lock are the interesting ones.
- Narrow stacks are noise.

### 4.2 JFR for events and long runs

```bash
java -XX:StartFlightRecording=duration=600s,filename=/tmp/rec.jfr,settings=profile \
     -XX:+HeapDumpOnOutOfMemoryError -jar app.jar

jfr summary /tmp/rec.jfr
jfr print --events jdk.GCPhasePause,jdk.JavaMonitorEnter,jdk.ThreadPark \
      /tmp/rec.jfr | head -100
jfr print --events jdk.ObjectAllocationSample /tmp/rec.jfr | grep -c 'objectClass'
```

### 4.3 Where the JVM profile is blind

```java
// Correlate wall time per phase. If W_dep dominates, your Java code is not the bottleneck.
@Timed(value = "catalog.request", percentiles = {0.5, 0.99, 0.999})
public List<ProductDto> list(...) {
    var t0 = System.nanoTime();
    var rows = repo.findByStatus(status);            // W_db
    var t1 = System.nanoTime();
    var recs = recommendations.forProducts(ids);      // W_dep
    var t2 = System.nanoTime();
    return map(rows, recs);                            // W_map
}
```

`W_total` vs `W_db + W_dep + W_map` tells you where to look. If `W_dep` is 70% of the total, profiling the Java code further is wasted effort.

### 4.4 Database side

```sql
-- pg_stat_statements: total time by query
SELECT calls, round(mean_exec_time,2) AS mean_ms, round(total_exec_time/1000,1) AS total_s,
       left(query, 80)
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 15;

-- is the hot filter indexed?
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM products WHERE status = 'ACTIVE' ORDER BY created_at DESC LIMIT 100;
```

Expect: the list query called ~50,000 times/min (the N+1), each cheap individually, cumulatively dominating; and a `Seq Scan` on `products` for the status filter.

**Deliverable**: `PROFILE.md` — the flame graph (or its top-10 collapsed stacks with percentages), the allocation hot spots, the phase-timing breakdown, the top database queries, and a one-paragraph statement of where the time is.

---

## Part 5 — Fix and verify

Fix in order of Amdahl (largest fraction first), one change per run:

**Fix 1 — N+1:**

```java
@Query("""
    select new com.example.catalog.dto.CategoryDto(c.id, c.name)
    from Category c where c.id in :ids
    """)
List<CategoryDto> findAllByIds(@Param("ids") Collection<Long> ids);

public List<ProductDto> list(String status, int limit) {
    List<Product> rows = repo.findTopByStatusOrderByCreatedAtDesc(status, PageRequest.of(0, limit));
    var categories = categoryRepo.findAllByIds(rows.stream().map(Product::getCategoryId).toSet())
                                 .stream().collect(toMap(Category::getId, CategoryDto::from));
    return rows.stream().map(p -> ProductMapper.toDto(p, categories.get(p.getCategoryId()))).toList();
}
```

**Fix 2 — allocation in the mapper:**

```java
// Before: string concat in a loop + autoboxing + a HashMap per row
// After: single StringBuilder, primitive accumulation, one pre-sized map
static String sku(List<Product> products) {
    var sb = new StringBuilder(products.size() * 8);
    for (Product p : products) { if (sb.length() > 0) sb.append(','); sb.append(p.getSku()); }
    return sb.toString();
}
```

**Fix 3 — the index:**

```sql
SET lock_timeout = '2s';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_status_created
  ON products (status, created_at DESC);
ANALYZE products;
```

**Fix 4 — pool sizing:**

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 45      # downstream capacity 50, safety margin, not 200
      minimum-idle: 10
      connection-timeout: 2000
      leak-detection-threshold: 5000
```

**Fix 5 — logging:**

```java
// Before: log.info("listing {}", products)   → formats every product at INFO
// After:
if (log.isDebugEnabled()) { log.debug("listing {} products", products.size()); }
log.info("listed {} products in {} ms", products.size(), elapsedMs);
```

**Fix 6 — retry budget:**

```java
@Retryable(retryFor = {TimeoutException.class}, maxAttempts = 2,
           backoff = @Backoff(delay = 50, multiplier = 2, random = true))
@CircuitBreaker(name = "recommendations", fallbackMethod = "empty")
public List<Recommendation> forProducts(List<Long> ids) { ... }
```

Re-run the full profile after each fix and record the incremental effect.

**Deliverable**: `FIXES.md` — per fix: the fraction of time it addressed, the before/after throughput and p99, the CPU-per-request change, and the spread across three runs.

---

## Part 6 — Project the capacity and the cost

```
cpu_per_request = cpu_time_total / requests       (measured, after fixes)
safe_rps_per_pod = cores_per_pod × U_target / cpu_per_request
pods = ceil(λ_peak_with_growth / safe_rps_per_pod)
pods_with_failure_tolerance = ceil(λ_peak_with_growth / (safe_rps_per_pod × (1 − N/N_total)))
```

Produce a before/after table:

```markdown
| Metric | Before | After |
|---|---|---|
| Peak throughput | 2,440 rps | 3,900 rps |
| CPU per request | 4.1 ms | 1.7 ms |
| DB queries per list request | 101 | 2 |
| p99 at 1,200 rps | 890 ms | 140 ms |
| Pods for peak 9,000 rps with N+1 | 53 | 33 |
| Annual compute cost | $114,480 | $71,280 |
```

**Deliverable**: `CAPACITY.md` — the model, the before/after table, and the dollars.

---

## Part 7 — Soak and stress

### Soak (4 hours at 70% of safe capacity)

Watch for drift: heap after full GC, live-set growth, thread count, connection count, log file growth, DB table/index bloat, cache hit ratio.

```bash
watch -n 60 'jstat -gcutil <pid> 1000 1; ls /proc/<pid>/fd | wc -l'
```

**Deliverable**: a soak table at 0/30/60/120/180/240 minutes for heap-after-GC, thread count, FD count, log size, and DB connections, with a verdict on leak vs stable.

### Stress (past the knee)

```javascript
{ executor: 'ramping-arrival-rate', startRate: 1000, timeUnit: '1s', preAllocatedVUs: 2000, maxVUs: 8000,
  stages: [{ target: 4000, duration: '5m' }, { target: 8000, duration: '5m' }] }
```

Record: where errors begin, whether the service degrades or collapses, whether it recovers when load is removed, and the CPU/GC behaviour at the plateau.

**Deliverable**: the stress curve with the collapse point, the recovery test, and the failure modes observed.

---

## Part 8 — CI performance gate

```yaml
# .github/workflows/perf.yml
perf-gate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: ./mvnw -B -q verify
    - name: JMH micro-benchmark guard
      run: |
        ./mvnw -B -q -pl core -am test -DbenchmarkMode=ci
        # fails if a benchmark regresses > 5% vs the committed baseline
    - name: Short load test against stubs
      run: |
        docker compose up -d db stub
        k6 run --quiet -e BASE_URL=http://localhost:8080 -e SHORT=1 ci-load.js
        # ci-load.js asserts: p99 < 250ms, errors < 0.5%, throughput floor
```

**Acceptance**: a PR that adds an N+1 or removes an index fails the gate; a PR that improves throughput by 20% passes and records the new baseline.

---

## Acceptance Criteria

- [ ] `DEFECTS_HYPOTHESIS.md` written before measuring, with each hypothesis marked confirmed/refuted afterwards.
- [ ] `TEST_METHODOLOGY.md` documents an open-loop arrival-rate profile, a justified warm-up, three runs with spread, and an environment ratio table with the network shaped.
- [ ] `BASELINE.md` gives the load curve, the knee, the peak, and the safe capacity with `L = λ × W`.
- [ ] `PROFILE.md` names where the time is, with flame graph or collapsed stacks, allocation hot spots, phase timings, and the top database queries.
- [ ] All six defects fixed, each measured separately, with before/after throughput, p99, and CPU-per-request.
- [ ] `CAPACITY.md` projects pods for peak with growth and failure tolerance, and shows the cost delta.
- [ ] Soak table over 4 hours with a leak/stable verdict.
- [ ] Stress curve with the collapse point and a recovery test.
- [ ] CI perf gate blocks a deliberately introduced N+1 and passes a real improvement.

---

## Stretch

- Write a JMH micro-benchmark for the mapper and compare its median against the in-situ distribution to demonstrate why micro-benchmarks miss tail effects.
- Add a chaos component: while at peak load, add 500 ms of latency to PostgreSQL and observe whether the service degrades or collapses; connect the result to pool sizing.
- Build a capacity model for a second service with a *shared* dependency and show that the two services cannot both be at peak.
- Convert the load test into a scheduled nightly job that tracks throughput and p99 trends and alerts on a regression, turning performance into a monitored property.
