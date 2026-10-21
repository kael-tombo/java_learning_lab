# Theory of Distributed Monitoring

## 1. Why Distributed Monitoring?

Single-node monitoring can't handle distributed systems:
- Multiple services generate metrics simultaneously
- Need to correlate metrics across services
- Traces span multiple service boundaries
- Alerting must consider system-wide state

## 2. Prometheus Architecture

### Core Components
- **Prometheus Server**: Scrapes metrics, stores locally
- **Exporters**: Expose metrics from various systems
- **Pushgateway**: Accepts pushed metrics for batch jobs
- **Alertmanager**: Handles alert routing and deduplication

### Metric Types
- **Counter**: Monotonically increasing value
- **Gauge**: Arbitrarily changing value
- **Histogram**: Distribution of values (bucketed)
- **Summary**: Quantiles over a sliding window

## 3. Prometheus Federation

Federation allows hierarchical scraping:
- Root Prometheus scrapes regional Prometheuses
- Regional Prometheuses scrape service-level ones
- Each level aggregates and filters metrics
- Enables global view of distributed systems

## 4. Thanos

Thanos extends Prometheus for global scale:
- **Sidecar**: Connects to Prometheus, uploads to object store
- **Store Gateway**: Queries historical data from object store
- **Query**: Global query across multiple Prometheuses
- **Compactor**: Downsamples and compacts historical data
- **Ruler**: Rule evaluation with global view

## 5. Cortex

Cortex provides multi-tenant, scalable metrics:
- **Distributor**: Receives and replicates incoming metrics
- **Ingester**: Buffers and stores recent data in memory
- **Store Gateway**: Long-term storage in object store
- **Query Frontend**: Query splitting and caching
- **Ruler**: Rule evaluation per tenant

## 6. Distributed Tracing (OpenTelemetry)

Tracing provides request-level visibility:
- **Trace**: End-to-end request path
- **Span**: Single unit of work within a trace
- **Context Propagation**: Trace context across service boundaries
- **Sampling**: Head-based, tail-based, probabilistic

## 7. Aggregation and Downsampling

For long-term storage, metrics must be aggregated:
- **Downsampling**: Reduce resolution over time
- **Rollups**: Pre-computed aggregates (avg, max, min, count)
- **Retention**: Configurable per resolution tier

## 8. Alerting at Scale

- **Alertmanager**: Deduplication, grouping, routing
- **Silences**: Mute alerts during maintenance
- **Inhibition**: Suppress less important alerts when critical ones fire
- **SLO-based alerting**: Alert on burn rate, not static thresholds
