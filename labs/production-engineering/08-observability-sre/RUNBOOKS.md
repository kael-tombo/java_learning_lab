# RUNBOOKS: Observability, OpenTelemetry & SRE Production Triage
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## Runbook 01: Triaging a 14.4x Error Budget Burn Rate Page (Google SRE Alert)

### 1. Alert Context & Severity
- **Severity**: P1 / SEV-1 (Critical Page)
- **Alert**: `PaymentServiceErrorBudgetFastBurn`
- **Condition**: Error budget burning at $\ge 14.4\times$ across both 1-hour and 5-minute rolling windows. 100% of monthly budget will deplete in 2 days.

### 2. Triage & Forensic Workflow

#### Step 1: Inspect Exemplars on Grafana Dashboard
1. Open the **SLO Error Budget Overview** dashboard.
2. Locate the latency/error spike on the metric graph.
3. Hover over the **blue exemplar dots** attached to the 5xx metric bucket.
4. Click **"Query with Tempo"** to jump directly to the root-cause trace DAG.

#### Step 2: Analyze the Causal Trace DAG in Tempo
- Identify the first span with `status = ERROR`.
- Note the failing service, HTTP endpoint, and database query.
- Check the span attributes for `exception.message` and `exception.stacktrace`.

#### Step 3: Check Structured JSON Logs by TraceID
```bash
# Query Grafana Loki or Elasticsearch for all log events sharing the exact TraceID:
{app="payment-orchestrator"} |= "4bf92f3577b34da6a3ce929d0e0e4736"
```
Review the exact contextual error state leading up to the transaction failure.

#### Step 4: Mitigate
- If errors correlate with a recent deployment: execute immediate rollback via ArgoCD.
- If errors correlate with downstream database saturation: trip emergency load-shedding circuit breaker.

---

## Runbook 02: Remediating a Prometheus Cardinality Explosion

### 1. Symptoms & Alert
- Alert: `PrometheusHighMemoryUsage` ($> 85\%$ RAM).
- Prometheus pod is crashing with `Exit Code 137` (OOM-Killed).
- Scrape duration is spiking past 10 seconds.

### 2. Live Diagnostics & Cardinality Audit

#### Step 1: Query Top Memory-Consuming Label Names
Execute query against Prometheus admin API:
```bash
# Query the top 10 highest-cardinality metric names
curl -s http://prometheus-k8s.monitoring.svc:9090/api/v1/status/tsdb | jq .data.seriesCountByMetricName | head -n 20
```

#### Step 2: Query Top Cardinality Labels for Offending Metric
```bash
curl -s http://prometheus-k8s.monitoring.svc:9090/api/v1/status/tsdb | jq .data.labelValueCountByLabelName | head -n 20
```
*Sample Output*:
```json
[
  {"name": "user_id", "value": 4820194},
  {"name": "order_uuid", "value": 1284092}
]
```
`user_id` and `order_uuid` are detected as rogue high-cardinality labels!

#### Step 3: Immediate Mitigation via Metric Relabeling
Add a metric relabeling rule to Prometheus to drop the offending labels at ingestion:
```yaml
# In Prometheus custom resource / scrape config:
metricRelabelings:
  - action: labeldrop
    regex: "(user_id|order_uuid|customer_id)"
```
Apply the configuration. Prometheus will stop indexing the rogue dimensions immediately, stabilizing memory consumption.

---

## Runbook 03: Diagnosing Broken Trace Context Propagation Across Services

### 1. Symptoms
- Distributed traces appear fragmented in Jaeger/Tempo: downstream microservice calls appear as isolated "root" spans rather than child spans of the upstream caller.
- Frontend user requests cannot be traced to database queries.

### 2. Forensic Investigation

#### Step 1: Inspect Inbound Network Headers with `tcpdump`
Capture HTTP traffic entering the downstream service:
```bash
# Capture incoming HTTP headers on target container
kubectl exec -it <DOWNSTREAM_POD> -- tcpdump -A -s 0 -i any 'tcp port 8080 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420 or tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354)' | grep -i "traceparent"
```
- If `traceparent` is missing: The upstream calling service is failing to inject the context into its HTTP/gRPC client!
- If `traceparent` is present: The downstream receiving service's WebFilter is failing to extract it into the active `SpanContext`.

#### Step 2: Verify OpenTelemetry Agent / Micrometer Bean Configuration
Verify the upstream service has configured `RestTemplate` or `WebClient` with the tracing interceptor:
```java
// Spring Boot 3 Requirement:
@Bean
public RestTemplate restTemplate(RestTemplateBuilder builder) {
    // RestTemplateBuilder automatically attaches ObservationRestTemplateCustomizer!
    return builder.build(); 
}
```
*Note*: Instantiating `new RestTemplate()` directly bypasses Micrometer instrumentation and loses trace propagation!

---

## Runbook 04: Continuous Profiling Triage with Pyroscope / async-profiler

### 1. Symptoms
- Container CPU utilization spikes to $100\%$ following a traffic surge.
- Traditional thread dumps show threads in `RUNNABLE` state without clear hotspot attribution.

### 2. Diagnostic Execution

#### Step 1: Access Pyroscope Flame Graph Dashboard
1. Open Pyroscope UI and select application `payment-orchestrator`.
2. Select metric: `CPU (samples/sec)`.
3. Set time window: past 15 minutes.

#### Step 2: Generate Release Differential Flame Graph
1. Select "Comparison View".
2. Baseline: `version = v3.3.9` (Previous stable release).
3. Comparison: `version = v3.4.0` (Current degraded release).
4. Identify bright red blocks:
   - Example: `com.fasterxml.jackson.databind.ObjectMapper.readValue()` taking **35% of total CPU** due to un-cached reflection introspection.

#### Step 3: Remediate
Deploy a patch replacing per-request `new ObjectMapper()` allocations with a singleton cached mapper.

---

## Runbook 05: OpenTelemetry Collector Queue Overflow & Backpressure Mitigation

### 1. Symptoms
- OpenTelemetry Collector logs show:
  ```text
  exporter helper dropped spans: queue is full
  ```
- Application pods experience network timeouts pushing OTLP spans to the collector.

### 2. Diagnostic Execution

#### Step 1: Inspect Collector Queue Metrics
```bash
kubectl top pods -n monitoring -l app=opentelemetry-collector
curl -s http://<COLLECTOR_IP>:8888/metrics | grep "otelcol_exporter_enqueue_failed_spans"
```

#### Step 2: Immediate Remediation via Collector HPA & Buffer Expansion
1. Scale up OTel Collector replicas:
   ```bash
   kubectl scale deployment opentelemetry-collector -n monitoring --replicas=8
   ```
2. Tune collector queue buffer in `otel-collector-config.yaml`:
   ```yaml
   processors:
     batch:
       timeout: 500ms
       send_batch_size: 2048
   exporters:
     otlp/tempo:
       sending_queue:
         queue_size: 10000
   ```
Apply and verify span drop rate drops back to 0.
