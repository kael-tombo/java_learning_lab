# Architecture — Distributed Monitoring

## Prometheus + Thanos Architecture
`
Service -> Prometheus (scrape)
              |
         Thanos Sidecar
              |
    +---------+---------+
    |                   |
Object Store       Thanos Query
(S3/GCS)               |
              +---------+
              |
         Prometheus (global)
`

## OpenTelemetry Architecture
`
Service A ---> OTel Collector ---> Tracing Backend (Jaeger)
Service B ---> OTel Collector ---> Tracing Backend (Tempo)
Service C ---> OTel Collector ---> Metrics Backend (Prometheus)
              |
              +--> Log Backend (Loki)
`

## Alert Flow
`
Prometheus (rule evaluation)
    |
Alertmanager (dedup, grouping, routing)
    |
+---+---+
|       |       |
Slack   PagerDuty   Email
`
"@

W "SECURITY.md" @"
# Security — Distributed Monitoring

## Threats
- Sensitive data exposed in metrics
- Unauthorized access to monitoring data
- Metric injection (fake data)
- Denial of service via high cardinality
- Alert fatigue covering real incidents

## Mitigations
- Authentication on monitoring endpoints
- TLS for all monitoring traffic
- Metric sanitization (remove sensitive labels)
- Cardinality limits per metric
- Rate limiting on metric ingestion
- Access control for alert management
