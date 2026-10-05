# Real-World Project — API Composition

## Scenario

A travel booking website displays a personalized dashboard for each user,
combining data from flight search, hotel recommendations, user profile,
booking history, and loyalty program services. The dashboard must load
in under 2 seconds despite aggregating from 5+ microservices, each with
different response formats and reliability characteristics.

## System Overview

The API composition layer aggregates data from multiple services:

| Service | Data | Latency | Reliability |
|---------|------|---------|-------------|
| User Service | Profile, preferences | 50ms | 99.99% |
| Flight Service | Search results, prices | 500ms | 99.9% |
| Hotel Service | Recommendations | 300ms | 99.9% |
| Booking Service | History, upcoming trips | 100ms | 99.99% |
| Loyalty Service | Points, tier status | 80ms | 99.95% |
| Review Service | Ratings, reviews | 200ms | 99.5% |

## Architecture Decisions

### Composition Strategy
- **Parallel aggregation** — fetch from all services concurrently
- **Timeout management** — per-service timeouts with graceful degradation
- **Partial failure handling** — return available data when services fail
- **Response merging** — combine data into unified client format

### Performance Optimization
- **Caching** — cache individual service responses (short TTL)
- **Request batching** — batch calls to the same service
- **Lazy loading** — defer non-critical data to secondary requests
- **CDN caching** — cache composed responses at CDN edge

### Reliability
- **Circuit breakers** — prevent cascading failures
- **Fallback data** — return cached or default data on failure
- **Retry with backoff** — retry transient failures
- **Health checks** — monitor service health and adjust composition

## Implementation Phases

### Phase 1: Foundation
1. Implement composition layer with parallel fetching
2. Add per-service timeout handling
3. Implement basic response merging
4. Add error handling and logging

### Phase 2: Optimization
5. Implement response caching
6. Add request batching
7. Implement lazy loading for non-critical data
8. Add CDN caching for composed responses

### Phase 3: Reliability
9. Add circuit breakers for each service
10. Implement fallback data strategies
11. Add retry with exponential backoff
12. Implement health check integration

### Phase 4: Operations
13. Add composition-level monitoring
14. Implement cache invalidation strategies
15. Add A/B testing support in composition
16. Build composition analytics dashboard

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Microsoft — API Gateway Pattern**: https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation
  Microsoft's Azure architecture center guidance on gateway aggregation
  and API composition patterns, including caching and reliability strategies.

- **GraphQL — Apollo Federation**: https://www.apollographql.com/docs/federation/
  Apollo Federation documentation on composing multiple GraphQL services
  into a unified API, an alternative approach to REST API composition.

## Success Metrics

- Dashboard load time: p99 under 2 seconds
- Composition cache hit rate: over 60%
- Partial failure rate: under 1% of requests
- Zero full dashboard failures due to single service outage
- User satisfaction: over 90% positive feedback

## Lessons from Production

1. **Cache aggressively but carefully** — stale data is often worse
   than no data; use short TTLs and invalidate on changes.

2. **Design for partial failure** — services will fail; the composition
   layer must gracefully degrade and return whatever data is available.

3. **Monitor composition performance** — the composition layer can
   become a bottleneck; monitor and optimize continuously.

4. **Version your composed APIs** — clients depend on the composition;
   version changes carefully to avoid breaking clients.
