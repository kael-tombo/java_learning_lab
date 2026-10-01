package com.learning.servicemesh;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

public class Lab {

    record Request(String service, String operation, String payload) {}
    record Response(int status, String result) {}

    static class ServiceProxy {
        private final String serviceName;

        ServiceProxy(String name) { serviceName = name; }

        Response call(String operation, String payload) {
            simulateLatency();
            return new Response(200, serviceName + ":" + operation + " -> " + payload);
        }

        private void simulateLatency() {
            try { Thread.sleep(ThreadLocalRandom.current().nextInt(10, 50)); } catch (InterruptedException e) {}
        }
    }

    static class RetryPolicy {
        final int maxRetries;
        final long baseDelayMs;

        RetryPolicy(int maxRetries, long baseDelayMs) {
            this.maxRetries = maxRetries;
            this.baseDelayMs = baseDelayMs;
        }

        <T> T execute(Supplier<T> op) {
            for (int i = 0; i < maxRetries; i++) {
                try {
                    return op.get();
                } catch (Exception e) {
                    if (i == maxRetries - 1) throw e;
                    try { Thread.sleep(baseDelayMs * (1L << i)); } catch (InterruptedException ie) { Thread.currentThread().interrupt(); }
                }
            }
            throw new RuntimeException("Unreachable");
        }
    }

    static class CircuitBreaker {
        private final AtomicInteger failures = new AtomicInteger(0);
        private final int threshold;
        private volatile boolean open = false;
        private volatile long openTime;

        CircuitBreaker(int threshold) { this.threshold = threshold; }

        <T> T call(Supplier<T> op) {
            if (open) {
                if (System.currentTimeMillis() - openTime > 5000) {
                    open = false;
                    failures.set(0);
                } else {
                    throw new RuntimeException("Circuit open for " + (System.currentTimeMillis() - openTime) + "ms");
                }
            }
            try {
                var result = op.get();
                failures.set(0);
                return result;
            } catch (Exception e) {
                if (failures.incrementAndGet() >= threshold) {
                    open = true;
                    openTime = System.currentTimeMillis();
                }
                throw e;
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Service Mesh Lab ===\n");

        sidecarProxy();
        serviceDiscovery();
        retryAndTimeout();
        circuitBreaking();
        trafficSplitting();
        observability();
    }

    static void sidecarProxy() {
        System.out.println("--- Sidecar Proxy ---");
        var proxy = new ServiceProxy("user-service");
        var response = proxy.call("getUser", "id=42");
        System.out.println("  " + response);
        System.out.println("  Sidecar intercepts ALL traffic (inbound + outbound)");
        System.out.println("  Transparent to application code");
        System.out.println("  Envoy/Linkerd-proxy: common sidecar implementations");
    }

    static void serviceDiscovery() {
        System.out.println("\n--- Service Discovery ---");
        var registry = new ConcurrentHashMap<String, List<String>>();
        registry.put("user-service", List.of("10.0.0.1:8080", "10.0.0.2:8080"));
        registry.put("order-service", List.of("10.0.0.3:8080"));

        System.out.println("  Registered services:");
        registry.forEach((svc, endpoints) -> {
            System.out.println("    " + svc + " -> " + String.join(", ", endpoints));
        });
        System.out.println("  DNS SRV / Kubernetes API / Consul / Eureka");
    }

    static void retryAndTimeout() {
        System.out.println("\n--- Retry & Timeout ---");
        var policy = new RetryPolicy(3, 50);
        var proxy = new ServiceProxy("inventory-service");

        try {
            String result = policy.execute(() -> {
                var r = proxy.call("checkStock", "item=100");
                return r.result();
            });
            System.out.println("  Success: " + result);
        } catch (Exception e) {
            System.out.println("  Failed: " + e.getMessage());
        }
        System.out.println("  Exponential backoff: 50ms, 100ms, 200ms");
    }

    static void circuitBreaking() {
        System.out.println("\n--- Circuit Breaker ---");
        var cb = new CircuitBreaker(3);
        var proxy = new ServiceProxy("faulty-service");

        for (int i = 0; i < 6; i++) {
            final int attempt = i; // effectively final for lambda capture
            try {
                var result = cb.call(() -> {
                    if (attempt >= 2 && attempt <= 4) throw new RuntimeException("Service error");
                    return proxy.call("op", "req-" + attempt).result();
                });
                System.out.println("  [" + attempt + "] Success: " + result);
            } catch (Exception e) {
                System.out.println("  [" + attempt + "] " + e.getMessage());
            }
        }
    }

    static void trafficSplitting() {
        System.out.println("\n--- Traffic Splitting ---");
        var weights = Map.of("v1", 90, "v2", 10);
        var hits = new ConcurrentHashMap<String, AtomicInteger>();
        weights.keySet().forEach(k -> hits.put(k, new AtomicInteger(0)));
        var rng = ThreadLocalRandom.current();

        int total = 1000;
        for (int i = 0; i < total; i++) {
            int roll = rng.nextInt(100);
            if (roll < weights.get("v1")) hits.get("v1").incrementAndGet();
            else hits.get("v2").incrementAndGet();
        }

        System.out.println("  Canary deployment: v1=90%, v2=10%");
        hits.forEach((k, v) -> System.out.println("    " + k + ": " + v.get() + " (" + (v.get() * 100 / total) + "%)"));
    }

    static void observability() {
        System.out.println("\n--- Observability (mTLS, Tracing, Metrics) ---");
        System.out.println("""
  mTLS: automatic mutual TLS between sidecars (no app change)
  Distributed Tracing: Zipkin/Jaeger headers propagated by sidecar
  Metrics: Envoy/Linkerd expose: success rate, latency, request volume
  Access Control: RBAC policies enforced at sidecar level
  Fault Injection: delay, abort requests for testing
    """);
    }
}
