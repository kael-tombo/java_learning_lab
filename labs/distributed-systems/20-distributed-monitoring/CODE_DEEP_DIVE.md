# Code Deep Dive — Distributed Monitoring

## 1. MetricRegistry Implementation

Thread-safe metric registration and reporting:
- ConcurrentHashMap for metric storage
- Support for counters, gauges, histograms
- Label support for multi-dimensional metrics
- Periodic export to monitoring system

## 2. PrometheusClient Implementation

- Fetches metrics from Prometheus HTTP API
- Parses PromQL responses
- Supports instant and range queries
- Implements series discovery

## 3. TracingSpan Implementation

`java
public class TracingSpan implements AutoCloseable {
    private final String traceId;
    private final String spanId;
    private final String parentSpanId;
    private final long startTime;
    private final Map<String, String> attributes;
    
    public void addEvent(String name, Map<String, String> attrs) { }
    public void setStatus(Status status) { }
    public void close() { /* record duration */ }
}
`

## 4. AlertEvaluator Implementation

- Evaluates PromQL expressions against metric data
- Checks threshold conditions
- Tracks alert state (pending, firing, resolved)
- Sends notifications to Alertmanager

## 5. AggregationPipeline Implementation

- Configurable aggregation windows
- Supports avg, sum, min, max, count, quantile
- Time-based and fixed-size windows
- Output to metric registry or monitoring backend
