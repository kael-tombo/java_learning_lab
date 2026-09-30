package com.learning.patterns;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Elite Design Patterns Training Tests")
class EliteDesignPatternsTrainingTest {

    // ============================================================================
    // SINGLETON
    // ============================================================================

    @Nested
    @DisplayName("Singleton Tests")
    class SingletonTests {

        @Test
        @DisplayName("getInstance should always return the same instance")
        void shouldReturnSameInstance() {
            assertThat(EliteDesignPatternsTraining.ConfigurationService.getInstance())
                    .isSameAs(EliteDesignPatternsTraining.ConfigurationService.getInstance());
        }

        @Test
        @DisplayName("getInstance should be thread-safe under concurrent access")
        void shouldBeThreadSafe() throws Exception {
            int threads = 16;
            ExecutorService pool = Executors.newFixedThreadPool(threads);
            CountDownLatch start = new CountDownLatch(1);
            List<EliteDesignPatternsTraining.ConfigurationService> instances =
                    new java.util.concurrent.CopyOnWriteArrayList<>();

            for (int i = 0; i < threads; i++) {
                pool.submit(() -> {
                    start.await();
                    instances.add(EliteDesignPatternsTraining.ConfigurationService.getInstance());
                    return null;
                });
            }
            start.countDown();
            pool.shutdown();
            assertThat(pool.awaitTermination(10, TimeUnit.SECONDS)).isTrue();

            assertThat(instances).hasSize(threads);
            assertThat(instances.stream().distinct()).hasSize(1);
        }

        @Test
        @DisplayName("Holder idiom should be lazy and distinct from DCL instance")
        void holderIdiomWorks() {
            EliteDesignPatternsTraining.ConfigurationService dcl =
                    EliteDesignPatternsTraining.ConfigurationService.getInstance();
            EliteDesignPatternsTraining.ConfigurationService.HolderSingleton holder =
                    EliteDesignPatternsTraining.ConfigurationService.HolderSingleton.getInstance();

            assertThat(holder).isNotNull();
            assertThat(System.identityHashCode(holder))
                    .isNotEqualTo(System.identityHashCode(dcl));
        }
    }

    // ============================================================================
    // BUILDER
    // ============================================================================

    @Nested
    @DisplayName("Builder Tests")
    class BuilderTests {

        @Test
        @DisplayName("Should build a valid immutable config with defaults")
        void shouldBuildValidConfig() {
            EliteDesignPatternsTraining.HttpServerConfig config =
                    EliteDesignPatternsTraining.HttpServerConfig.builder().build();

            assertThat(config.getHost()).isEqualTo("localhost");
            assertThat(config.getPort()).isEqualTo(8080);
            assertThat(config.isTlsEnabled()).isFalse();
            assertThat(config.getMaxConnections()).isEqualTo(100);
            assertThat(config.getAllowedOrigins()).isEmpty();
        }

        @Test
        @DisplayName("Should reject invalid port at build time")
        void shouldRejectInvalidPort() {
            assertThatThrownBy(() -> EliteDesignPatternsTraining.HttpServerConfig.builder()
                    .port(70000).build())
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Port");
        }

        @Test
        @DisplayName("Should reject insecure origins when TLS enabled")
        void shouldRejectInsecureOriginUnderTls() {
            assertThatThrownBy(() -> EliteDesignPatternsTraining.HttpServerConfig.builder()
                    .tls(true)
                    .allowOrigin("http://legacy.example.com")
                    .build())
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Insecure origin");
        }

        @Test
        @DisplayName("Built config should be immutable (defensive copy)")
        void builtConfigShouldBeImmutable() {
            EliteDesignPatternsTraining.HttpServerConfig config =
                    EliteDesignPatternsTraining.HttpServerConfig.builder()
                            .allowOrigin("https://a.example.com")
                            .build();

            List<String> origins = config.getAllowedOrigins();
            assertThatThrownBy(() -> origins.add("https://evil.example.com"))
                    .isInstanceOf(UnsupportedOperationException.class);
        }
    }

    // ============================================================================
    // FACTORY METHOD + sealed shapes
    // ============================================================================

    @Nested
    @DisplayName("Factory Method Tests")
    class FactoryTests {

        @Test
        @DisplayName("Should create shapes from spec strings")
        void shouldCreateShapes() {
            assertThat(EliteDesignPatternsTraining.ShapeFactory.create("circle:3"))
                    .isInstanceOf(EliteDesignPatternsTraining.Circle.class);
            assertThat(EliteDesignPatternsTraining.ShapeFactory.create("square:5"))
                    .isEqualTo(new EliteDesignPatternsTraining.Rectangle(5, 5));
            assertThat(EliteDesignPatternsTraining.ShapeFactory.create("rect:2:7"))
                    .isEqualTo(new EliteDesignPatternsTraining.Rectangle(2, 7));
        }

        @Test
        @DisplayName("Should reject unknown specs and non-positive dimensions")
        void shouldRejectBadInput() {
            assertThatThrownBy(() -> EliteDesignPatternsTraining.ShapeFactory.create("hexagon:6"))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Unknown shape");
            assertThatThrownBy(() -> EliteDesignPatternsTraining.ShapeFactory.create("circle:-1"))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("radius");
        }

        @Test
        @DisplayName("Record accessors should expose shape data")
        void recordAccessorsWork() {
            EliteDesignPatternsTraining.Circle circle =
                    (EliteDesignPatternsTraining.Circle) EliteDesignPatternsTraining.ShapeFactory.create("circle:2.5");
            assertThat(circle.radius()).isEqualTo(2.5);
        }
    }

    // ============================================================================
    // STRATEGY
    // ============================================================================

    @Nested
    @DisplayName("Strategy Tests")
    class StrategyTests {

        @Test
        @DisplayName("Default strategy should be subtotal + fee")
        void defaultStrategy() {
            EliteDesignPatternsTraining.Order order = new EliteDesignPatternsTraining.Order()
                    .addLine("book", 10.0, 2);
            assertThat(order.total()).isEqualTo(20.0);
        }

        @Test
        @DisplayName("Handling fee should apply for orders with more than 5 lines")
        void handlingFeeApplies() {
            EliteDesignPatternsTraining.Order order = new EliteDesignPatternsTraining.Order();
            for (int i = 0; i < 6; i++) {
                order.addLine("item" + i, 1.0, 1);
            }
            assertThat(order.total()).isEqualTo(16.0); // 6 * 1.0 + 10 fee
        }

        @Test
        @DisplayName("Custom strategies should replace pricing without touching Order")
        void customStrategy() {
            EliteDesignPatternsTraining.Order order = new EliteDesignPatternsTraining.Order()
                    .addLine("book", 100.0, 1)
                    .withStrategy((subtotal, fee) -> subtotal * 0.5 + fee);
            assertThat(order.total()).isEqualTo(50.0);
        }
    }

    // ============================================================================
    // OBSERVER
    // ============================================================================

    @Nested
    @DisplayName("Observer Tests")
    class ObserverTests {

        @Test
        @DisplayName("All subscribers should receive published events")
        void allSubscribersReceiveEvents() {
            EliteDesignPatternsTraining.EventBus<String> bus = new EliteDesignPatternsTraining.EventBus<>();
            List<String> received = new ArrayList<>();
            bus.subscribe(received::add);

            bus.publish("one");
            bus.publish("two");

            assertThat(received).containsExactly("one", "two");
        }

        @Test
        @DisplayName("Unsubscribed listeners should not receive events")
        void unsubscribedListenerStopsReceiving() {
            EliteDesignPatternsTraining.EventBus<String> bus = new EliteDesignPatternsTraining.EventBus<>();
            List<String> received = new ArrayList<>();
            EliteDesignPatternsTraining.EventBus.Listener<String> listener = received::add;
            bus.subscribe(listener);
            bus.publish("a");
            assertThat(bus.unsubscribe(listener)).isTrue();
            bus.publish("b");

            assertThat(received).containsExactly("a");
            assertThat(bus.listenerCount()).isZero();
        }

        @Test
        @DisplayName("Subscriber throwing should be visible, not silently swallowed")
        void subscriberFailureIsObservable() {
            EliteDesignPatternsTraining.EventBus<String> bus = new EliteDesignPatternsTraining.EventBus<>();
            bus.subscribe(e -> { throw new IllegalStateException("boom"); });

            assertThatThrownBy(() -> bus.publish("x"))
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessageContaining("boom");
        }
    }

    // ============================================================================
    // DECORATOR
    // ============================================================================

    @Nested
    @DisplayName("Decorator Tests")
    class DecoratorTests {

        @Test
        @DisplayName("Decorators should stack costs and descriptions")
        void decoratorsStack() {
            EliteDesignPatternsTraining.Coffee coffee =
                    new EliteDesignPatternsTraining.Caramel(
                            new EliteDesignPatternsTraining.Milk(
                                    new EliteDesignPatternsTraining.Espresso()));

            assertThat(coffee.description()).isEqualTo("Espresso + milk + caramel");
            assertThat(coffee.cost()).isEqualTo(2.0 + 0.5 + 0.75);
        }

        @Test
        @DisplayName("Order of decoration should not change cost")
        void orderDoesNotChangeCost() {
            double a = new EliteDesignPatternsTraining.Caramel(
                    new EliteDesignPatternsTraining.Milk(new EliteDesignPatternsTraining.Espresso())).cost();
            double b = new EliteDesignPatternsTraining.Milk(
                    new EliteDesignPatternsTraining.Caramel(new EliteDesignPatternsTraining.Espresso())).cost();
            assertThat(a).isEqualTo(b);
        }

        @Test
        @DisplayName("Base coffee should be unaffected by decorators")
        void baseCoffeeUnaffected() {
            EliteDesignPatternsTraining.Coffee espresso = new EliteDesignPatternsTraining.Espresso();
            assertThat(espresso.cost()).isEqualTo(2.0);
        }
    }

    // ============================================================================
    // TEMPLATE METHOD
    // ============================================================================

    @Nested
    @DisplayName("Template Method Tests")
    class TemplateMethodTests {

        @Test
        @DisplayName("CSV pipeline should split, trim, and uppercase")
        void csvPipeline() {
            List<String> out = new EliteDesignPatternsTraining.CsvPipeline()
                    .run(List.of("alice, bob", " carol"));
            assertThat(out).containsExactly("ALICE", "BOB", "CAROL");
        }

        @Test
        @DisplayName("JSON pipeline should strip braces and keep only key-value lines")
        void jsonPipeline() {
            List<String> out = new EliteDesignPatternsTraining.JsonPipeline()
                    .run(List.of("{\"name\":\"dan\"}", "plain line"));
            assertThat(out).containsExactly("name:dan");
        }

        @Test
        @DisplayName("Pipelines should filter blank entries via default hook")
        void blankEntriesFiltered() {
            List<String> out = new EliteDesignPatternsTraining.CsvPipeline().run(List.of("a,,b"));
            assertThat(out).containsExactly("A", "B");
        }
    }

    // ============================================================================
    // ADAPTER
    // ============================================================================

    @Nested
    @DisplayName("Adapter Tests")
    class AdapterTests {

        @Test
        @DisplayName("Adapter should translate cents to legacy dollar API")
        void shouldTranslateCentsToDollars() {
            EliteDesignPatternsTraining.PaymentProcessor processor =
                    new EliteDesignPatternsTraining.LegacyGatewayAdapter(
                            new EliteDesignPatternsTraining.LegacyPaymentGateway());

            assertThat(processor.pay(1999, "USD")).isEqualTo("OK:USD19.99");
            assertThat(processor.pay(100, "EUR")).isEqualTo("OK:EUR1.0");
        }

        @Test
        @DisplayName("Adapter should reject negative amounts")
        void shouldRejectNegativeAmounts() {
            EliteDesignPatternsTraining.PaymentProcessor processor =
                    new EliteDesignPatternsTraining.LegacyGatewayAdapter(
                            new EliteDesignPatternsTraining.LegacyPaymentGateway());

            assertThatThrownBy(() -> processor.pay(-5, "USD"))
                    .isInstanceOf(IllegalArgumentException.class);
        }
    }

    // ============================================================================
    // DEMO SMOKE TEST
    // ============================================================================

    @Test
    @DisplayName("demonstrate() should run all pattern demos without throwing")
    void demoRunsCleanly() {
        assertThatCode(EliteDesignPatternsTraining::demonstrate).doesNotThrowAnyException();
    }
}
