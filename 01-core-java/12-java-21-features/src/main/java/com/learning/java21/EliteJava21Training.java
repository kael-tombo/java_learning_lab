package com.learning.java21;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Elite Java 21 Features Training
 *
 * Hands-on coverage of the headline Java 21 features:
 * - Virtual Threads (project Loom)
 * - Pattern Matching for switch (with record patterns)
 * - Records with compact constructors and validated invariants
 * - Sealed hierarchies for exhaustive modeling
 * - Text blocks and String templates (manual interpolation)
 *
 * Every section is designed to be read together with its test suite,
 * which pins the semantics that learners usually get wrong.
 */
public class EliteJava21Training {

    // ============================================================================
    // SECTION 1: RECORDS — compact constructors & derived data
    // ============================================================================

    public record Money(long amountCents, String currency) {
        public Money {
            if (amountCents < 0) {
                throw new IllegalArgumentException("amount must be >= 0, got " + amountCents);
            }
            currency = currency == null ? "USD" : currency.toUpperCase();
        }

        public Money plus(Money other) {
            if (!currency().equals(other.currency())) {
                throw new IllegalArgumentException("Currency mismatch: " + currency + " vs " + other.currency);
            }
            return new Money(amountCents + other.amountCents, currency);
        }

        public double asDouble() {
            return amountCents / 100.0;
        }

        public static Money ofDollars(double dollars, String currency) {
            return new Money(Math.round(dollars * 100), currency);
        }
    }

    public record Range(int low, int high) {
        public Range {
            if (low > high) {
                throw new IllegalArgumentException("low > high: " + low + " > " + high);
            }
        }

        public boolean contains(int value) {
            return value >= low && value <= high;
        }

        public static Range parse(String spec) {
            String[] parts = spec.split("\\.\\.");
            return new Range(Integer.parseInt(parts[0]), Integer.parseInt(parts[1]));
        }
    }

    // ============================================================================
    // SECTION 2: SEALED HIERARCHIES — exhaustive domain modeling
    // ============================================================================

    public sealed interface Shape permits Circle, Rectangle, Triangle {}

    public record Circle(double radius) implements Shape {
        public Circle {
            if (radius <= 0) throw new IllegalArgumentException("radius must be positive");
        }
    }

    public record Rectangle(double width, double height) implements Shape {
        public Rectangle {
            if (width <= 0 || height <= 0) throw new IllegalArgumentException("sides must be positive");
        }
    }

    public record Triangle(double base, double height) implements Shape {
        public Triangle {
            if (base <= 0 || height <= 0) throw new IllegalArgumentException("sides must be positive");
        }
    }

    public static double area(Shape shape) {
        return switch (shape) {
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Rectangle(double w, double h) -> w * h;        // record pattern
            case Triangle(double b, double h) -> 0.5 * b * h;   // record pattern
        }; // no default: sealed types make switch exhaustive
    }

    // ============================================================================
    // SECTION 3: PATTERN MATCHING FOR SWITCH — guarded patterns & null handling
    // ============================================================================

    public sealed interface ApiEvent permits UserCreated, PaymentReceived, Heartbeat {}

    public record UserCreated(String userId) implements ApiEvent {}
    public record PaymentReceived(String orderId, long amountCents) implements ApiEvent {}
    public record Heartbeat(long sequence) implements ApiEvent {}

    public static String describeEvent(ApiEvent event) {
        return switch (event) {
            case null -> "null event";
            case UserCreated u when u.userId().isBlank() -> "user created with blank id";
            case UserCreated(var id) -> "user created: " + id;
            case PaymentReceived p when p.amountCents() < 0 -> "negative payment for " + p.orderId();
            case PaymentReceived(var orderId, var cents) -> "payment " + cents + " cents for order " + orderId;
            case Heartbeat(long seq) when seq % 10 == 0 -> "milestone heartbeat #" + seq;
            case Heartbeat(long seq) -> "heartbeat #" + seq;
        };
    }

    public static String legacyTypeHandling(Object obj) {
        // shows how old instanceof-casts collapse into typed patterns
        if (obj instanceof String s && s.length() > 3) {
            return "long string: " + s;
        }
        if (obj instanceof List<?> list && !list.isEmpty()) {
            return "non-empty list of " + list.size();
        }
        if (obj instanceof Integer i) {
            return "integer " + i;
        }
        return "something else";
    }

    // ============================================================================
    // SECTION 4: VIRTUAL THREADS
    // ============================================================================

    public static class VirtualThreadDemo {

        public static long runConcurrentTasks(int taskCount) throws InterruptedException {
            AtomicInteger completed = new AtomicInteger();
            try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                for (int i = 0; i < taskCount; i++) {
                    final int taskId = i;
                    executor.submit(() -> {
                        Thread.currentThread().setName("demo-task-" + taskId);
                        completed.incrementAndGet();
                        return null;
                    });
                }
            } // close() waits for all tasks
            return completed.get();
        }

        public static List<Long> collectThreadIds(int taskCount) throws InterruptedException {
            List<Long> ids = java.util.Collections.synchronizedList(new ArrayList<>());
            try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                for (int i = 0; i < taskCount; i++) {
                    executor.submit(() -> {
                        ids.add(Thread.currentThread().threadId());
                        return null;
                    });
                }
            }
            return List.copyOf(ids);
        }

        public static boolean isVirtual(Thread thread) {
            return thread.isVirtual();
        }
    }

    // ============================================================================
    // SECTION 5: TEXT BLOCKS & STRING UTILITIES
    // ============================================================================

    public static String jsonConfig(String serviceName, int port) {
        return """
                {
                  "name": "%s",
                  "port": %d,
                  "features": ["metrics", "health"]
                }
                """.formatted(serviceName, port);
    }

    /** Poor-man's string template (before Java 21 templates ship broadly). */
    public static String interpolate(String template, Object... values) {
        StringBuilder out = new StringBuilder();
        int valueIndex = 0;
        for (int i = 0; i < template.length(); i++) {
            char c = template.charAt(i);
            if (c == '{' && i + 1 < template.length() && template.charAt(i + 1) == '}') {
                if (valueIndex >= values.length) {
                    throw new IllegalArgumentException("Missing value for placeholder " + valueIndex);
                }
                out.append(values[valueIndex++]);
                i++; // skip closing brace
            } else {
                out.append(c);
            }
        }
        if (valueIndex < values.length) {
            throw new IllegalArgumentException("Unused values: expected " + valueIndex + ", got " + values.length);
        }
        return out.toString();
    }

    // ============================================================================
    // SECTION 6: SEQUENCED COLLECTIONS (Java 21)
    // ============================================================================

    public static List<String> reversedView(List<String> source) {
        return source.reversed(); // SequencedCollection API
    }

    public static String firstOf(java.util.SequencedCollection<String> seq) {
        return seq.getFirst();
    }

    public static String lastOf(java.util.SequencedCollection<String> seq) {
        return seq.getLast();
    }

    // ============================================================================
    // DEMO
    // ============================================================================

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=".repeat(60));
        System.out.println("ELITE JAVA 21 FEATURES TRAINING");
        System.out.println("=".repeat(60));
        demonstrate();
        System.out.println("\nALL JAVA 21 DEMOS COMPLETED SUCCESSFULLY");
    }

    public static void demonstrate() throws InterruptedException {
        System.out.println("\n### Records ###");
        Money price = Money.ofDollars(19.99, "usd");
        Money tax = Money.ofDollars(1.65, "USD");
        System.out.println("  " + price + " + " + tax + " = " + price.plus(tax));
        System.out.println("  Range.parse(\"1..5\").contains(3) = " + Range.parse("1..5").contains(3));

        System.out.println("\n### Sealed Shapes + Record Patterns ###");
        System.out.printf("  circle r=2 area=%.2f%n", area(new Circle(2)));
        System.out.printf("  rect 3x4 area=%.2f%n", area(new Rectangle(3, 4)));
        System.out.printf("  triangle b=6 h=2 area=%.2f%n", area(new Triangle(6, 2)));

        System.out.println("\n### Pattern Matching for switch ###");
        System.out.println("  " + describeEvent(new UserCreated("u-42")));
        System.out.println("  " + describeEvent(new PaymentReceived("ord-7", 2500)));
        System.out.println("  " + describeEvent(new Heartbeat(20)));
        System.out.println("  " + describeEvent(null));

        System.out.println("\n### Virtual Threads ###");
        long done = VirtualThreadDemo.runConcurrentTasks(1000);
        System.out.println("  completed " + done + " tasks on virtual threads");

        System.out.println("\n### Text Blocks ###");
        System.out.println(jsonConfig("payments", 8443).indent(2).trim());

        System.out.println("\n### Sequenced Collections ###");
        List<String> letters = new ArrayList<>(List.of("a", "b", "c"));
        System.out.println("  first=" + firstOf(letters) + " last=" + lastOf(letters));
        System.out.println("  reversed view=" + reversedView(letters));
    }
}
