# EXERCISES: Observability, OpenTelemetry & SRE Reliability
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Reproducing and Remediating a Prometheus Cardinality Explosion

### 1. Objective
Deliberately trigger a metric cardinality explosion in a local Prometheus instance, observe memory consumption surge, use Prometheus TSDB administrative APIs to isolate the offending label, and remediate the explosion using runtime metric relabeling.

### 2. Implementation Tasks
1. Build a Java test harness using Micrometer that registers a counter with a random UUID tag:
   ```java
   public class CardinalityBomb {
       public static void main(String[] args) {
           MeterRegistry registry = new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
           for (int i = 0; i < 200_000; i++) {
               registry.counter("api.requests", "user_uuid", UUID.randomUUID().toString()).increment();
           }
       }
   }
   ```
2. Run the application and scrape it via a local Prometheus container:
   - Monitor Prometheus memory usage: observe RAM ballooning to several gigabytes.
3. Query the Prometheus TSDB status API:
   ```bash
   curl -s http://localhost:9090/api/v1/status/tsdb | jq .data.labelValueCountByLabelName
   ```
   - Identify that `user_uuid` accounts for $> 99\%$ of all active series.
4. Add an ingestion relabeling rule in `prometheus.yml`:
   ```yaml
   scrape_configs:
     - job_name: "cardinality-test"
       static_configs:
         - targets: ["host.docker.internal:8080"]
       metric_relabel_configs:
         - action: labeldrop
           regex: "user_uuid"
   ```
5. Reload Prometheus: verify active series drops to 1 and memory usage immediately flattens.

---

## Exercise 2: Implementing Trace Context Propagation Across CompletableFuture & Virtual Threads

### 1. Objective
Demonstrate how standard `CompletableFuture` loses W3C TraceContext across thread boundaries, and implement the `TraceContextTaskDecorator` to bridge tracing DAGs end-to-end.

### 2. Implementation Tasks
1. Build two Spring Boot microservices: `OrderService` (caller) and `PaymentService` (downstream).
2. In `OrderService`, expose an endpoint that invokes `PaymentService` inside an un-instrumented `CompletableFuture.supplyAsync()`:
   ```bash
   curl http://localhost:8080/api/orders/order-123
   ```
3. Open Jaeger or Tempo:
   - Observe that the trace is broken: `OrderService` creates a 2ms trace, and `PaymentService` logs a completely separate, disconnected root trace!
4. Refactor `OrderService` using `TraceContextTaskDecorator`:
   - Wrap the asynchronous supplier with `Context.current().wrapSupplier()`.
5. Re-run the request:
   - Open Jaeger / Tempo and verify that `PaymentService` now renders as a **child span** directly beneath `OrderService` sharing the exact same `TraceID`.

---

## Exercise 3: Building and Testing a Multi-Burn-Rate Alert with Synthetic Traffic

### 1. Objective
Configure Google SRE's 14.4x Multi-Window Multi-Burn-Rate alert rule in Prometheus, generate synthetic HTTP traffic, simulate a high-velocity failure, and verify the alert pages within 2 minutes.

### 2. Implementation Tasks
1. Deploy Prometheus and Alertmanager with the `PaymentServiceErrorBudgetFastBurn` alert rule from Pattern 4 of CODE DEEP DIVE.
2. Launch a synthetic HTTP traffic generator (`hey` or `k6`) sending 1,000 requests/sec with a healthy error rate of $0.05\%$:
   - Verify zero alerts fire.
3. Inject a failure: increase synthetic error responses to $2.0\%$ (exceeding the $14.4\times$ burn threshold for a 99.9% SLO):
   ```bash
   # Synthetic error injection
   curl -X POST http://localhost:8080/test/chaos/inject-errors?rate=0.02
   ```
4. Monitor Prometheus alert evaluations:
   - Verify that within **2 minutes**, both the 5m short window and the 1h long window breach the threshold simultaneously.
   - Verify Alertmanager emits a Critical P1 page notification to your webhook / Slack channel.
5. Disable error injection:
   - Verify that because the 5-minute short window drops below the threshold immediately, the alert **resets to OK within 3 minutes**, preventing false alarms!

---

## Exercise 4: Setting Up Tail-Based Sampling in OTel Collector & Measuring Cost Reduction

### 1. Objective
Deploy an OpenTelemetry Collector with Tail-Based Sampling, process a stream of 10,000 transactions containing 9,800 healthy 2ms requests, 150 slow requests (>300ms), and 50 errors (HTTP 500), and verify that 100% of errors and slow requests are retained while cutting total stored span volume by $> 90\%$.

### 2. Implementation Tasks
1. Run the OpenTelemetry Collector using the configuration from Pattern 3 of CODE DEEP DIVE.
2. Run a synthetic trace generator emitting:
   - 9,800 healthy spans ($< 20\text{ms}$, HTTP 200).
   - 150 slow spans ($> 400\text{ms}$, HTTP 200).
   - 50 error spans (HTTP 500 with stack traces).
3. Query the Tempo / Jaeger backend storage:
   - Verify that **all 50 error traces** are present in storage.
   - Verify that **all 150 slow traces** are present in storage.
   - Verify that only $\approx 490$ healthy traces ($5\%$) were retained.
4. Calculate total telemetry data reduction:
   $$\text{Data Reduction} = 1.0 - \frac{50 + 150 + 490}{10{,}000} = 93.1\% \text{ reduction}$$
   Proving that tail-based sampling achieves a **93% reduction in cloud tracing storage costs** with zero loss of failure telemetry!
