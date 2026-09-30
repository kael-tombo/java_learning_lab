# PRODUCTION SCENARIOS: Debugging & Profiling
## Lab 03 | Production Engineering Academy

---

## Scenario 1: The Monday Slowdown Mystery

### Context
Order processing service. Every Monday at ~11 AM, p99 latency climbs from 50ms to 3000ms. No errors in logs. By 5 PM it's back to normal. Happens every Monday for 3 weeks.

### Investigation

**Step 1: Correlate with Monday patterns**
- Monday 11 AM: Marketing team runs weekly batch report (fetches 2M order records)
- The batch runs SQL: `SELECT * FROM orders WHERE created_at > '2020-01-01'` — full table scan!

**Step 2: Confirm with jstat**
```bash
jstat -gcutil $(pgrep java) 5000 30
# S0   S1    E      O      M    YGC  YGCT  FGC  FGCT    GCT
# 0.0  36.5  92.2   94.1  97.8   890  8.23   12  48.234  56.46
#                   ^^^^   ^^^
# Old Gen: 94.1% — nearly full!
# FGC: 12 Full GCs!
# FGCT: 48 seconds in Full GC! — every Full GC = service freezes
```

**Step 3: Heap dump shows the cause**
```
Eclipse MAT - Dominator Tree:
  ArrayList [1,987,432 elements] - 2.4 GB retained heap  ← THE PROBLEM
    └── Order objects (2M instances)
```

**Step 4: Flame graph shows the reporter**
```
async-profiler -e alloc → Allocation flamegraph:
  45% of allocations from:
    com.company.ReportService.generateWeeklyReport()
      → orderRepository.findAllOrders()  ← fetches 2M rows into memory!
```

### Root Cause
`orderRepository.findAllOrders()` loaded **all 2M orders into memory** at once. This caused massive Old Gen pressure → repeated Full GC → 3s pauses.

### Fix
```java
// Before: loads 2M rows
List<Order> all = orderRepository.findAllOrders();
generateReport(all);

// After: stream with pagination
try (Stream<Order> stream = orderRepository.streamAllOrders()) {  // JPA streaming cursor
    stream.forEach(order -> reportBuilder.addOrder(order));
}
// OR: process in batches of 1000
int page = 0;
List<Order> batch;
do {
    batch = orderRepository.findAll(PageRequest.of(page++, 1000)).getContent();
    reportBuilder.addBatch(batch);
} while (!batch.isEmpty());
```

**Result**: Monday latency: 50ms (no change). Batch report: streaming, no heap impact.

---

## Scenario 2: The Memory Leak That Lived for 6 Months

### Context
Customer portal. Memory usage grows ~50MB/day. Service OOMs every 72 hours and restarts. Monday morning restarts mask the problem. Running for 6 months before investigated.

### Investigation

**Heap dump over time (automated snapshots every 24h)**:
```
Day 1: Heap 2.1GB (normal)
Day 2: Heap 2.4GB
Day 3: Heap 2.6GB (+500MB in 24h — consistent growth)
```

**Eclipse MAT — Dominator Tree on Day 3 dump**:
```
com.company.cache.ProductCache  — 1.8 GB retained
  └── HashMap<Long, ProductDetails>
       ├── 47,832 ProductDetails entries
       └── Each ProductDetails contains:
            └── byte[] thumbnailImage  ← 40KB each!
                47,832 × 40KB = 1.9GB
```

**Path to GC Root**:
```
ProductCache.cache (HashMap) → static field → productCache (static)
                                                       ↑
                              com.company.AppConfig.productCache (static field)
```

### Root Cause
`ProductCache` was a static field with no eviction policy. 47,000 products × 40KB thumbnail cache = 1.9GB. Products added over 6 months, never evicted.

### Fix
```java
// Before — unbounded cache
@Component
public class ProductCache {
    private static final Map<Long, ProductDetails> cache = new HashMap<>();

    public ProductDetails get(Long id) {
        return cache.computeIfAbsent(id, this::loadFromDb);
    }
}

// After — Caffeine with size limit and TTL
@Component
public class ProductCache {
    private final Cache<Long, ProductDetails> cache = Caffeine.newBuilder()
        .maximumSize(10_000)                // Max 10K products
        .expireAfterAccess(1, TimeUnit.HOURS)  // Evict if not accessed 1h
        .recordStats()                      // Enable hit/miss metrics
        .build();

    public ProductDetails get(Long id) {
        return cache.get(id, this::loadFromDb);
    }
    // Exposes: cache.stats().hitRate(), missRate(), evictionCount()
}
```

---

## Scenario 3: CPU Spike Every 15 Minutes (Scheduled Job)

### Context
API service. Every 15 minutes, CPU jumps from 20% to 95% for 30-45 seconds. All API latency degrades during this window. No clue what's causing it.

### Investigation

**Timeline correlation**: CPU spikes at :00, :15, :30, :45 of each hour. That's cron-like.

**async-profiler CPU flamegraph** captured during spike:
```
Flame graph shows (from bottom, 60% of width):
  com.company.analytics.MetricsAggregator.aggregate()
    → StreamSupport.stream()
      → IntStream.range().forEach()
        → HashMap.computeIfAbsent()
          → ... computing metrics for 500K events
```

**Root Cause**: Scheduled task runs every 15 minutes, processes 500K accumulated events synchronously on the main thread pool. Starves API request threads.

### Fix
```java
// Before — runs in main thread pool, starves API threads
@Scheduled(fixedRate = 15, timeUnit = TimeUnit.MINUTES)
public void aggregateMetrics() {
    doHeavyAggregation();  // Runs for 45 seconds!
}

// After — dedicated thread pool for background jobs
@Configuration
public class SchedulerConfig {
    @Bean
    public TaskScheduler analyticsScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(2);
        scheduler.setThreadNamePrefix("analytics-");
        scheduler.setDaemon(true);
        return scheduler;
    }
}

@Scheduled(fixedRate = 15, timeUnit = TimeUnit.MINUTES)
@Async("analyticsScheduler")  // Runs in isolated pool — doesn't touch API threads
public void aggregateMetrics() {
    doHeavyAggregation();
}
```

---

## Scenario 4: "Slow" Service That Wasn't Slow

### Context
Recommendation service. p99 = 2 seconds. Profiling shows no slow code. GC logs show < 50ms pauses. Developers baffled.

### Investigation

**Distributed tracing** (Jaeger):
```
Trace ID: abc123 — Total: 2100ms

  recommendation-service.getRecommendations  — 48ms (fast!)
  
  api-gateway → recommendation-service  — 2052ms
```

The service itself was 48ms. But **the client was waiting 2 seconds**. Gap = 2004ms. Where?

**Checked network**: Fine.

**Checked TCP connection reuse**:
```bash
# On the caller (order-service):
ss -s  # Socket stats
netstat -an | grep TIME_WAIT | wc -l  # 4892 connections in TIME_WAIT!
```

**Root Cause**: `order-service` was creating a new HTTP connection for **every request** to recommendation-service (no connection pooling). Each new connection: TCP handshake (1 RTT) + TLS handshake (1-2 RTT) = 2 seconds overhead. Service was fast; TCP handshake was slow.

### Fix
```java
// Before — new connection per request
RestTemplate restTemplate = new RestTemplate();  // No connection pool!

// After — pooled HTTP client
@Bean
public RestTemplate restTemplate() {
    HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory();
    factory.setHttpClient(HttpClients.custom()
        .setConnectionManager(PoolingHttpClientConnectionManagerBuilder.create()
            .setMaxConnPerRoute(50)   // 50 connections to recommendation-service
            .setMaxConnTotal(100)     // 100 total
            .build())
        .build());
    return new RestTemplate(factory);
}
// Result: p99 drops from 2000ms to 48ms
```
