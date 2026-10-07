# Prevention Guide — Avoiding Cache Stampede Incidents

## How to Prevent Recurrence of SEV1 Cache Stampede / Database Overload

This document outlines the engineering practices, caching architecture standards, and monitoring requirements to prevent cache stampede incidents. Drawing from Meta's Memcache engineering, Google's production systems, and Amazon ElastiCache best practices.

---

## 1. TTL Management Standards

### Mandatory TTL Jitter
- ALL cache TTLs MUST include jitter of at least +/- 10%
- Jitter must be applied at write time, not read time
- Minimum TTL after jitter: 30 seconds
- Maximum TTL after jitter: no limit (as long as base TTL is reasonable)

### TTL Configuration Template
```yaml
cache:
  ttl:
    base: 300               # Base TTL in seconds
    jitter:
      enabled: true
      percentage: 0.10       # +/- 10%
      minimum: 30           # Minimum TTL after jitter
    swr:
      enabled: true
      window: 60            # Seconds to serve stale data
    xfetch:
      enabled: true
      beta: 1.0
      delta: 0.5
```

### Prohibited TTL Patterns
- Fixed TTL for all entries of a key space
- TTL set based on batch creation time (all entries expire simultaneously)
- TTL exceeding 1 hour without SRE review
- TTL of 0 (cache forever without expiration)

---

## 2. Stale-While-Revalidate (SWR) Requirements

### Mandatory SWR Rules
- All read-heavy cache operations MUST implement SWR
- SWR window must be at least 20% of base TTL
- Background revalidation must use dedicated thread pool (isolated from request threads)
- Stale data must be clearly marked (response header: `X-Cache-Stale: true`)
- SWR must not block the requesting thread

### SWR Implementation Checklist
- [ ] Asynchronous revalidation executor configured
- [ ] Thread pool size: 10 (minimum), isolated from request threads
- [ ] Stale data served immediately, revalidation runs in background
- [ ] Revalidation failures logged but never propagated to client
- [ ] SWR window exceeded → synchronous revalidation with backpressure

---

## 3. Request Coalescing Requirements

### Mandatory Coalescing Rules
- Concurrent requests for the same cache key MUST be coalesced into a single backend query
- Distributed mutex (Redis-based) required for multi-instance deployments
- Lock TTL: 5 seconds (sufficient for regeneration, short enough to avoid deadlock)
- Fallback: if lock acquisition fails, wait up to 500ms for the other request to populate cache
- Timeout fallback: query backend directly with reduced TTL (30 seconds)

### Coalescing Implementation Checklist
- [ ] Redis SET NX for distributed lock
- [ ] Lock key different from cache key (prefix: `lock:`)
- [ ] Lock auto-expiry (TTL) for deadlock prevention
- [ ] Double-check pattern (check cache again after acquiring lock)
- [ ] Spin-wait with backoff for lock waiters

---

## 4. Probabilistic Early Expiration (XFetch)

### XFetch Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `beta` | 1.0 | Higher = more aggressive early refresh |
| `delta` | 0.5 | Controls maximum refresh probability |
| Decision interval | Every read | Evaluate on each cache hit |
| Trigger | Async refresh | Never block the requesting thread |

### XFetch Integration Rules
- XFetch must NOT block the requesting thread — it only triggers async revalidation
- XFetch is complementary to SWR (use both together)
- XFetch is most effective for high-traffic keys (requested multiple times per TTL window)
- For low-traffic keys (< 1 request per TTL), SWR is sufficient

---

## 5. Rate Limiting for Cache Miss Regeneration

### Rate Limiter Configuration
```yaml
resilience4j:
  ratelimiter:
    configs:
      default:
        limitForPeriod: 500        # Max 500 regenerations per second
        limitRefreshPeriod: 1s
        timeoutDuration: 100ms
```

### Rate Limiting Rules
- Cache miss regeneration MUST be rate-limited per service instance
- Rate limit must be proportional to database connection pool size
- When rate limited: return degraded response (stale data or error)

---

## 6. Cache Warming Strategy

### Warming Triggers
| Trigger | Action | Priority |
|---------|--------|----------|
| Scheduled (every 5 min) | Warm top 1,000 popular keys | Normal |
| Traffic spike detected | Warm all keys matching spike pattern | High |
| Post-deployment | Warm all cache keys for deployed service | High |
| Breaking news event | Manual warming of news-feed keys | Immediate |

### Warming Implementation
- Warming runs asynchronously, not blocking any requests
- Warming respects TTL (does not overwrite fresh entries)
- Warming uses jitter (does not create a new stampede on cache expiry)
- Warming is idempotent

---

## 7. Backpressure and Circuit Breakers

### Database Connection Pool Protection
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 200
      minimum-idle: 50
      connection-timeout: 5000
      max-lifetime: 1800000
      leak-detection-threshold: 10000
```

### Circuit Breaker for Cache Miss DB Queries
```java
@CircuitBreaker(name = "cacheMissDbQuery", fallbackMethod = "cacheMissFallback")
public String generateFeedFromDatabase(String userId) {
    return feedRepository.generateFeed(userId);
}

public String cacheMissFallback(String userId, Throwable t) {
    // Return cached (even if stale) or error
    return getAnyCachedEntry(userId);
}
```

---

## 8. Monitoring and Alerting for Cache Stampede Prevention

### Key Metrics to Monitor
| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Cache hit rate | Redis INFO | < 90% for > 1 minute |
| Database query rate | PostgreSQL pg_stat | > 3x baseline for > 1 minute |
| Database connection pool utilization | Hikari CP | > 80% |
| Cache miss regeneration rate | Application metric | > 500/s (rate limit) |
| TTL distribution | Redis debug | > 10% entries within 1s of each other |
| SWR stale serves | Application metric | Monitor trend |

### Automated Prevention Alerts
```yaml
groups:
  - name: cache-stampede-prevention
    rules:
      - alert: CacheHitRateDrop
        expr: rate(redis_keyspace_hits_total[1m]) / (rate(redis_keyspace_hits_total[1m]) + rate(redis_keyspace_misses_total[1m])) < 0.9
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit rate dropped below 90%"

      - alert: DatabaseQueryRateSpike
        expr: rate(pg_stat_database_xact_commit[1m]) > 3 * avg_over_time(rate(pg_stat_database_xact_commit[1m])[24h:5m])
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database query rate spike detected"
```

---

## 9. Testing Requirements

### Mandatory Cache Tests
| Test | Frequency | Scenario |
|------|-----------|----------|
| TTL jitter verification | Per deployment | Verify TTL distribution is random |
| Cache stampede simulation | Weekly | Simulate simultaneous expiration of 100% of keys |
| SWR behavior test | Per deployment | Verify stale data is served during regeneration |
| Coalescing test | Per deployment | Verify concurrent requests are coalesced |
| Cache warming test | Monthly | Verify warming populates expected keys |

---

## Summary of Prevention Measures

| # | Measure | Owner | Timeline | Impact |
|---|---------|-------|----------|--------|
| 1 | TTL jitter (mandatory) | Platform Team | Immediate | Critical |
| 2 | Stale-while-revalidate | Platform Team | 1 week | Critical |
| 3 | Request coalescing | Platform Team | 2 weeks | Critical |
| 4 | XFetch algorithm | Platform Team | 3 weeks | High |
| 5 | Cache miss rate limiter | Platform Team | 1 week | High |
| 6 | Cache warming automation | Data Team | 1 month | Medium |
| 7 | Cache stampede testing | QA Team | 1 month | High |

### References
- Meta USENIX NSDI 2013: "Scaling Memcache at Facebook" — https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala
- Meta USENIX NSDI 2013: "An Analysis of Facebook Photo Caching" — (link removed)
- Google SRE Book — Chapter 22: "Managing Cascading Failures"
- Amazon ElastiCache Best Practices — https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html
- XFetch Algorithm — Vattani, Zaccarato
- Redis Documentation: "Cache Stampede Prevention" — (link removed)
