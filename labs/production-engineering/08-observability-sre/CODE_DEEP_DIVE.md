# CODE DEEP DIVE: Observability, OpenTelemetry & SRE Patterns
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Spring Boot 3 Unified Micrometer Observation & OpenTelemetry Integration

```java
package com.learning.production.lab08;

import io.micrometer.observation.Observation;
import io.micrometer.observation.ObservationRegistry;
import io.micrometer.observation.annotation.Observed;
import io.opentelemetry.api.trace.Span;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Demonstrates the unified Micrometer 1.10+ / Spring Boot 3 Observation API.
 * A single observation automatically publishes BOTH:
 *   1. Prometheus metric timer (low-cardinality tags)
 *   2. OpenTelemetry distributed trace span (high-cardinality attributes)
 */
@Service
public class OrderFulfillmentService {

    private static final Logger log = LoggerFactory.getLogger(OrderFulfillmentService.class);
    private final ObservationRegistry observationRegistry;
    private final PaymentClient paymentClient;

    public OrderFulfillmentService(ObservationRegistry observationRegistry, PaymentClient paymentClient) {
        this.observationRegistry = observationRegistry;
        this.paymentClient = paymentClient;
    }

    public OrderResult processFulfillment(OrderRequest request) {
        return Observation.createNotStarted("order.fulfillment", observationRegistry)
                // Low-cardinality keys -> Bound to Prometheus Metric Tags:
                .lowCardinalityKeyValue("order.tier", request.tier().name())
                .lowCardinalityKeyValue("payment.method", request.paymentMethod())
                // High-cardinality keys -> Bound to OpenTelemetry Trace Span Attributes:
                .highCardinalityKeyValue("order.id", request.orderId())
                .highCardinalityKeyValue("customer.id", request.customerId())
                .observe(() -> {
                    log.info("Executing fulfillment pipeline for customer {}", request.customerId());

                    // Enrich active OpenTelemetry span with runtime business event:
                    Span.current().addEvent("inventory_reserved");

                    PaymentResponse payment = paymentClient.authorize(request.paymentDetails());
                    if (!payment.isSuccessful()) {
                        Span.current().recordException(new PaymentDeclinedException(payment.reason()));
                        throw new PaymentDeclinedException(payment.reason());
                    }

                    return new OrderResult(request.orderId(), OrderStatus.COMPLETED);
                });
    }
}
```

---

## Pattern 2: Context Propagation Across Asynchronous & Virtual Threads

```java
package com.learning.production.lab08;

import io.opentelemetry.context.Context;
import io.opentelemetry.context.Scope;
import org.slf4j.MDC;
import org.springframework.core.task.TaskDecorator;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.*;

/**
 * Bridges OpenTelemetry Trace Context and SLF4J MDC across asynchronous
 * thread pools and Java 21 Virtual Threads.
 */
@Component
public class TraceContextTaskDecorator implements TaskDecorator {

    @Override
    public Runnable decorate(Runnable runnable) {
        // 1. Capture context from the caller thread
        Context otelContext = Context.current();
        Map<String, String> mdcContext = MDC.getCopyOfContextMap();

        return () -> {
            // 2. Attach context inside the worker thread
            Map<String, String> previousMdc = MDC.getCopyOfContextMap();
            if (mdcContext != null) {
                MDC.setContextMap(mdcContext);
            } else {
                MDC.clear();
            }

            try (Scope scope = otelContext.makeCurrent()) {
                // 3. Execute original business logic with valid TraceID
                runnable.run();
            } finally {
                // 4. Restore worker thread baseline state
                if (previousMdc != null) {
                    MDC.setContextMap(previousMdc);
                } else {
                    MDC.clear();
                }
            }
        };
    }

    /**
     * Helper to wrap raw CompletableFuture asynchronous suppliers:
     */
    public static <T> CompletableFuture<T> supplyAsyncWithContext(
            java.util.function.Supplier<T> supplier, 
            Executor executor) {
        
        Context capturedContext = Context.current();
        return CompletableFuture.supplyAsync(() -> {
            try (Scope scope = capturedContext.makeCurrent()) {
                return supplier.get();
            }
        }, executor);
    }
}
```

---

## Pattern 3: OpenTelemetry Collector Tail-Based Sampling Pipeline

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

  # Tail-Based Sampling Processor:
  # Evaluates complete traces before deciding whether to persist or drop!
  tail_sampling:
    decision_wait: 10s
    num_traces: 50000
    expected_new_traces_per_sec: 2000
    policies:
      # Policy 1: Always sample 100% of error spans
      - name: sample-errors
        type: status_code
        status_code: { status_codes: [ERROR] }

      # Policy 2: Always sample 100% of HTTP 5xx responses
      - name: sample-http-5xx
        type: numeric_attribute
        numeric_attribute:
          key: http.status_code
          min_value: 500
          max_value: 599

      # Policy 3: Always sample 100% of slow requests (> 300ms)
      - name: sample-slow-requests
        type: latency
        latency: { threshold_ms: 300 }

      # Policy 4: Sample 5% of healthy baseline traffic for statistical percentiles
      - name: probabilistic-sample-healthy
        type: probabilistic
        probabilistic: { sampling_percentage: 5.0 }

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp/tempo:
    endpoint: tempo-distributor.monitoring.svc:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling, batch]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

---

## Pattern 4: Google SRE Multi-Window Multi-Burn-Rate Prometheus Alert Manifest

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: payment-orchestrator-slo-burn-rate
  namespace: production
  labels:
    role: alert-rules
spec:
  groups:
    - name: payment-orchestrator-slo
      rules:
        # P1 CRITICAL PAGE: 14.4x Burn Rate (2% budget consumed in 1 hour)
        - alert: PaymentServiceErrorBudgetFastBurn
          expr: >-
            (
              sum(rate(http_requests_total{app="payment-orchestrator", status=~"5.*"}[1h]))
              /
              sum(rate(http_requests_total{app="payment-orchestrator"}[1h]))
            ) > (14.4 * (1 - 0.999))
            and
            (
              sum(rate(http_requests_total{app="payment-orchestrator", status=~"5.*"}[5m]))
              /
              sum(rate(http_requests_total{app="payment-orchestrator"}[5m]))
            ) > (14.4 * (1 - 0.999))
          for: 2m
          labels:
            severity: critical
            tier: tier-0
          annotations:
            summary: "Payment Service 14.4x Error Budget Burn Rate (P1 Page)"
            description: "Service is burning monthly error budget at 14.4x speed. 100% of budget will deplete in 2 days!"
            runbook_url: "https://wiki.corp.internal/runbooks/payment-burn-rate"

        # P2 URGENT PAGE: 6.0x Burn Rate (5% budget consumed in 6 hours)
        - alert: PaymentServiceErrorBudgetSlowBurn
          expr: >-
            (
              sum(rate(http_requests_total{app="payment-orchestrator", status=~"5.*"}[6h]))
              /
              sum(rate(http_requests_total{app="payment-orchestrator"}[6h]))
            ) > (6.0 * (1 - 0.999))
            and
            (
              sum(rate(http_requests_total{app="payment-orchestrator", status=~"5.*"}[30m]))
              /
              sum(rate(http_requests_total{app="payment-orchestrator"}[30m]))
            ) > (6.0 * (1 - 0.999))
          for: 15m
          labels:
            severity: warning
          annotations:
            summary: "Payment Service 6x Error Budget Burn Rate (P2 Page)"
            description: "Service has consumed 5% of monthly error budget over 6 hours."
```

---

## Pattern 5: Structured JSON Logging with W3C Trace Injection & PII Masking

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- src/main/resources/logback-spring.xml -->
<configuration scan="true" scanPeriod="30 seconds">

    <!-- Production JSON Console Appender -->
    <appender name="JSON_CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LoggingEventCompositeJsonEncoder">
            <providers>
                <timestamp>
                    <timeZone>UTC</timeZone>
                </timestamp>
                <logLevel/>
                <loggerName/>
                <threadName/>
                <message/>
                <stackTrace/>
                
                <!-- Automatically extracts W3C TraceContext from MDC -->
                <mdc>
                    <includeMdcKeyName>trace_id</includeMdcKeyName>
                    <includeMdcKeyName>span_id</includeMdcKeyName>
                    <includeMdcKeyName>customer_id</includeMdcKeyName>
                </mdc>
                
                <arguments/>
                
                <!-- Custom PII Regex Masking Provider for PAN / CVV -->
                <provider class="com.learning.production.lab08.SensitiveDataMaskingProvider"/>
            </providers>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="JSON_CONSOLE"/>
    </root>
</configuration>
```
