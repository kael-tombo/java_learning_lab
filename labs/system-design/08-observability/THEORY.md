# Observability - THEORY

## Overview

Observability enables understanding system behavior through metrics, logs, and traces.

## 1. Three Pillars

### Logs
- **Application Logs**: Debug, info, warn, error
- **Access Logs**: Request/response logging
- **Audit Logs**: Security events

```java
@Slf4j
@RestController
public class UserController {
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        log.info("Fetching user: {}", id);
        try {
            return userService.findById(id);
        } catch (Exception e) {
            log.error("Failed to fetch user: {}", id, e);
            throw e;
        }
    }
}
```

### Metrics
- **Counters**: Request count, error count
- **Gauges**: Current connections, queue size
- **Histograms**: Request latency, response size

```java
@Service
public class MetricsService {
    private final MeterRegistry registry;
    
    public void recordLatency(long duration) {
        Timer.builder("request.latency")
            .tag("service", "user-service")
            .register(registry)
            .record(duration, TimeUnit.MILLISECONDS);
    }
    
    public void incrementError() {
        Counter.builder("request.errors")
            .tag("service", "user-service")
            .register(registry)
            .increment();
    }
}
```

### Traces
```java
@Traced
public User getUser(Long id) {
    Span span = tracer.startSpan("getUser");
    try {
        return userService.findById(id);
    } finally {
        span.end();
    }
}
```

## 2. Distributed Tracing

### Trace Flow
```
Client → Gateway → User Service → Database
   |        |           |
   └────────┴───────────┴── Trace ID: abc123
```

### Headers
```
X-Request-ID: abc123
X-Trace-ID: abc123
X-Span-ID: 456
```

## 3. Health Checks

```java
@RestController
@RequestMapping("/actuator")
public class HealthController {
    @GetMapping("/health")
    public Health health() {
        return Health.builder()
            .status(Status.UP)
            .withDetail("database", checkDatabase())
            .withDetail("redis", checkRedis())
            .build();
    }
}
```

## 4. Alerting

```yaml
# Prometheus alerting rules
groups:
- name: service-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_errors_total[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
```

## Summary

1. **Logs**: Structured logging for debugging
2. **Metrics**: Quantitive measurements (Prometheus, Grafana)
3. **Traces**: Request flow across services (Jaeger, Zipkin)
4. **Health**: Readiness and liveness probes
5. **Alert**: Proactive monitoring with thresholds

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Monitoring Distributed Systems" (Rob Ewaschuk, Google SRE Book Ch. 6, O'Reilly 2016) — https://sre.google/sre-book/monitoring-distributed-systems — Alert on symptoms (latency/traffic/errors/saturation — the four golden signals), not causes; structure the lab's alert rules around user-visible symptoms first.
- "Monitoring Distributed Systems" (Rob Ewaschuk, Google SRE Book Ch. 6, O'Reilly 2016) — https://sre.google/sre-book/monitoring-distributed-systems — Combine white-box (logs/internal metrics) with black-box (externally-visible probes) monitoring; use this split when wiring the lab's metrics-vs-health-check exercises.
- "Monitoring Distributed Systems" (Rob Ewaschuk, Google SRE Book Ch. 6, O'Reilly 2016) — https://sre.google/sre-book/monitoring-distributed-systems — Keep paging rules simple, actionable, and novel — every page should need human intelligence; prune the lab's noisy email-style alerts into dashboards plus a small pager set.
- "Monitoring Distributed Systems" (Rob Ewaschuk, Google SRE Book Ch. 6, O'Reilly 2016) — https://sre.google/sre-book/monitoring-distributed-systems — Measure latency distributions (histogram buckets), not means, and watch tail/99th percentile as the early saturation signal; apply when the lab instruments request-latency timers.