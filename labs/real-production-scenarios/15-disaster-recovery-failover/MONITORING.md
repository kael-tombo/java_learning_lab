# Monitoring: Disaster Recovery and Failover

## Monitoring Architecture

Multi-region monitoring designed to detect region-level failures, track RTO/RPO performance, and provide visibility during failover events.

## 1. Cross-Region Health Checks

### Route53 Health Checks

```yaml
health_checks:
  primary:
    endpoint: https://api.us-east-1.acmecorp.com/health
    type: HTTPS
    interval: 10 seconds
    failure_threshold: 3
    regions:
      - us-west-1
      - eu-west-1
      - ap-southeast-1
  
  dr:
    endpoint: https://api.us-west-2.acmecorp.com/health
    type: HTTPS
    interval: 10 seconds
    failure_threshold: 3
    regions:
      - us-east-2
      - eu-west-1
      - ap-southeast-1
```

### Prometheus Multi-Region Scraping

```yaml
scrape_configs:
  - job_name: 'cross-region-health'
    metrics_path: /health
    static_configs:
      - targets:
          - 'https://api.us-east-1.acmecorp.com'
          - 'https://api.us-west-2.acmecorp.com'
          - 'https://api.eu-west-1.acmecorp.com'
    relabel_configs:
      - source_labels: [__address__]
        target_label: region
        regex: 'https://api\.(.+)\.acmecorp\.com'
        replacement: '${1}'
```

## 2. RDS Replication Monitoring

### Prometheus Alert Rules

```yaml
groups:
  - name: rds_replication
    rules:
      - alert: RDSReplicationLagHigh
        expr: aws_rds_replica_lag_seconds > 5
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "RDS replication lag > 5 seconds"
          description: "Current lag: {{ $value }}s"

      - alert: RDSReplicationLagCritical
        expr: aws_rds_replica_lag_seconds > 30
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "RDS replication lag > 30 seconds — RPO at risk"
          description: "Current lag: {{ $value }}s"

      - alert: RDSReplicationStopped
        expr: aws_rds_replica_status != "replicating"
        for: 10s
        labels:
          severity: critical
        annotations:
          summary: "RDS replication STOPPED"
          description: "Replica status: {{ $value }}"
```

### Grafana Dashboard: RDS Replication

**Panel 1: Replication Lag** (Timeseries)
- Query: `aws_rds_replica_lag_seconds{region="us-west-2"}`
- Warning line: 5s, Critical line: 30s

**Panel 2: Replica Status** (Singlestat)
- Query: `aws_rds_replica_status{region="us-west-2"}`
- Display: "Replicating" or error

**Panel 3: Transactions Behind** (Gauge)
- Query: `aws_rds_replica_transactions_behind_master`
- Range: 0 — 10000

## 3. Route53 DNS Monitoring

### Prometheus Alert Rules

```yaml
groups:
  - name: dns_health
    rules:
      - alert: DNSRecordUnhealthy
        expr: route53_health_check_status == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Route53 health check failed for {{ $labels.endpoint }}"

      - alert: DNSFailoverActive
        expr: route53_failover_routing_active{region="us-west-2"} == 1
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "DNS failover to us-west-2 is ACTIVE"
          description: "Primary (us-east-1) health check has failed"
```

### Synthetic DNS Monitoring

```bash
#!/bin/bash
# dns-monitor.sh — Monitor DNS propagation

DOMAINS=("api.acmecorp.com" "www.acmecorp.com" "app.acmecorp.com")
EXPECTED_PRIMARY="203.0.113.10"
EXPECTED_DR="198.51.100.10"
SLACK_WEBHOOK="(link removed)"

check_dns() {
  local domain=$1
  local resolver=$2
  local result=$(dig @$resolver $domain +short 2>/dev/null | head -1)
  echo "$result"
}

echo "=== DNS Health Check ==="
for domain in "${DOMAINS[@]}"; do
  # Check multiple resolvers
  for resolver in "8.8.8.8" "1.1.1.1" "208.67.222.222"; do
    ip=$(check_dns $domain $resolver)
    region="unknown"
    [ "$ip" = "$EXPECTED_PRIMARY" ] && region="us-east-1"
    [ "$ip" = "$EXPECTED_DR" ] && region="us-west-2"
    echo "$domain @ $resolver → $ip ($region)"
  done
done
```

## 4. Failover Monitoring Dashboard

### Grafana: DR Status Overview

**Panel 1: Region Health Status** (Singlestat per region)
- us-east-1: green/red
- us-west-2: green/red
- eu-west-1: green/red

**Panel 2: Active Region** (Singlestat)
- Shows which region is currently serving traffic
- Expected: us-east-1 unless failover active

**Panel 3: Failover History** (Table)
- Timestamp of last failover
- Duration of failover
- Trigger reason

**Panel 4: RTO/RPO Tracker** (Timeseries)
- Last drill RTO vs target
- Last drill RPO vs target
- Days since last successful drill

**Panel 5: Cross-Region Latency** (Timeseries)
- Response time from primary vs DR
- Alert if DR response is > 5x primary

**Panel 6: CloudFormation Drift** (Singlestat)
- Number of stacks in-sync vs drifted
- Alert any drift detected

## 5. Chaos Engineering Metrics

```yaml
chaos_metrics:
  - name: chaos_drill_completion
    type: gauge
    description: "1 if last chaos drill succeeded"
    severity: warning
    alert_if: == 0
  
  - name: chaos_drill_duration
    type: gauge
    description: "Duration of last chaos drill in minutes"
    compare_to: target_duration
  
  - name: chaos_attack_count
    type: counter
    description: "Total chaos attacks executed"
  
  - name: chaos_failure_found
    type: gauge
    description: "1 if chaos drill found a failure"
    severity: critical
```

## 6. Automated Failover Alerting

```yaml
groups:
  - name: dr_status
    rules:
      - alert: RegionOutageDetected
        expr: |
          count(route53_health_check_status{endpoint=~".*\\.us-east-1\\.acmecorp\\.com"} == 0)
          / count(route53_health_check_status{endpoint=~".*\\.us-east-1\\.acmecorp\\.com"})
          > 0.5
        for: 2m
        labels:
          severity: critical
          dr_team: paged
        annotations:
          summary: "us-east-1 region outage detected"
          runbook: "https://runbook.acmecorp.com/dr-failover-us-east-1"

      - alert: FailoverCompleted
        expr: route53_failover_routing_active{region="us-west-2"} == 1
        for: 1m
        labels:
          severity: info
        annotations:
          summary: "Auto-failover to us-west-2 completed"
          description: "RTO: {{ $value }}s since detection"

      - alert: FailbackRequired
        expr: |
          route53_failover_routing_active{region="us-west-2"} == 1
          AND ON() aws_region_healthy{region="us-east-1"} == 1
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Primary region recovered — failback recommended"
```

## 7. Alert Escalation Matrix

| Condition | Severity | Notification | Response | Action |
|-----------|----------|-------------|----------|--------|
| RDS lag > 5s | Warning | Slack | 15 min | Investigate |
| RDS lag > 30s | Critical | PagerDuty | 5 min | Fix replication |
| RDS replication stopped | Critical | PagerDuty | 2 min | Resume replication |
| Region health check failed | Critical | PagerDuty + Phone | Immediate | Declare incident |
| DNS failover active | Critical | PagerDuty | Immediate | Verify failover |
| CloudFormation drift | Warning | Slack | 24h | Sync templates |
| DR drill overdue | Warning | Slack | 1 week | Schedule drill |
| Chaos experiment found issue | Critical | PagerDuty | 1 day | Fix before production |

## References

- AWS Health Checks: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/health-checks.html
- Prometheus Multi-Region: https://prometheus.io/docs/practices/remote_write/
- Netflix Chaos Monitoring: https://netflixtechblog.com/chaos-monitoring
- Google SRE Monitoring: https://sre.google/sre-book/monitoring-distributed-systems/
