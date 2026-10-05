# Real-World Project — Circuit Breaker Pattern

## Scenario

A food delivery platform coordinates between restaurants, delivery
drivers, payment processors, and mapping services. During peak hours,
external services (payment processor, mapping API) occasionally become
slow or unavailable. Without circuit breakers, these failures cascade:
threads block waiting for timeouts, connection pools exhaust, and the
entire platform becomes unresponsive. The platform implements circuit
breakers on all external service calls.

## System Overview

The platform implements circuit breakers for all external dependencies:

| Service | Failure Threshold | Timeout | Fallback |
|---------|------------------|---------|----------|
| Payment Processor | 5 failures in 60s | 30s | Queue for retry |
| Mapping API | 10 failures in 60s | 15s | Cached routes |
| Restaurant API | 5 failures in 60s | 30s | Show cached menu |
| Notification Service | 10 failures in 60s | 15s | Log for later |
| Fraud Detection | 3 failures in 60s | 30s | Manual review |

## Architecture Decisions

### Circuit Breaker Implementation
- **Resilience4j** (Java) / **Polly** (.NET) / **Hystrix** (legacy)
- **Per-service circuit breakers** — each external dependency has its own
- **Sliding window** — count failures in a time window, not just consecutive
- **Configurable thresholds** — different services have different tolerances

### State Management
- **Closed**: normal operation, track failures in sliding window
- **Open**: fail fast, return fallback, start timeout timer
- **Half-Open**: allow limited test requests, close on success

### Fallback Strategies
- **Cached data**: return last known good response (menus, routes)
- **Queue for retry**: defer processing (payments, notifications)
- **Degraded mode**: reduced functionality (manual fraud review)
- **Default response**: graceful error message to users

### Monitoring and Alerting
- **Metrics**: circuit state, failure rate, fallback usage
- **Alerting**: notify on circuit open, track recovery time
- **Dashboards**: real-time view of all circuit breakers
- **Runbooks**: procedures for manual circuit breaker management

## Implementation Phases

### Phase 1: Foundation
1. Implement circuit breaker library wrapper
2. Add circuit breaker to payment processor calls
3. Implement fallback for payment failures
4. Add metrics and alerting

### Phase 2: Core Services
5. Add circuit breaker to mapping API calls
6. Implement cached route fallback
7. Add circuit breaker to restaurant API
8. Implement cached menu fallback

### Phase 3: Remaining Services
9. Add circuit breaker to notification service
10. Implement queue-based fallback
11. Add circuit breaker to fraud detection
12. Implement manual review fallback

### Phase 4: Operations
13. Build circuit breaker dashboard
14. Implement automated recovery testing
15. Add circuit breaker configuration management
16. Create operational runbooks

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Martin Fowler — Circuit Breaker**: https://martinfowler.com/bliki/CircuitBreaker.html
  Martin Fowler's overview of the circuit breaker pattern, explaining
  the motivation, state machine, and implementation considerations.

- **Netflix — Hystrix**: https://github.com/Netflix/Hystrix
  Netflix's Hystrix library (now in maintenance mode), the original
  circuit breaker implementation for Java, with extensive documentation
  on circuit breaker patterns and resilience.

## Success Metrics

- Circuit breaker activations: monitored and alerted
- Fallback usage rate: under 5% of requests
- Recovery time: under 5 minutes for transient failures
- Zero cascading failures during external service outages
- User-facing error rate: under 1% during degraded operation

## Lessons from Production

1. **Tune thresholds carefully** — too sensitive causes false positives;
   too insensitive defeats the purpose. Monitor and adjust based on data.

2. **Fallbacks are as important as the circuit breaker** — a circuit
   breaker without a good fallback just moves the problem; design
   fallbacks that provide real user value.

3. **Test circuit breakers regularly** — they only matter when failures
   happen; use chaos engineering to test them under real conditions.

4. **Monitor half-open state** — frequent half-open transitions indicate
   a flapping service; alert on this pattern.
