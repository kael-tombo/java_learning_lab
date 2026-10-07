# Monitoring: API Rate Limiting

## Monitoring Architecture

Comprehensive monitoring for rate limiting effectiveness, Redis health, client behavior, and early warning of cascade failures.

## 1. Kong Rate Limiter Metrics

### Core Metrics

| Metric | Type | Description | Threshold |
|--------|------|-------------|-----------|
| `kong_http_requests_total` | Counter | Total requests by status code | N/A |
| `kong_rate_limiting_limits` | Gauge | Current rate limit per consumer | Matches config |
| `kong_rate_limiting_remaining` | Gauge | Remaining requests for current window | > 20% |
| `rate_limiter_429_total` | Counter | Count of 429 responses per consumer | < 10/hour |
| `rate_limiter_429_ratio` | Gauge | Percentage of 429 responses | < 1% |

### Prometheus Alert Rules

```yaml
groups:
  - name: api_rate_limiting
    interval: 30s
    rules:
      - alert: HighRateLimitExceeded
        expr: |
          sum(rate(kong_http_requests_total{status="429"}[5m]))
          / sum(rate(kong_http_requests_total[5m])) > 0.05
        for: 1m
        labels:
          severity: critical
          team: api-platform
        annotations:
          summary: "> 5% of API requests returning 429"
          description: "Current 429 rate: {{ $value | humanizePercentage }}"

      - alert: ConsumerRateLimited
        expr: |
          rate(kong_http_requests_total{status="429"}[5m]) > 100
        for: 2m
        labels:
          severity: warning
          team: api-platform
        annotations:
          summary: "Consumer {{ $labels.consumer }} heavily rate limited"
          description: "{{ $value }} 429s per 5 minutes"

      - alert: RateLimitRedisDown
        expr: |
          redis_up{service="redis-ratelimit"} == 0
        for: 10s
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Rate limiter Redis is DOWN"
          description: "Rate limiting will fail open (all requests allowed)"

      - alert: RateLimitRedisMemoryHigh
        expr: |
          redis_memory_used_bytes{service="redis-ratelimit"}
          / redis_memory_max_bytes{service="redis-ratelimit"} > 0.85
        for: 2m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Rate limiter Redis memory > 85%"
```

## 2. Redis Rate Limiter Monitoring

### Key Redis Metrics

```bash
# Redis INFO command monitoring
redis-cli -h redis-ratelimit INFO stats | grep -E "evicted|expired|keyspace"
redis-cli -h redis-ratelimit INFO memory | grep -E "used_memory|maxmemory"
redis-cli -h redis-ratelimit INFO cpu | grep -E "used_cpu"
```

### Grafana Dashboard: Redis Rate Limiter

**Panel 1: Memory Usage** (Gauge)
- Query: `redis_memory_used_bytes{service="redis-ratelimit"} / redis_memory_max_bytes`
- Warning: 80%, Critical: 90%

**Panel 2: Eviction Rate** (Timeseries)
- Query: `rate(redis_keys_evicted_total{service="redis-ratelimit"}[5m])`
- Threshold: 0 (any eviction is critical)

**Panel 3: Key Count** (Timeseries)
- Query: `redis_db_keys{service="redis-ratelimit"}`
- Display: total keys by namespace

**Panel 4: Operations Rate** (Timeseries)
- Query: `rate(redis_commands_total{service="redis-ratelimit"}[5m])`
- Broken down by INCR, EXPIRE, EVAL commands

## 3. Kong Gateway Monitoring

### Prometheus Integration

```yaml
# kong-prometheus-plugin.yml
plugins:
  - name: prometheus
    config:
      status_code_metrics: true
      latency_metrics: true
      bandwidth_metrics: true
      upstream_health_metrics: true
```

### Key Kong Metrics

```bash
# Check Kong status
curl -s http://localhost:8001/status

# Get rate limiter plugin status
curl -s http://localhost:8001/plugins | jq '.data[] | select(.name=="rate-limiting")'

# Check Kong node health
curl -s http://localhost:8001/health
```

### Grafana Dashboard: Kong Rate Limiter

**Panel 1: 429 Rate by Consumer** (Table)
- Query: `topk(10, sum by (consumer) (rate(kong_http_requests_total{status="429"}[5m])))`
- Display: top 10 consumers by 429 rate

**Panel 2: Rate Limit Remaining** (Heatmap)
- Query: `kong_rate_limiting_remaining`
- Color: green > 50%, yellow > 20%, red < 20%

**Panel 3: Request Latency** (Timeseries)
- Query: `kong_latency_ms{type="request"}`
- Compare: latency for 200 vs 429 responses

**Panel 4: Kong Node CPU** (Singlestat)
- Query: `avg(rate(container_cpu_usage_seconds_total{container="kong"}[5m]))`
- Warning: > 70%, Critical: > 85%

## 4. Client Usage Analytics

### Per-Client Monitoring

```sql
-- PostgreSQL analytics query
SELECT 
    client_id,
    client_name,
    tier,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE status = 429) as rate_limited_count,
    ROUND(COUNT(*) FILTER (WHERE status = 429) * 100.0 / COUNT(*), 2) as rate_limited_pct,
    MAX(request_time) as last_request
FROM api_requests
WHERE request_time > NOW() - INTERVAL '1 hour'
GROUP BY client_id, client_name, tier
ORDER BY rate_limited_pct DESC
LIMIT 20;
```

### Alert Rules for Client Behavior

```yaml
- alert: ClientHigh429Rate
  expr: |
    sum(rate(kong_http_requests_total{status="429"}[5m])) by (consumer)
    / sum(rate(kong_http_requests_total[5m])) by (consumer) > 0.5
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Consumer {{ $labels.consumer }} has > 50% 429 rate"
    description: "Check client retry behavior"

- alert: ClientRetryStorm
  expr: |
    rate(kong_http_requests_total{consumer="sk_live_megaretail_2026_08"}[1m]) > 1000
  for: 30s
  labels:
    severity: critical
  annotations:
    summary: "Possible retry storm from {{ $labels.consumer }}"
    description: "Request rate: {{ $value }} req/min"
```

## 5. Automated Remediation

```yaml
# alertmanager webhook for auto-remediation
receivers:
  - name: auto-ratelimit-fix
    webhook_configs:
      - url: http://ratelimit-autofix.production.svc.cluster.local:8080/remediate
        send_resolved: true
```

### Auto-Remediation Service

```java
package com.acmecorp.apigateway.autoremediation;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/remediate")
public class RateLimitAutoRemediation {

    @PostMapping
    public RemediationResult remediate(@RequestBody Alert alert) {
        switch (alert.getAlertName()) {
            case "ConsumerRateLimited":
                return increaseRateLimit(alert.getConsumer());
            case "RateLimitRedisMemoryHigh":
                return increaseRedisMemory();
            case "ClientRetryStorm":
                return blockAbusiveClient(alert.getConsumer());
            default:
                return new RemediationResult(false, "No action defined");
        }
    }

    private RemediationResult increaseRateLimit(String consumer) {
        // Call Kong Admin API to increase limit by 50%
        return new RemediationResult(true,
            "Rate limit increased for " + consumer);
    }

    private RemediationResult increaseRedisMemory() {
        // Scale Redis StatefulSet memory
        return new RemediationResult(true, "Redis memory scaled");
    }

    private RemediationResult blockAbusiveClient(String consumer) {
        // Temporarily block client with 60-second timeout
        return new RemediationResult(true,
            "Client " + consumer + " blocked for 60 seconds");
    }
}
```

## 6. Alert Escalation Matrix

| Condition | Severity | Notification | Response | Auto-Remediation |
|-----------|----------|-------------|----------|------------------|
| 429 rate > 5% | Critical | PagerDuty + Slack | 5 min | No (investigate) |
| Single consumer > 50% 429 | Warning | Slack | 15 min | Increase limit |
| Redis memory > 85% | Warning | Slack | 15 min | Scale Redis |
| Redis evictions > 0 | Critical | PagerDuty | 5 min | Increase memory |
| Retry storm > 1K req/min | Critical | PagerDuty | 2 min | Block client |
| Kong CPU > 85% | Critical | PagerDuty | 5 min | Scale Kong |

## References

- Kong Monitoring: (link removed)
- Prometheus Redis Exporter: https://github.com/oliver006/redis_exporter
- Google Cloud Armor Metrics: (link removed)
- GitHub API Rate Limit Monitoring: https://docs.github.com/en/rest/overview/resources-in-the-rest-api
