# RUNBOOK: Observability & SRE Alert Triage
## Lab 08 | Production Engineering Academy

---

## RUNBOOK 01: Error Budget Fast Burn Rate (14.4x Alert)

**Severity**: P1 (Page immediately)  
**Meaning**: 2% of the monthly error budget consumed in the last 1 hour. Total depletion in $< 48$ hours.

### Step 1: Identify the Failing Component & Region
Query Prometheus:
```promql
sum by (service, endpoint, status_code) (
  rate(http_server_requests_seconds_count{status=~"5.."}[5m])
) / 
sum by (service, endpoint) (
  rate(http_server_requests_seconds_count[5m])
) > 0.01
```

### Step 2: Extract Correlated Traces from Jaeger / Grafana Tempo
1. Filter traces by:
   - `service.name == payment-service`
   - `http.status_code == 500`
   - `duration > 200ms`
2. Open trace with exemplar linked in Prometheus alert.
3. Identify which span failed (e.g. `POST /v1/charges` -> `DB query timeout`).

### Step 3: Rollback or Circuit Break
- If error rate started immediately after a new deployment:
  ```bash
  kubectl rollout undo deployment/payment-service
  ```
- If downstream third-party dependency is failing: trip circuit breaker to static fallback.

---

## RUNBOOK 02: Metric High-Cardinality Drop Procedure
If Prometheus scrape buffer memory alerts fire:
1. Run Prometheus runtime series check:
   ```bash
   curl -g 'http://prometheus:9090/api/v1/status/tsdb' | jq '.data.seriesCountByMetricName | head -n 10'
   ```
2. Identify runaway metric. Apply drop rule in Prometheus config:
   ```yaml
   metric_relabel_configs:
     - source_labels: [__name__]
       regex: 'package_lookup_duration_.*'
       action: drop
   ```
3. Reload Prometheus without restart:
   ```bash
   curl -X POST http://prometheus:9090/-/reload
   ```
