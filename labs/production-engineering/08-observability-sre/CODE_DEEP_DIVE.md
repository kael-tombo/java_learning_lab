# CODE DEEP DIVE: Observability & SRE Production Engineering
## Lab 08 | Production Engineering Academy

---

## Pattern 1: Production OpenTelemetry Context Propagation & Virtual Threads

```java
package com.learning.production.lab08;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Context;
import io.opentelemetry.context.Scope;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TracingContextBridge {
    private static final Logger log = LoggerFactory.getLogger(TracingContextBridge.class);
    private static final Tracer TRACER = GlobalOpenTelemetry.getTracer("com.learning.payment-service", "1.0.0");
    private static final ExecutorService VIRTUAL_EXECUTOR = Executors.newVirtualThreadPerTaskExecutor();

    /**
     * Executes asynchronous work on virtual threads while preserving OTel Trace Context and SLF4J MDC.
     */
    public static void executeWithTrace(String spanName, String orderId, Runnable task) {
        Span parentSpan = TRACER.spanBuilder(spanName)
                .setAttribute("order.id", orderId) // High cardinality attribute is SAFE in trace spans
                .setAttribute("thread.name", Thread.currentThread().getName())
                .startSpan();

        try (Scope scope = parentSpan.makeCurrent()) {
            String traceId = parentSpan.getSpanContext().getTraceId();
            String spanId = parentSpan.getSpanContext().getSpanId();

            // Populate MDC for logs on the current thread
            MDC.put("trace_id", traceId);
            MDC.put("span_id", spanId);
            MDC.put("order_id", orderId);

            log.info("Initiating async order fulfillment within span {}", spanName);

            // Capture current OTel Context to pass across virtual thread boundary
            Context currentContext = Context.current();

            VIRTUAL_EXECUTOR.submit(() -> {
                // Attach context inside the newly spawned virtual thread
                try (Scope asyncScope = currentContext.makeCurrent()) {
                    MDC.put("trace_id", traceId);
                    MDC.put("span_id", spanId);
                    MDC.put("order_id", orderId);
                    
                    try {
                        task.run();
                        parentSpan.setStatus(StatusCode.OK);
                    } catch (Exception ex) {
                        parentSpan.setStatus(StatusCode.ERROR, ex.getMessage());
                        parentSpan.recordException(ex);
                        log.error("Async execution failed for order {}", orderId, ex);
                        throw ex;
                    } finally {
                        MDC.clear(); // Always clean up thread local state
                    }
                }
            });
        } finally {
            MDC.clear();
            parentSpan.end(); // Span must be ended to flush to collector
        }
    }
}
```

---

## Pattern 2: Prometheus SLO Latency Histogram with Explicit Buckets

```java
package com.learning.production.lab08;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

@Configuration
public class MetricsSloConfiguration {

    @Bean
    public Timer orderProcessingSloTimer(MeterRegistry registry) {
        return Timer.builder("http.server.requests.slo")
                .description("Measures HTTP request latency tailored to 99.9% SLO boundaries")
                // Define explicit latency buckets aligned with SLOs (e.g., 25ms, 50ms, 100ms, 200ms, 500ms, 1s)
                .serviceLevelObjectives(
                        Duration.ofMillis(25),
                        Duration.ofMillis(50),
                        Duration.ofMillis(100),
                        Duration.ofMillis(200), // SLO Breach boundary
                        Duration.ofMillis(500),
                        Duration.ofSeconds(1)
                )
                .publishPercentileHistogram(false) // Disable costly dynamic percentile calculation
                .minimumExpectedValue(Duration.ofMillis(5))
                .maximumExpectedValue(Duration.ofSeconds(5))
                .register(registry);
    }
}
```
