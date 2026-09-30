package com.learning.patterns;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.DoubleBinaryOperator;

/**
 * Elite Design Patterns Training
 *
 * Implements the most interview-relevant GoF patterns as small, self-contained
 * frameworks: Singleton, Builder, Factory Method, Strategy, Observer,
 * Decorator, Template Method, and Adapter.
 *
 * Each implementation is deliberately minimal but production-shaped:
 * thread-safety, immutability, and open/closed principles are demonstrated
 * rather than just mentioned.
 */
public class EliteDesignPatternsTraining {

    // ============================================================================
    // SECTION 1: SINGLETON (double-checked locking + holder idiom)
    // ============================================================================

    public static class ConfigurationService {
        private static volatile ConfigurationService instance;
        private final AtomicLong accessCount = new AtomicLong();
        private final java.util.Map<String, String> settings = new java.util.HashMap<>();

        private ConfigurationService() {
            settings.put("env", "dev");
            settings.put("region", "eu-west-1");
        }

        /** Double-checked locking: volatile read is cheap on the fast path. */
        public static ConfigurationService getInstance() {
            if (instance == null) {
                synchronized (ConfigurationService.class) {
                    if (instance == null) {
                        instance = new ConfigurationService();
                    }
                }
            }
            return instance;
        }

        public String get(String key) {
            accessCount.incrementAndGet();
            return settings.get(key);
        }

        public long getAccessCount() {
            return accessCount.get();
        }

        /** Initialization-on-demand holder idiom: lazy + lock-free + thread-safe. */
        public static class HolderSingleton {
            private HolderSingleton() {}

            private static class Holder {
                static final HolderSingleton INSTANCE = new HolderSingleton();
            }

            public static HolderSingleton getInstance() {
                return Holder.INSTANCE;
            }
        }
    }

    // ============================================================================
    // SECTION 2: BUILDER (immutable target + validation)
    // ============================================================================

    public static class HttpServerConfig {
        private final String host;
        private final int port;
        private final boolean tlsEnabled;
        private final int maxConnections;
        private final List<String> allowedOrigins;

        private HttpServerConfig(Builder b) {
            this.host = b.host;
            this.port = b.port;
            this.tlsEnabled = b.tlsEnabled;
            this.maxConnections = b.maxConnections;
            this.allowedOrigins = List.copyOf(b.allowedOrigins);
        }

        public String getHost() { return host; }
        public int getPort() { return port; }
        public boolean isTlsEnabled() { return tlsEnabled; }
        public int getMaxConnections() { return maxConnections; }
        public List<String> getAllowedOrigins() { return allowedOrigins; }

        public static Builder builder() { return new Builder(); }

        public static final class Builder {
            private String host = "localhost";
            private int port = 8080;
            private boolean tlsEnabled = false;
            private int maxConnections = 100;
            private final List<String> allowedOrigins = new ArrayList<>();

            public Builder host(String host) { this.host = host; return this; }
            public Builder port(int port) { this.port = port; return this; }
            public Builder tls(boolean enabled) { this.tlsEnabled = enabled; return this; }
            public Builder maxConnections(int max) { this.maxConnections = max; return this; }
            public Builder allowOrigin(String origin) { this.allowedOrigins.add(origin); return this; }

            public HttpServerConfig build() {
                if (port <= 0 || port > 65535) {
                    throw new IllegalArgumentException("Port must be in (0, 65535]: " + port);
                }
                if (maxConnections <= 0) {
                    throw new IllegalArgumentException("maxConnections must be positive: " + maxConnections);
                }
                if (tlsEnabled && allowedOrigins.stream().anyMatch(o -> o.startsWith("http://"))) {
                    throw new IllegalArgumentException("Insecure origin under TLS: " +
                            allowedOrigins.stream().filter(o -> o.startsWith("http://")).findFirst().orElse("?"));
                }
                return new HttpServerConfig(this);
            }
        }
    }

    // ============================================================================
    // SECTION 3: FACTORY METHOD
    // ============================================================================

    public sealed interface Shape permits Circle, Rectangle {}
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

    public static class ShapeFactory {
        public static Shape create(String spec) {
            String[] parts = spec.split(":");
            return switch (parts[0].toLowerCase()) {
                case "circle" -> new Circle(Double.parseDouble(parts[1]));
                case "square" -> new Rectangle(Double.parseDouble(parts[1]), Double.parseDouble(parts[1]));
                case "rect" -> new Rectangle(Double.parseDouble(parts[1]), Double.parseDouble(parts[2]));
                default -> throw new IllegalArgumentException("Unknown shape spec: " + spec);
            };
        }
    }

    // ============================================================================
    // SECTION 4: STRATEGY
    // ============================================================================

    public record OrderLine(String product, double price, int quantity) {}

    public static class Order {
        private final List<OrderLine> lines = new ArrayList<>();
        private DoubleBinaryOperator pricingStrategy;

        public Order withStrategy(DoubleBinaryOperator strategy) {
            this.pricingStrategy = strategy;
            return this;
        }

        public Order addLine(String product, double price, int qty) {
            lines.add(new OrderLine(product, price, qty));
            return this;
        }

        public double total() {
            DoubleBinaryOperator strategy = pricingStrategy != null
                    ? pricingStrategy
                    : (subtotal, fee) -> subtotal + fee;
            double subtotal = lines.stream().mapToDouble(l -> l.price() * l.quantity()).sum();
            double fee = lines.size() > 5 ? 10.0 : 0.0; // handling fee for large orders
            return strategy.applyAsDouble(subtotal, fee);
        }

        public double subtotal() {
            return lines.stream().mapToDouble(l -> l.price() * l.quantity()).sum();
        }
    }

    // ============================================================================
    // SECTION 5: OBSERVER
    // ============================================================================

    public static class EventBus<T> {
        public interface Listener<E> {
            void onEvent(E event);
        }

        private final List<Listener<T>> listeners = new ArrayList<>();

        public void subscribe(Listener<T> listener) {
            listeners.add(listener);
        }

        public boolean unsubscribe(Listener<T> listener) {
            return listeners.remove(listener);
        }

        public int listenerCount() {
            return listeners.size();
        }

        public void publish(T event) {
            for (Listener<T> listener : List.copyOf(listeners)) {
                listener.onEvent(event);
            }
        }
    }

    // ============================================================================
    // SECTION 6: DECORATOR
    // ============================================================================

    public interface Coffee {
        String description();
        double cost();
    }

    public static class Espresso implements Coffee {
        @Override public String description() { return "Espresso"; }
        @Override public double cost() { return 2.0; }
    }

    public static abstract class CoffeeDecorator implements Coffee {
        protected final Coffee wrapped;
        protected CoffeeDecorator(Coffee wrapped) { this.wrapped = wrapped; }
    }

    public static class Milk extends CoffeeDecorator {
        public Milk(Coffee wrapped) { super(wrapped); }
        @Override public String description() { return wrapped.description() + " + milk"; }
        @Override public double cost() { return wrapped.cost() + 0.5; }
    }

    public static class Caramel extends CoffeeDecorator {
        public Caramel(Coffee wrapped) { super(wrapped); }
        @Override public String description() { return wrapped.description() + " + caramel"; }
        @Override public double cost() { return wrapped.cost() + 0.75; }
    }

    // ============================================================================
    // SECTION 7: TEMPLATE METHOD
    // ============================================================================

    public abstract static class DataPipeline {
        /** Template method: fixed skeleton, varying steps. */
        public final List<String> run(List<String> raw) {
            List<String> extracted = extract(raw);
            List<String> transformed = extracted.stream().map(this::transform).toList();
            List<String> loaded = new ArrayList<>();
            for (String item : transformed) {
                if (filter(item)) loaded.add(item);
            }
            return loaded;
        }

        protected abstract List<String> extract(List<String> raw);
        protected abstract String transform(String item);
        protected boolean filter(String item) { return !item.isBlank(); }
    }

    public static class CsvPipeline extends DataPipeline {
        @Override protected List<String> extract(List<String> raw) {
            return raw.stream().flatMap(l -> java.util.Arrays.stream(l.split(","))).toList();
        }
        @Override protected String transform(String item) { return item.trim().toUpperCase(); }
    }

    public static class JsonPipeline extends DataPipeline {
        @Override protected List<String> extract(List<String> raw) {
            return raw.stream().map(s -> s.replace("{", "").replace("}", "").replace("\"", "")).toList();
        }
        @Override protected String transform(String item) { return item.trim(); }
        @Override protected boolean filter(String item) { return item.contains(":"); }
    }

    // ============================================================================
    // SECTION 8: ADAPTER
    // ============================================================================

    /** Legacy third-party API we cannot change. */
    public static class LegacyPaymentGateway {
        public String makePayment(double amountInDollars, String currency) {
            return "OK:" + currency + amountInDollars;
        }
    }

    /** Modern interface the rest of the codebase targets. */
    public interface PaymentProcessor {
        /** @param amountCents amount in cents */
        String pay(long amountCents, String currency);
    }

    public static class LegacyGatewayAdapter implements PaymentProcessor {
        private final LegacyPaymentGateway legacy;

        public LegacyGatewayAdapter(LegacyPaymentGateway legacy) {
            this.legacy = legacy;
        }

        @Override
        public String pay(long amountCents, String currency) {
            if (amountCents < 0) {
                throw new IllegalArgumentException("amountCents must be >= 0");
            }
            double dollars = amountCents / 100.0;
            return legacy.makePayment(dollars, currency);
        }
    }

    // ============================================================================
    // DEMO
    // ============================================================================

    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("ELITE DESIGN PATTERNS TRAINING");
        System.out.println("=".repeat(60));
        demonstrate();
        System.out.println("\nALL PATTERN DEMOS COMPLETED SUCCESSFULLY");
    }

    public static void demonstrate() {
        // Singleton
        System.out.println("\n### Singleton ###");
        System.out.println("  env=" + ConfigurationService.getInstance().get("env")
                + ", holder=" + (ConfigurationService.HolderSingleton.getInstance() != null));

        // Builder
        System.out.println("\n### Builder ###");
        HttpServerConfig config = HttpServerConfig.builder()
                .host("api.example.com").port(8443).tls(true).maxConnections(500)
                .allowOrigin("https://app.example.com").build();
        System.out.println("  " + config.getHost() + ":" + config.getPort() + " tls=" + config.isTlsEnabled());

        // Factory + sealed shapes
        System.out.println("\n### Factory Method ###");
        Shape circle = ShapeFactory.create("circle:2.5");
        Shape square = ShapeFactory.create("square:4");
        System.out.println("  " + circle + " | " + square);

        // Strategy
        System.out.println("\n### Strategy ###");
        Order order = new Order().addLine("book", 12.0, 2).addLine("pen", 1.5, 4);
        System.out.printf("  default total=%.2f, discount-10%% total=%.2f%n",
                order.total(), order.withStrategy((sub, fee) -> (sub + fee) * 0.9).total());

        // Observer
        System.out.println("\n### Observer ###");
        EventBus<String> bus = new EventBus<>();
        bus.subscribe(e -> System.out.println("  [A] " + e));
        bus.subscribe(e -> System.out.println("  [B] " + e.toUpperCase()));
        bus.publish("deploy");

        // Decorator
        System.out.println("\n### Decorator ###");
        Coffee coffee = new Caramel(new Milk(new Espresso()));
        System.out.printf("  %s = $%.2f%n", coffee.description(), coffee.cost());

        // Template Method
        System.out.println("\n### Template Method ###");
        System.out.println("  csv: " + new CsvPipeline().run(List.of("alice, bob", " carol")));
        System.out.println("  json: " + new JsonPipeline().run(List.of("{\"name\":\"dan\"}", "x")));

        // Adapter
        System.out.println("\n### Adapter ###");
        PaymentProcessor processor = new LegacyGatewayAdapter(new LegacyPaymentGateway());
        System.out.println("  " + processor.pay(1999, "USD"));
    }
}
