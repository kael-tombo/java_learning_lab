# Datadog Interview Guide — Real Production Scenarios Academy

## Interview Process for SRE/Infrastructure Roles

### Rounds
1. **Phone Screen (45 min)**: Observability fundamentals, monitoring philosophy, basic coding in Python or Go
2. **Onsite (4-5 rounds, 45 min each)**:
   - **Coding Round**: Python/Go medium difficulty — often involving data processing (metrics, logs, traces)
   - **Systems Design**: Design a monitoring system (e.g., time-series database, distributed tracing system)
   - **Observability Deep-Dive**: Debugging with Datadog tools — given a dashboard, find the issue
   - **Infrastructure Debugging**: On-call simulation using real monitoring data
   - **Behavioral/Product Sense**: Customer empathy, product-led growth mindset

### SRE/Infrastructure-Specific Expectations
- Datadog is an observability company — the interview IS the product. They expect you to think like their users.
- Deep knowledge of monitoring pillars: metrics, traces, logs (the "Three Pillars of Observability")
- Experience with Datadog Agent integration, DogStatsD, custom metrics
- Understanding of time-series databases (TSDB internals, compression, downsampling)
- Distributed tracing (OpenTelemetry, Datadog APM) — trace propagation, sampling, head-based vs tail-based
- "Customer obsession" — Datadog builds for engineers; you need to think about what features help users debug faster

### Round Breakdown
- Systems Design: 35% — monitoring system design
- Coding (Python/Go): 25% — data processing pipelines
- Observability Deep-Dive: 25% — dashboard analysis, incident investigation
- Behavioral: 15% — product empathy, collaboration

## Top Incidents Aligned to Datadog Observability Focus

### Incident: Slow Query — No Index / Missing Trace (Lab 05)
#### Problem Scenario
A customer reports their e-commerce platform's checkout page takes 15 seconds to load. They have Datadog APM and RUM (Real User Monitoring) enabled. The APM trace shows a database query taking 12 seconds, but the database team says the query is fast in their environment.

#### Interview Walkthrough
**Step 1 — Analyze the trace**: In Datadog APM, navigate to Traces → CheckoutService → `POST /checkout/submit`. The flame graph shows:
- `checkout.submit`: 15s total (root span)
- `validateAddress`: 500ms
- `processPayment`: 2s
- `getShippingRates`: 12s (database query)

**Step 2 — Check the database query**: Click on the `getShippingRates` span. The full SQL is shown in tags: `SELECT * FROM shipping_rates WHERE zone_id = ? AND weight < ? ORDER BY price`. There is no `LIMIT` clause.

**Step 3 — Check database query volume**: Use Datadog Metrics → `mysql.queries.count` grouped by `query_signature`. The query runs 10k times/day with average 12s execution. The table has 5M rows with no index on `(zone_id, weight)`.

**Step 4 — Root cause**: Missing composite index on `(zone_id, weight)`. The query does a full table scan on 5M rows. The database team's environment has only 10k rows, so it's fast locally.

**Step 5 — Fix**: Add the missing index. Use Datadog Database Monitoring to identify missing indexes proactively.

**What Datadog evaluates**: APM trace reading; SQL analysis; understanding of how monitoring helps debug "works on my machine" problems; knowledge of Datadog Database Monitoring.

#### Solution
```sql
-- Add missing composite index
CREATE INDEX idx_shipping_rates_zone_weight
ON shipping_rates(zone_id, weight);

-- Datadog Database Monitoring query to detect missing indexes
-- Run from Datadog Notebook:
SELECT
    query_signature,
    avg(query_time) as avg_time_us,
    count(*) as executions,
    rows_examined,
    rows_sent
FROM datadog.database_monitoring.query_metrics
WHERE service = "checkout-service"
  AND env = "production"
  AND rows_examined / NULLIF(rows_sent, 0) > 1000  -- bad ratio
ORDER BY avg_time_us DESC
LIMIT 10;

// Python script to add Datadog custom metric for query performance
import datadog
from datadog import statsd

def track_query_performance(query_name, duration_ms, rows_examined):
    statsd.histogram(f"db.query.duration", duration_ms, tags=[f"query:{query_name}"])
    statsd.gauge(f"db.query.rows_examined", rows_examined, tags=[f"query:{query_name}"])
    if rows_examined > 10000:
        statsd.event("Slow Query Detected", f"Query {query_name} examined {rows_examined} rows")
```

**Post-mortem**: Add Datadog Database Monitoring for all production databases. Set up SLO-based alerting for query performance. Add `EXPLAIN ANALYZE` to CI pipeline.

#### Follow-ups
- **At Datadog scale**: Use Database Monitoring to analyze query performance across thousands of customers. Build a recommendation engine for missing indexes.
- **Product improvement**: Datadog's Database Monitoring should auto-detect missing indexes and suggest `CREATE INDEX` statements.

### Incident: High CPU — Agent Overhead (Lab 03)
#### Problem Scenario
A customer enables a new Datadog integration (process collection, container monitoring). Their application hosts see CPU increase from 20% to 60%. The Datadog Agent is consuming 40% CPU per host across 500 hosts.

#### Interview Walkthrough
**Step 1 — Check Agent status**: `datadog-agent status` on an affected host. Shows `process` check running with `python.process_collector` consuming 30% of Agent CPU time.

**Step 2 — Check Agent logs**: `/var/log/datadog/agent.log` shows:
```
process_collector: Collected 2500 processes (22ms)
process_collector: Collected 2500 processes (21ms)
```
The collector runs every 10 seconds and collects 2500 processes per host. For 500 hosts, this is 125k processes collected every 10 seconds.

**Step 3 — Root cause**: The `process_collection` check with `expanded_process_collection: true` collects all process details (open files, network connections) at the default interval (10s). The overhead of reading `/proc/[pid]/` for 2500 processes adds 20ms of Python execution time per run, plus IO wait.

**Step 4 — Fix**: Reduce process collection interval. Disable expanded process collection. Use process filtering to exclude known low-value processes.

**What Datadog evaluates**: Understanding of Datadog Agent architecture; ability to optimize Agent overhead; customer-first mindset (helping them reduce cost without losing visibility).

#### Solution
```yaml
# datadog.yaml — Agent configuration optimization
process_config:
  enabled: "true"
  # Reduce collection interval from 10s to 30s
  collection_interval: 30
  # Disable expanded collection (open files, network)
  exprocess_collection: false
  # Exclude known processes
  blacklist_patterns:
    - "sleep"
    - "kworker/*"
    - "watchdog/*"
    - "systemd-*"
  # Limit process count per host
  max_proc_count: 500

# Python check: custom process monitoring with reduced overhead
from checks import AgentCheck

class EfficientProcessCheck(AgentCheck):
    def check(self, instance):
        # Only collect high-value processes
        important_processes = ["java", "python", "nginx", "mysqld"]
        for proc in self.get_process_list():
            if any(p in proc.name for p in important_processes):
                self.gauge(f"process.{proc.name}.cpu", proc.cpu_percent)
                self.gauge(f"process.{proc.name}.memory", proc.memory_rss)
```

**Post-mortem**: Set up Agent resource monitoring (`datadog.agent.running`, `datadog.agent.cpu`). Create a dashboard of Agent overhead per integration. Add Agent overhead alert at 20% CPU.

#### Follow-ups
- **At Datadog scale**: Build Agent overhead dashboards for customers. Auto-tune collection intervals based on host capacity.
- **Product improvement**: Add "Agent Performance" view in Datadog that shows per-check resource consumption.

### Incident: Connection Pool Exhaustion — DogStatsD (Lab 04)
#### Problem Scenario
A service starts dropping DogStatsD metrics. Datadog APM traces show "StatsD submit error: connection refused". The service uses DogStatsD to submit 50k metrics/second to the local Datadog Agent.

#### Interview Walkthrough
**Step 1 — Check DogStatsD metrics**: `datadog-agent dogstatsd-stats` shows `dogstatsd.packets_sent: 50k/s` but `dogstatsd.packets_dropped: 5k/s`. 10% of metrics are dropped.

**Step 2 — Check Agent DogStatsD stats**: `datadog-agent dogstatsd-stats --json` shows:
```
"UdsTransport": {
    "ConnectionErrors": 5000,
    "ReadBuffers": 1
}
```
The UDS (Unix Domain Socket) transport is hitting connection limits.

**Step 3 — Root cause**: The DogStatsD client opens a new UDS connection for every metric submission. At 50k metrics/second, this creates 50k connections/second to the Agent. The Agent's UDS server can only process 4096 simultaneous connections (default `net.core.somaxconn`).

**Step 4 — Fix**: Use the DogStatsD client with buffering (batch metrics in a single connection). Increase `dogstatsd_buffer_size`. Use the UDS transport with connection reuse (Datadog Java/Python/Go clients all support this).

**What Datadog evaluates**: DogStatsD protocol understanding; client-side buffering; UDS vs UDP transport; Datadog Agent internals.

#### Solution
```java
// Before: unbuffered DogStatsD — new connection per metric
StatsDClient client = new NonBlockingStatsDClient("myapp", "localhost", 8125);
client.recordGaugeValue("checkout.latency", 150, "status:success");
client.recordGaugeValue("checkout.latency", 1200, "status:failure");

// After: buffered with connection reuse
// DDSketch for metric aggregation before submission
import com.datadoghq.sketch.ddsketch.DDSketch;

DDSketch latencySketch = DDSketch.default();
latencySketch.accept(150);
latencySketch.accept(1200);

// Batch submit using histogram (single connection)
client.recordHistogramValue("checkout.latency", 150, "status:success");
client.recordHistogramValue("checkout.latency", 1200, "status:failure");

// Java client configuration for connection reuse
// In dd-java-agent.config:
dd.dogstatsd.buffer.size=32768
dd.dogstatsd.namespace=checkout
dd.dogstatsd.sender.queue.size=100000
dd.dogstatsd.pipeline.enabled=true
```

**Post-mortem**: Add DogStatsD drop rate monitoring. Set up alert if drop rate > 1%. Use DDSketch for pre-aggregation.

#### Follow-ups
- **At Datadog scale**: Use DDSketch for quantile approximation before sending to DogStatsD. Use the Agent's internal buffering and retry logic.
- **Product improvement**: Add DogStatsD drop rate to the Datadog Agent dashboard in the UI.

### Incident: Kafka Consumer Lag — Log Ingestion Pipeline (Lab 13)
#### Problem Scenario
Datadog's log ingestion pipeline processes 10TB/day of customer logs through Kafka. Consumer lag grows from 10 seconds to 10 minutes. Logs for a major customer show 30-minute latency from ingestion to searchability.

#### Interview Walkthrough
**Step 1 — Check pipeline health**: Datadog internal monitoring shows `kafka.consumer.lag` for the `log-indexing` consumer group at 50M messages. The pipeline has 50 partitions.

**Step 2 — Check per-partition lag**: One partition (partition 23) has 40M messages lagging. The other 49 partitions have < 200k each.

**Step 3 — Check the hot partition**: The log parsing service for partition 23 is running but processing messages at 100 msg/s vs the normal 5000 msg/s. The service CPU is at 100%.

**Step 4 — Root cause**: A customer sent a 50MB JSON log line (single log event with a massive stack trace). The log parser spends 500ms processing this single line (parsing, extracting fields, GeoIP lookup). At 2 lines/second, that's 1 second of processing for 2 lines. Other partitions process 5000 regular lines/second each.

**Step 5 — Fix**: Add a maximum log line size limit (protobuf message size limit). Implement "drop large logs" policy with a customer notification. Use a separate Kafka topic for large logs with dedicated processing capacity.

**What Datadog evaluates**: Understanding of log ingestion pipelines; Kafka partition design; handling of outlier events; capacity planning.

#### Solution
```java
// Log parser with size limits
public class LogParser {
    private static final int MAX_LOG_SIZE_BYTES = 10_000_000; // 10MB
    private static final int MAX_LOG_SIZE_CHARS = 100_000; // 100k chars

    public ParsedLog parse(String rawLog) {
        // Reject logs that exceed size limits
        if (rawLog.length() > MAX_LOG_SIZE_CHARS) {
            logger.warn("Dropping oversized log ({} chars)", rawLog.length());
            statsd.increment("log.parser.dropped.oversized",
                "reason:max_chars",
                "size:" + rawLog.length());
            return null;  // Skip this log — moved to dead-letter
        }

        // Process with timeout
        try {
            return CompletableFuture
                .supplyAsync(() -> parseInternal(rawLog), parserPool)
                .get(2, TimeUnit.SECONDS);  // timeout per log line
        } catch (TimeoutException e) {
            statsd.increment("log.parser.timeout");
            return null;  // Skip slow-to-parse logs
        }
    }
}

// Kafka consumer configuration with poison pill handling
Properties props = new Properties();
props.put("max.partition.fetch.bytes", 10 * 1024 * 1024);  // 10MB max fetch
props.put("max.poll.records", 500);
props.put("max.poll.interval.ms", 300000);  // 5 min heartbeat

// Send oversized logs to a dead-letter topic
if (parsedLog == null) {
    deadLetterProducer.send(new ProducerRecord<>("logs-dlq", key, rawLog));
    consumer.commitSync();  // Commit offset to avoid reprocessing
    continue;
}
```

**Post-mortem**: Add per-partition processing latency monitoring. Add log size anomaly detection. Set up dead-letter queue monitoring and alerting.

#### Follow-ups
- **At Datadog scale**: Implement adaptive partitioning — auto-detect hot partitions and rebalance. Use the Datadog Log Pipeline's exclusion filters at the ingestion level.
- **Product improvement**: Add "Large Log Detection" to Datadog Log Management that notifies customers when they send oversized logs.

### Incident: TLS Certificate Expiry — Agent -> API Communication (Lab 12)
#### Problem Scenario
Datadog Agents across a customer's fleet fail to send metrics to `api.datadoghq.com`. The Agent logs show "TLS handshake failed: certificate expired". Metrics stop flowing for all services.

#### Interview Walkthrough
**Step 1 — Check Agent logs**: `grep "TLS\|certificate\|handshake" /var/log/datadog/agent.log`. Shows:
```
2026-07-23 03:15:00 UTC | CORE | ERROR | (pkg/forwarder/forwarder.go:123)
Failed to flush to endpoint '(link removed)':
x509: certificate has expired or is not yet valid

```

**Step 2 — Check system certificates**: `openssl s_client -connect api.datadoghq.com:443 -servername api.datadoghq.com 2>/dev/null | openssl x509 -noout -dates`. The server certificate is valid. The issue is the customer's intermediate CA certificate is expired in their trust store.

**Step 3 — Check the trust store**: `ls -la /etc/ssl/certs/ | grep -i datadog`. No Datadog-specific cert. `update-ca-trust check` shows expired root certificate for the CA that issued the Datadog API certificate.

**Step 4 — Root cause**: The customer's internal CA (which MITM-inspects all TLS traffic) has an expired root certificate. All outbound TLS connections are intercepted by a proxy that presents an expired certificate. Datadog Agent doesn't have an option to skip TLS verification (security requirement).

**Step 5 — Fix**: Update the customer's internal CA root certificate. As a workaround, configure the Agent to use a custom CA bundle: `DD_CA_CERT_PATH=/etc/datadog-agent/certs/custom-ca.crt`.

**What Datadog evaluates**: TLS troubleshooting; understanding of certificate chains; proxy configuration; Datadog Agent configuration.

#### Solution
```bash
# 1. Verify the exact TLS error
openssl s_client -connect api.datadoghq.com:443 \
  -CApath /etc/ssl/certs \
  -servername api.datadoghq.com \
  -debug 2>&1 | grep "error\|certificate\|fail"

# 2. Update trust store
sudo cp /path/to/new-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates --fresh

# 3. Configure Datadog Agent with custom CA (if needed)
cat >> /etc/datadog-agent/datadog.yaml << 'EOF'
# Custom CA bundle for TLS verification
ca_cert_path: /etc/datadog-agent/certs/datadog-ca.crt
EOF

# 4. Restart Agent
sudo systemctl restart datadog-agent

# 5. Verify Agent connectivity
datadog-agent healthcheck
datadog-agent check --json network | head -20
```

**Post-mortem**: Add Agent TLS monitoring (`datadog.agent.api_connectivity`). Set up alert for `api_connectivity:fail`. Add certificate expiry monitoring for all internal CAs.

#### Follow-ups
- **At Datadog scale**: Build Agent certificate health dashboard. Ship the Datadog Agent with a bundled CA that auto-updates.
- **Product improvement**: Add "Agent Connectivity Diagnostics" to the Datadog UI (like a built-in network troubleshoot tool).

### Incident: Cache Stampede — Tag Aggregation (Lab 08)
#### Problem Scenario
A customer has a Datadog dashboard showing "CPU by service" that refreshes every 30 seconds. The dashboard query aggregates across 200 services with 500 hosts per service (100k time series). The query times out, showing "Query timeout — try reducing scope."

#### Interview Walkthrough
**Step 1 — Analyze the query**: Navigate to Metrics → CPU → `avg:system.cpu.user{*} by {service}`. The query spans `-6h` window in `rollup(avg, 60)`. This generates 100k time series.

**Step 2 — Check query execution**: Datadog's query engine (internal) executes this by scanning all time series matching the `{*}` filter. With 100k series, each scan reads ~100 data points per series, totaling 10M data points.

**Step 3 — Root cause**: The wildcard `{*}` expands to all services. The dashboard was designed for a small environment (10 services) but the customer grew to 200 services. The `avg` aggregator computes correctly but the query engine exceeds the 30-second timeout.

**Step 4 — Fix**: Add a `top()` aggregator to limit to the top 20 services by CPU. Use `as_count()` for better rollup behavior. Add caching with a 30-second TTL (matching the refresh interval).

**What Datadog evaluates**: Understanding of Datadog query language; time-series query optimization; aggregation strategies; dashboard design best practices.

#### Solution
```python
# Python script to optimize query using Datadog API
from datadog import api

# Before: unbounded query
cpu_series = api.Metric.query(
    query="avg:system.cpu.user{*} by {service}",
    from_=int(time.time()) - 3600,
    to=int(time.time())
)

# After: optimized with top() and rollup
cpu_series = api.Metric.query(
    query="top(avg:system.cpu.user{*}) by {service}(20)",
    from_=int(time.time()) - 3600,
    to=int(time.time())
)

# Use rollup for better performance
cpu_series = api.Metric.query(
    query="avg:system.cpu.user{*}.rollup(avg, 300) by {service}",
    from_=int(time.time()) - 21600,
    to=int(time.time())
)

# Implement client-side caching for dashboard queries
class DashboardQueryCache:
    def __init__(self, default_ttl=30):
        self.cache = {}
        self.default_ttl = default_ttl

    def get_or_query(self, query_key, query_fn):
        now = time.time()
        if query_key in self.cache:
            result, expiry = self.cache[query_key]
            if now < expiry:
                return result
        result = query_fn()
        self.cache[query_key] = (result, now + self.default_ttl)
        return result
```

**Post-mortem**: Add dashboard query performance monitoring. Set up dashboard complexity guardrails. Add query timeout correlation with series count.

#### Follow-ups
- **At Datadog scale**: Build query complexity profiler that warns users when a dashboard query may time out. Implement query result caching at the API layer.
- **Product improvement**: Add "Query Performance" tab in the dashboard editor showing estimated time series count and expected response time.

### Incident: API Rate Limiting — Custom Metrics Ingest (Lab 14)
#### Problem Scenario
A customer's custom metrics stop being accepted by the Datadog API. API responses show "429 Too Many Requests — rate limit exceeded". The customer is sending 10M custom metrics/minute (limit is 5M).

#### Interview Walkthrough
**Step 1 — Check API response headers**: The HTTP response includes:
```
X-RateLimit-Limit: 5000000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1648339200
```

**Step 2 — Check metric submission pattern**: The customer has 500 hosts each sending 20k custom metrics/min. This is 10M/min — double the limit.

**Step 3 — Root cause**: A new deployment added detailed per-request custom metrics (latency, status, size) for every API endpoint. Each request now submits 15 custom metrics. At 666k requests/minute across 500 hosts, that's 10M custom metrics/minute.

**Step 4 — Immediate fix**: Reduce metric cardinality by using tags instead of separate metric names. Use `statsd.histogram` instead of individual `gauge` calls.

**Step 5 — Long-term fix**: Implement metric pre-aggregation on the client side using DDSketch. Use metric submission rate limiting in the Datadog Agent configuration.

**What Datadog evaluates**: Understanding of Datadog API rate limits; metric cardinality reduction; client-side aggregation; DogStatsD best practices.

#### Solution
```python
# Before: one metric per value — high cardinality
def submit_request_metrics(request):
    statsd.gauge(f"api.request.latency.{request.endpoint}", request.latency_ms)
    statsd.gauge(f"api.request.size.{request.endpoint}", request.size_bytes)
    statsd.gauge(f"api.request.status.{request.endpoint}", int(request.success))

# After: tagged metrics with pre-aggregation
import threading
from collections import defaultdict

class MetricsAggregator:
    def __init__(self, flush_interval=10):
        self.buffer = defaultdict(list)
        self.lock = threading.Lock()
        self.flush_interval = flush_interval
        threading.Timer(flush_interval, self.flush).start()

    def record(self, metric, value, tags=None):
        key = (metric, tuple(sorted((tags or {}).items())))
        with self.lock:
            self.buffer[key].append(value)

    def flush(self):
        with self.lock:
            for (metric, tags), values in self.buffer.items():
                # Pre-aggregate: min, max, avg, count, p50, p99
                values.sort()
                n = len(values)
                statsd.gauge(f"{metric}.avg", sum(values) / n, tags=list(tags))
                statsd.gauge(f"{metric}.count", n, tags=list(tags))
                statsd.gauge(f"{metric}.p99", values[int(n * 0.99)], tags=list(tags))
            self.buffer.clear()
        threading.Timer(self.flush_interval, self.flush).start()

# Use tags instead of metric name cardinality
statsd.histogram("api.request.latency", request.latency_ms,
    tags=[f"endpoint:{request.endpoint}", "env:production"])
```

**Post-mortem**: Add custom metrics rate monitoring. Set up alert at 80% of rate limit. Implement metric submission budget per service.

#### Follow-ups
- **At Datadog scale**: Build metric submission rate dashboards. Add auto-scaling rate limits based on account level.
- **Product improvement**: Add "Metric Usage" page showing rate limit consumption and recommendations for reduction.

## System Design for Reliability

### Design Question 1: Design a Time-Series Database for Datadog
Design the storage engine for 500M custom metrics/hour. Discuss compression algorithms (gorilla, XOR), downsampling strategies, retention policies, and query performance optimization.

### Design Question 2: Design Distributed Tracing at Datadog Scale
Design the trace ingestion and storage pipeline for 1B spans/minute. Discuss sampling strategies (heads-based vs tail-based), trace propagation (W3C trace context), and query patterns (trace search, flame graph generation).

### Design Question 3: Design the Datadog Agent for 10M Hosts
Design the Datadog Agent architecture that ingests metrics, logs, and traces from 10M hosts globally. Discuss auto-configuration, integration discovery, resource overhead, and secure data transmission.

## Incident Command Behavioral

### Question 1: Describe a time you helped a customer solve a problem with monitoring.
**STAR**: A customer couldn't identify their slow database query (Lab 05). I helped them set up Datadog Database Monitoring, identified the full table scan via APM traces, and suggested the missing index. Query time dropped from 12s to 30ms.

### Question 2: Tell me about a time you optimized system performance.
**STAR**: The DogStatsD connection exhaustion (Lab 04) was causing 10% metric drop rate. I optimized the client to use persistent connections and buffering, reducing drop rate to 0.01% and decreasing CPU overhead by 15%.

### Question 3: How do you design for scale while maintaining cost efficiency?
**STAR**: For the custom metrics rate limit issue (Lab 14), I implemented client-side pre-aggregation using DDSketch. This reduced custom metric submission by 90% while maintaining p99 accuracy.

### Question 4: Describe a time you used data to drive a product improvement.
**STAR**: I analyzed Agent overhead data (Lab 03) and found process collection consuming 40% CPU. I proposed adding auto-tuning to the Agent — it now adjusts collection frequency based on host capacity.

### Question 5: How do you handle a situation where a tool you built causes customer impact?
**STAR**: The dashboard query timeout (Lab 08) was impacting customer use. I created a query profiler feature that warns users when a query will scan too many time series, preventing timeouts before they happen.

## Study Plan

### Priority Labs for Datadog SRE/Infrastructure
1. **Lab 05 (Slow Query)** — APM/Database Monitoring fundamentals
2. **Lab 03 (High CPU)** — Agent optimization and profiling
3. **Lab 04 (Connection Pool)** — DogStatsD performance tuning
4. **Lab 13 (Kafka Consumer Lag)** — Log ingestion pipeline
5. **Lab 08 (Cache Stampede)** — Query optimization and aggregation
6. **Lab 14 (API Rate Limiting)** — Custom metrics management

### Recommended Schedule
- Week 1: Labs 05, 03 (observability fundamentals + agent optimization)
- Week 2: Labs 04, 14 (metrics ingestion + rate limiting)
- Week 3: Labs 13, 08 (log pipelines + query optimization)
- Week 4: System design + Datadog API practice + behavioral

### Top Incidents Aligned to Datadog Observability Focus (Continued)

### Incident: Security Breach — Agent API Key Leak (Lab 10)
#### Problem Scenario
A customer's Datadog API key is accidentally committed to a public GitHub repository. Within minutes, an attacker uses the key to query all metrics, traces, and logs in the customer's Datadog account.

#### Interview Walkthrough
**Step 1 — Revoke the compromised key**: `DD_API_KEY=<old_key> datadog-agent config | grep api_key`. Generate a new key in Datadog UI: Organization Settings → API Keys → New Key.

**Step 2 — Update the Agent**: On all hosts: update `/etc/datadog-agent/datadog.yaml` with new key: `api_key: <new_key>`. Restart Agent: `sudo systemctl restart datadog-agent`.

**Step 3 — Audit access**: In Datadog, use the Audit Logs feature to see all API calls made with the compromised key. `DD-API-KEY: <old_key>` is shown in the audit trail.

**Step 4 — Root cause**: The API key was hardcoded in a configuration file in the application repository. No secret scanning in CI. No use of Datadog's Agent environment variable override.

**Step 5 — Long-term fix**: Use `DD_API_KEY` environment variable instead of hardcoded `datadog.yaml`. Add secret scanning (GitGuardian, truffleHog) to CI pipeline. Use Datadog's Key Management to rotate keys automatically.

**What Datadog evaluates**: Security incident response; understanding of API key management; Agent configuration best practices; audit trail analysis.

#### Solution
```bash
# Rotate the key immediately (via Datadog API)
curl -X POST "https://api.datadoghq.com/api/v1/api_key/<old_key>" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: <admin_key>" \
  -d '{"data":{"attributes":{"name":"Rotated Key"}}}'

# Update all Agent configurations via automation
ansible all -m replace \
  -a "path=/etc/datadog-agent/datadog.yaml regexp='api_key:.*' replace='api_key: <new_key>'" \
  -b

# Restart all Agents
ansible all -m service -a "name=datadog-agent state=restarted" -b

# Audit the exposure
# In Datadog: Logs → Audit Trail → Search:
# @evt.name:"API Key" @asset.name:"<old_key>"
```

**Post-mortem**: Add secret scanning to CI pipeline. Use Datadog's built-in HIPAA/PCI compliance monitoring. Rotate all API keys quarterly.

#### Follow-ups
- **At Datadog scale**: Implement automatic key rotation via Datadog's API. Use per-service API keys instead of a single key. Enable multi-factor authentication for API access.
- **Product improvement**: Add "key usage anomaly detection" that alerts when a key is used from an unexpected IP or for unusual data volumes.

## Tips

### Datadog SRE/Infrastructure Interview Strategies
1. **Think like a Datadog user**: Every answer should reference real monitoring data. Use specific queries, dashboards, or alerts in your examples.
2. **Know the three pillars**: Metrics (DogStatsD/custom), Traces (APM), Logs (Log Management). Understand how they complement each other.
3. **Agent knowledge is key**: Know how the Datadog Agent works — checks, integrations, DogStatsD, logs collection, trace agent.
4. **Query language fluency**: Practice Datadog query syntax: `avg:metric{tag:value} by {group}.rollup(func, interval)`. Be ready to write and optimize queries.
5. **Understand the product**: Datadog is an observability platform. Know its major features: Dashboards, Monitors, APM, Logs, RUM, Synthetics, Database Monitoring, Network Performance.
6. **Customer empathy**: In every design answer, think about what makes a feature easy or hard for a customer. Datadog is product-led.
7. **Scale thinking**: Design answers should handle millions of hosts, billions of data points. Talk about compression, sampling, aggregation.
8. **OpenTelemetry awareness**: Datadog is a strong supporter of OpenTelemetry. Know how OTel integrates with Datadog (exporters, collectors).
9. **Practice with the Datadog API**: Many questions involve scripting Datadog API calls, creating monitors, or querying metrics programmatically.
10. **Understand the competitive landscape**: Know how Datadog compares to New Relic, Grafana, Splunk, and Prometheus.
