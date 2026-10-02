# 11 — AWS Observability — Theory

## Overview
AWS Observability provides tools to monitor, trace, and analyze applications and infrastructure. This lab covers CloudWatch, X-Ray, Prometheus on AWS, AMP, and AMG.

## 1. CloudWatch

### Metrics
- **Standard Metrics**: CPU, network, disk for AWS services (1-minute granularity)
- **Custom Metrics**: Application-specific metrics (1-second granularity with high-res)
- **Dimensions**: Key-value pairs that identify a metric (InstanceId, AutoScalingGroupName)
- **Resolution**: Standard (60s), High (1s)
- **Retention**: 1s metrics (3h), 1min metrics (15d), 5min metrics (63d), 1h metrics (455d)

### Metric Math
Combine multiple metrics with arithmetic operations:
- `m1 + m2` — Sum of two metrics
- `(m1 - m2) / 100` — Difference as percentage
- `FILL(m1, 0)` — Fill missing data with zeros
- `METRICS("m1", "m2")` — Reference multiple metrics

### Logs
- **Log Groups**: Container for log streams (usually per application)
- **Log Streams**: Sequence of log events (usually per instance/container)
- **Log Events**: Individual log records with timestamp and message
- **Subscription Filters**: Real-time processing of log events to Lambda, Kinesis, or OpenSearch

### Alarms
- **State**: OK, ALARM, INSUFFICIENT_DATA
- **Period**: Evaluation period (1s to 1 day)
- **Threshold**: Static or anomaly detection (ML-based)
- **Actions**: SNS, Auto Scaling, EC2 actions
- **Composite Alarms**: Combine multiple alarms with AND/OR logic

## 2. X-Ray

### Distributed Tracing
X-Ray traces requests as they travel through distributed applications:
- **Trace**: End-to-end path of a request through the application
- **Segment**: Record of work done by a single service
- **Subsegment**: Record of downstream calls (API calls, database queries)
- **Service Graph**: Map of services and their connections

### Instrumentation
- **X-Ray SDK**: Manual instrumentation in Java, Python, Node.js, .NET, Go, Ruby
- **Auto-instrumentation**: Lambda, API Gateway, ECS, EKS (container sidecar)
- **OpenTelemetry**: Can export traces to X-Ray via AWS OTel Distro

### Sampling
- **Reservoir sampling**: 1 request/second + 5% of additional requests (adjustable)
- **Rules**: Define sampling behavior by service, URL path, or HTTP method
- **Fixed rate**: Set a specific percentage of requests to trace

### Annotations and Metadata
- **Annotations**: Key-value pairs indexed for filtering (used for search)
- **Metadata**: Key-value pairs not indexed (for additional context)

## 3. Prometheus on AWS

### What is Prometheus?
Prometheus is an open-source monitoring and alerting toolkit originally built at SoundCloud. It uses a pull-based model to scrape metrics from targets.

### Prometheus Architecture
```
Service A (metrics:8080) -> Scrape -> Prometheus Server -> TSDB
Service B (metrics:8081) -> Scrape ->                    |
                                                  Alertmanager -> Alert
                                                  |
                                               Grafana -> Dashboard
```

### Metric Types
- **Counter**: Cumulative count (total requests, errors)
- **Gauge**: Single numeric value that can go up/down (CPU, memory)
- **Histogram**: Samples observations in configurable buckets (latency)
- **Summary**: Similar to histogram but with pre-computed quantiles

### PromQL (Prometheus Query Language)
- Instant queries: `http_requests_total{status="200"}`
- Range queries: `rate(http_requests_total[5m])`
- Aggregation: `sum by(service) (rate(http_requests_total[5m]))`
- Functions: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`

## 4. AMP (Amazon Managed Service for Prometheus)

AMP is a fully managed Prometheus-compatible monitoring service:
- Automatically scales ingestion and query capacity
- Stores data in your account (encrypted at rest with KMS)
- Supports existing Prometheus tools (Grafana, alertmanager)
- Works with EKS, ECS, and self-managed Kubernetes
- Uses AWS SigV4 authentication for write/read APIs

### Workspace Architecture
```
Prometheus Server (EKS) -> Remote Write -> AMP Workspace
                                              |
Grafana (AMG) -> AMP Data Source -> Query -> Dashboard
                                              |
Third-party tools -> AMP Query API -> Analysis
```

## 5. AMG (Amazon Managed Grafana)

AMG is a fully managed Grafana service:
- Workspaces with automatic version upgrades
- Built-in security with SAML/SSO and IAM authorization
- Pre-configured data sources for AWS services (CloudWatch, X-Ray, AMP)
- Enterprise plugins including Grafana OnCall
- Scalable with automatic capacity management

### Data Sources
- CloudWatch (metrics and logs)
- Amazon Managed Service for Prometheus
- Amazon OpenSearch Service
- Amazon Timestream
- X-Ray
- Athena (for querying S3 logs)

## Key Takeaways
1. CloudWatch provides metrics, logs, and alarms for all AWS resources
2. X-Ray traces requests across distributed services for performance analysis
3. Prometheus is the standard for Kubernetes monitoring with a powerful query language
4. AMP provides managed Prometheus with automatic scaling and AWS integration
5. AMG unifies dashboards across multiple AWS and third-party data sources

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Monitoring — Google SRE Workbook Ch. 4 (2018; O'Reilly, CC BY-NC-ND 4.0) — https://sre.google/workbook/monitoring/ — Takeaway for CloudWatch alarm exercises: monitor to alert, investigate/diagnose, visualize, track trends, and compare before/after changes; keep data fresher than ~4–5 min for incident response.
- Metrics vs logs sources — Google SRE Workbook Ch. 4 (2018) — https://sre.google/workbook/monitoring/ — Takeaway for metrics/CloudWatch-Logs/X-Ray exercises: use near-real-time metrics (counters + windowed rates, percentiles not means) for alerts/dashboards and granular logs for root-cause; increment a counter metric even for single exceptional events.
- Purposeful metrics + golden signals — Google SRE Workbook Ch. 4 (2018) — https://sre.google/workbook/monitoring/ — Takeaway for PromQL/AMP exercises: export latency/error/traffic/saturation per dependency (bytes, latency, codes, RPC method), track binary/config versions for change correlation, and alert on SLO-burn plus resource-exhaustion thresholds.
- Managing monitoring as code — Google SRE Workbook Ch. 4 (2018) — https://sre.google/workbook/monitoring/ — Takeaway for Grafana/AMG dashboard exercises: store monitoring config in version control, converge on one framework with consistent basic metrics, and loosely couple collection/storage/alerting/visualization (e.g., Prometheus + long-term store + Alertmanager + Grafana).
