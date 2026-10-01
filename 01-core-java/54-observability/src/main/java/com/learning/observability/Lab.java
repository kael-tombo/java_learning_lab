package com.learning.observability;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class Lab {

    static class Logger {
        enum Level { DEBUG, INFO, WARN, ERROR }
        private final String name;

        Logger(String name) { this.name = name; }

        void log(Level level, String message, Map<String, Object> context) {
            var entry = new LinkedHashMap<String, Object>();
            entry.put("timestamp", System.currentTimeMillis());
            entry.put("level", level);
            entry.put("logger", name);
            entry.put("message", message);
            if (context != null) entry.put("context", context);
            System.out.println("  " + entry);
        }

        void info(String msg) { log(Level.INFO, msg, null); }
        void error(String msg, Map<String, Object> ctx) { log(Level.ERROR, msg, ctx); }
    }

    static class Metrics {
        private final ConcurrentHashMap<String, AtomicLong> counters = new ConcurrentHashMap<>();
        private final ConcurrentHashMap<String, AtomicLong> gauges = new ConcurrentHashMap<>();

        void increment(String name) {
            counters.computeIfAbsent(name, k -> new AtomicLong()).incrementAndGet();
        }

        void gauge(String name, long value) {
            gauges.put(name, new AtomicLong(value));
        }

        Map<String, Long> snapshot() {
            var result = new HashMap<String, Long>();
            counters.forEach((k, v) -> result.put("counter_" + k, v.get()));
            gauges.forEach((k, v) -> result.put("gauge_" + k, v.get()));
            return result;
        }
    }

    static class Tracer {
        private final String traceId;
        private final List<Span> spans = new CopyOnWriteArrayList<>();

        Tracer() { this.traceId = UUID.randomUUID().toString().substring(0, 8); }

        Span startSpan(String name) {
            var span = new Span(name, traceId);
            spans.add(span);
            return span;
        }

        record Span(String name, String traceId, long startTime) {
            Span(String name, String traceId) {
                this(name, traceId, System.nanoTime());
            }
        }

        void report() {
            System.out.println("  Trace " + traceId + " spans:");
            spans.forEach(s -> System.out.println("    " + s.name() + " [" + s.startTime() + "]"));
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Observability Lab ===\n");

        structuredLogging();
        metricsCollector();
        distributedTracing();
        healthChecks();
        alerting();
    }

    static void structuredLogging() {
        System.out.println("--- Structured Logging ---");
        var log = new Logger("OrderService");

        log.info("Order created");
        log.error("Payment failed", Map.of(
            "orderId", "ORD-123",
            "amount", 99.99,
            "errorCode", "INSUFFICIENT_FUNDS"
        ));

        System.out.println("""
  Structured = JSON format (machine-readable)
  vs Unstructured = plain text (human-only)
  Log aggregation: Elasticsearch / Loki / CloudWatch
  Log levels: TRACE < DEBUG < INFO < WARN < ERROR < FATAL
    """);
    }

    static void metricsCollector() {
        System.out.println("\n--- Metrics Collection ---");
        var metrics = new Metrics();

        for (int i = 0; i < 100; i++) metrics.increment("api.requests");
        for (int i = 0; i < 5; i++) metrics.increment("api.errors");
        metrics.gauge("active.connections", 42);
        metrics.gauge("heap.used.mb", 256);

        System.out.println("  Metrics snapshot:");
        metrics.snapshot().forEach((k, v) -> System.out.println("    " + k + " = " + v));

        System.out.println("""
  Types:
  Counter:    cumulative (total requests, errors)
  Gauge:      point-in-time (connections, memory)
  Histogram:  distribution (latency p50, p95, p99)
  Summary:    sliding window percentile

  Prometheus / Micrometer / Dropwizard Metrics
    """);
    }

    static void distributedTracing() {
        System.out.println("\n--- Distributed Tracing ---");
        var tracer = new Tracer();

        var s1 = tracer.startSpan("HTTP GET /orders/123");
        var s2 = tracer.startSpan("SELECT FROM orders");
        var s3 = tracer.startSpan("Cache get order:123");

        tracer.report();

        System.out.println("""
  Trace: end-to-end request path across services
  Span: single unit of work (service call, DB query)
  Trace ID: propagated via headers (x-trace-id, W3C traceparent)
  Context propagation: ThreadLocal / ScopedValue / MDC

  Tools: Jaeger, Zipkin, OpenTelemetry (OTel)
  OTel SDK: TracerProvider -> Tracer -> Span
    """);
    }

    static void healthChecks() {
        System.out.println("\n--- Health Checks ---");
        interface HealthIndicator {
            String name();
            boolean isHealthy();
        }

        var checks = List.<HealthIndicator>of(
            new HealthIndicator() {
                public String name() { return "database"; }
                public boolean isHealthy() { return true; }
            },
            new HealthIndicator() {
                public String name() { return "redis"; }
                public boolean isHealthy() { return true; }
            },
            new HealthIndicator() {
                public String name() { return "upstream-api"; }
                public boolean isHealthy() { return false; }
            }
        );

        System.out.println("  Health check results:");
        int healthy = 0;
        for (var c : checks) {
            boolean ok = c.isHealthy();
            if (ok) healthy++;
            System.out.println("    " + c.name() + ": " + (ok ? "UP" : "DOWN"));
        }
        System.out.println("  Overall: " + (healthy == checks.size() ? "UP" : "DEGRADED"));

        System.out.println("""
  Liveness:  is the app alive? (restart if dead)
  Readiness: can the app serve traffic? (remove from LB)
  Startup:   has the app started? (Kubernetes startup probe)
    """);
    }

    static void alerting() {
        System.out.println("\n--- Alerting ---");
        System.out.println("""
  Prometheus + Alertmanager:

  Rule example:
    alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels: severity: critical
    annotations:
      summary: "Error rate above 5% for 5 minutes"

  Severity: info < warning < critical
  Notification channels:
  - PagerDuty / OpsGenie (critical)
  - Slack / email (warning)
  - Webhook (custom)

  SRE Golden Signals:
  Latency, Traffic, Errors, Saturation
    """);
    }
}
