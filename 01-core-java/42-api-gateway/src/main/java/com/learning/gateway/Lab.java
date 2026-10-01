package com.learning.gateway;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Predicate;

public class Lab {

    record Request(String path, String method, String body, Map<String, String> headers) {}
    record Response(int status, String body, Map<String, String> headers) {}

    interface Filter {
        Response filter(Request request, NextFilter next);
    }

    interface NextFilter {
        Response next(Request request);
    }

    static class Gateway {
        private final List<Filter> filters = new ArrayList<>();
        private final Map<String, String> routes = new ConcurrentHashMap<>();

        void addFilter(Filter filter) { filters.add(filter); }

        void addRoute(String pathPrefix, String target) {
            routes.put(pathPrefix, target);
        }

        Response execute(Request request) {
            var chain = new LinkedList<>(filters);
            NextFilter finalHandler = req -> {
                var target = routes.entrySet().stream()
                    .filter(e -> req.path().startsWith(e.getKey()))
                    .findFirst();
                if (target.isEmpty()) return new Response(404, "Not Found", Map.of());
                return new Response(200, "OK from " + target.get().getValue(), Map.of());
            };

            // Use a mutable holder to allow self-reference in lambda
            class Holder { NextFilter value; }
            Holder holder = new Holder();
            holder.value = req -> {
                if (holder.value == null) return finalHandler.next(req); // safety
                if (chain.isEmpty()) return finalHandler.next(req);
                var filter = chain.removeFirst();
                return filter.filter(req, holder.value);
            };

            return holder.value.next(request);
        }
    }

    public static void main(String[] args) {
        System.out.println("=== API Gateway Lab ===\n");

        routing();
        filterChain();
        rateLimiting();
        circuitBreaker();
        aggregation();
    }

    static void routing() {
        System.out.println("--- Routing ---");
        var gw = new Gateway();
        gw.addRoute("/users", "user-service:8081");
        gw.addRoute("/orders", "order-service:8082");
        gw.addRoute("/payments", "payment-service:8083");

        for (var path : List.of("/users/123", "/orders/456", "/products", "/")) {
            var req = new Request(path, "GET", "", Map.of());
            var resp = gw.execute(req);
            System.out.println("  " + path + " -> " + resp.body());
        }
    }

    static void filterChain() {
        System.out.println("\n--- Filter Chain ---");
        var gw = new Gateway();
        gw.addRoute("/api", "backend:9000");

        gw.addFilter((req, next) -> {
            System.out.println("  [Auth] checking token");
            if (!req.headers().containsKey("Authorization")) {
                return new Response(401, "Unauthorized", Map.of());
            }
            return next.next(req);
        });

        gw.addFilter((req, next) -> {
            System.out.println("  [Log] " + req.method() + " " + req.path());
            return next.next(req);
        });

        var secured = new Request("/api/data", "GET", "", Map.of("Authorization", "Bearer tok"));
        var unsecured = new Request("/api/data", "GET", "", Map.of());

        System.out.println("  Secured request:");
        var r1 = gw.execute(secured);
        System.out.println("  Status: " + r1.status());

        System.out.println("  Unsecured request:");
        var r2 = gw.execute(unsecured);
        System.out.println("  Status: " + r2.status());
    }

    static void rateLimiting() {
        System.out.println("\n--- Rate Limiting ---");
        var limits = new ConcurrentHashMap<String, AtomicInteger>();

        Predicate<String> allowRequest = clientId -> {
            var count = limits.computeIfAbsent(clientId, k -> new AtomicInteger(0));
            int current = count.incrementAndGet();
            if (current > 5) {
                System.out.println("  " + clientId + ": RATE LIMITED after " + (current - 1) + " requests");
                return false;
            }
            System.out.println("  " + clientId + ": allowed (request #" + current + ")");
            return true;
        };

        var scheduler = Executors.newScheduledThreadPool(1);
        scheduler.scheduleAtFixedRate(limits::clear, 0, 10, TimeUnit.SECONDS);

        for (int i = 0; i < 7; i++) allowRequest.test("client-A");
        scheduler.shutdown();
    }

    static void circuitBreaker() {
        System.out.println("\n--- Circuit Breaker ---");
        record CircuitBreaker(int threshold, long timeoutMs) {
            enum State { CLOSED, OPEN, HALF_OPEN }
        }

        System.out.println("""
  States: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (probing) -> CLOSED
  Threshold: 5 failures in 10s -> OPEN
  Timeout: 30s -> HALF_OPEN
  On success in HALF_OPEN -> CLOSED
  On failure in HALF_OPEN -> OPEN again
    """);
        System.out.println("  Prevents cascading failures & gives downstream time to recover");
    }

    static void aggregation() {
        System.out.println("\n--- Response Aggregation ---");
        System.out.println("  Gateway fan-out: parallel calls to multiple backends");
        System.out.println("  Scenario: product page needs ->");
        System.out.println("    product-service: product details");
        System.out.println("    review-service: reviews");
        System.out.println("    inventory-service: stock info");
        System.out.println("    recommendation-service: related items");
        System.out.println("  Gateway merges all responses into one composite response");
        System.out.println("  Reduces client-side N+1 calls to 1 call");
    }
}
