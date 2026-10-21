# Visual Guide — Distributed Monitoring

## Prometheus Scrape Flow
`
Prometheus Server -> HTTP GET /metrics
  Service A: returns metrics
  Service B: returns metrics
  Service C: returns metrics
Prometheus: stores in TSDB
Prometheus: evaluates alert rules
Prometheus -> Alertmanager: firing alerts
`

## Distributed Trace Visualization
`
Trace: POST /api/order
  Span: API Gateway (2ms)
    Span: Auth Service (1ms)
    Span: Order Service (3ms)
      Span: Payment Service (2ms)
      Span: Inventory Service (1ms)
    Span: Notification Service (1ms)
Total: 10ms
`
"@ -Encoding UTF8

Set-Content "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\distributed-systems\20-distributed-monitoring\SECURITY.md" -Value @"
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
