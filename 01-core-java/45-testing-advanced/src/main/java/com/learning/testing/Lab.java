package com.learning.testing;

import java.util.*;
import java.util.function.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.Objects;

public class Lab {

    // Test result tracking (moved out of record to avoid conflicts)
    static int passed = 0;
    static int failed = 0;

    static class Calculator {
        int add(int a, int b) { return a + b; }
        int divide(int a, int b) { if (b == 0) throw new ArithmeticException("Division by zero"); return a / b; }
        int[] fibonacci(int n) {
            if (n <= 0) return new int[0];
            var result = new int[n];
            for (int i = 0; i < n; i++) result[i] = i < 2 ? i : result[i - 1] + result[i - 2];
            return result;
        }
    }

    static class ShoppingCart {
        private final Map<String, Integer> items = new ConcurrentHashMap<>();

        void add(String product, int qty) { items.merge(product, qty, Integer::sum); }
        void remove(String product) { items.remove(product); }
        boolean contains(String product) { return items.containsKey(product); }
        int totalItems() { return items.values().stream().mapToInt(Integer::intValue).sum(); }
        void clear() { items.clear(); }
    }

    static class AsyncService {
        CompletableFuture<String> fetchData(String key) {
            return CompletableFuture.supplyAsync(() -> {
                try { Thread.sleep(50); } catch (InterruptedException e) {}
                return "data-for-" + key;
            });
        }
    }

    record TestResult(String name, boolean passed, String reason) {}

    static void assertTrue(String name, boolean condition) {
        if (condition) { passed++; System.out.println("  PASS: " + name); }
        else { failed++; System.out.println("  FAIL: " + name); }
    }

    static void assertEquals(String name, Object expected, Object actual) {
        assertTrue(name, Objects.equals(expected, actual));
    }

    static void assertThrows(String name, Class<? extends Throwable> exType, Runnable block) {
        try { block.run(); failed++; System.out.println("  FAIL: " + name + " (no exception)"); }
        catch (Exception e) {
            if (exType.isInstance(e)) { passed++; System.out.println("  PASS: " + name + " [" + e.getClass().getSimpleName() + "]"); }
            else { failed++; System.out.println("  FAIL: " + name + " (wrong exception: " + e.getClass().getSimpleName() + ")"); }
        }
    }

    static void report() {
        System.out.println("\n  Results: " + passed + " passed, " + failed + " failed");
    }

    public static void main(String[] args) throws Exception {
        System.out.println("=== Testing Advanced Lab ===\n");

        unitTesting();
        parameterizedTests();
        exceptionTesting();
        mocking();
        asyncTesting();
        integrationTest();
    }

    static void unitTesting() {
        System.out.println("--- Unit Testing ---");
        var calc = new Calculator();

        assertEquals("add(2,3) == 5", 5, calc.add(2, 3));
        assertEquals("add(-1,1) == 0", 0, calc.add(-1, 1));
        assertEquals("fib(5) first", 0, calc.fibonacci(5)[0]);
        assertEquals("fib(5) last", 3, calc.fibonacci(5)[4]);
        assertEquals("fib(0).length", 0, calc.fibonacci(0).length);

        var cart = new ShoppingCart();
        cart.add("apple", 2);
        assertEquals("cart contains apple", true, cart.contains("apple"));
        assertEquals("cart total", 2, cart.totalItems());
        cart.remove("apple");
        assertEquals("cart empty after remove", false, cart.contains("apple"));
    }

    static void parameterizedTests() {
        System.out.println("\n--- Parameterized Tests ---");
        var calc = new Calculator();
        var testCases = List.of(
            new int[]{1, 1, 2}, new int[]{-1, -1, -2},
            new int[]{100, 200, 300}, new int[]{0, 0, 0}
        );

        for (var tc : testCases) {
            assertEquals("add(" + tc[0] + "," + tc[1] + ") == " + tc[2],
                tc[2], calc.add(tc[0], tc[1]));
        }
    }

    static void exceptionTesting() {
        System.out.println("\n--- Exception Testing ---");
        var calc = new Calculator();

        assertThrows("divide by zero", ArithmeticException.class,
            () -> calc.divide(5, 0));
        assertEquals("divide(10,2)", 5, calc.divide(10, 2));
    }

    static void mocking() {
        System.out.println("\n--- Mocking (Manual) ---");
        var realCart = new ShoppingCart();
        var spyCart = new ShoppingCart() {
            public void add(String product, int qty) {
                System.out.println("  [SPY] add called with " + product + " x" + qty);
                super.add(product, qty);
            }
        };
        spyCart.add("test-item", 1);
        assertEquals("spy tracked item", true, spyCart.contains("test-item"));
        System.out.println("""
            Mockito: @Mock, @InjectMocks, verify()
            Stub: when(mock.getX()).thenReturn(value)
            Spy: partial real + partial mock
              """);
    }

    static void asyncTesting() throws Exception {
        System.out.println("\n--- Async Testing ---");
        var svc = new AsyncService();
        var result = svc.fetchData("key-1").get(1, TimeUnit.SECONDS);
        assertEquals("async fetch", "data-for-key-1", result);

        var combined = svc.fetchData("a").thenCombine(svc.fetchData("b"), (a, b) -> a + "|" + b);
        var combo = combined.get(1, TimeUnit.SECONDS);
        assertEquals("combined async", "data-for-a|data-for-b", combo);
    }

    static void integrationTest() {
        System.out.println("\n--- Integration Test Approach ---");
        System.out.println("""
            @SpringBootTest - loads full context
            @WebMvcTest - controller layer only
            @DataJpaTest - repository layer only
            @Testcontainers - real DB in Docker
            @RestClientTest - REST client mocking
            WireMock - stub external HTTP services
            Test pyramid: unit >> integration >> e2e
              """);
        report();
    }
}