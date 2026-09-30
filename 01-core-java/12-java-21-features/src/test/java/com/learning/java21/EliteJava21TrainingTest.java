package com.learning.java21;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Elite Java 21 Features Training Tests")
class EliteJava21TrainingTest {

    // ============================================================================
    // RECORDS
    // ============================================================================

    @Nested
    @DisplayName("Record Tests")
    class RecordTests {

        @Test
        @DisplayName("Money compact constructor should normalize currency")
        void moneyNormalizesCurrency() {
            EliteJava21Training.Money money = new EliteJava21Training.Money(1000, "eur");
            assertThat(money.currency()).isEqualTo("EUR");
        }

        @Test
        @DisplayName("Money should default null currency to USD")
        void moneyDefaultsNullCurrency() {
            EliteJava21Training.Money money = new EliteJava21Training.Money(1000, null);
            assertThat(money.currency()).isEqualTo("USD");
        }

        @Test
        @DisplayName("Money should reject negative amounts")
        void moneyRejectsNegative() {
            assertThatThrownBy(() -> new EliteJava21Training.Money(-1, "USD"))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining(">= 0");
        }

        @Test
        @DisplayName("Money.plus should add same-currency amounts and reject mixing")
        void moneyPlus() {
            EliteJava21Training.Money a = EliteJava21Training.Money.ofDollars(19.99, "USD");
            EliteJava21Training.Money b = EliteJava21Training.Money.ofDollars(1.65, "USD");
            assertThat(a.plus(b).asDouble()).isEqualTo(21.64);

            EliteJava21Training.Money eur = EliteJava21Training.Money.ofDollars(1.0, "EUR");
            assertThatThrownBy(() -> a.plus(eur))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Currency mismatch");
        }

        @Test
        @DisplayName("ofDollars should round correctly to cents")
        void ofDollarsRounds() {
            assertThat(EliteJava21Training.Money.ofDollars(0.1, "USD").amountCents()).isEqualTo(10);
            assertThat(EliteJava21Training.Money.ofDollars(19.999, "USD").amountCents()).isEqualTo(2000);
        }

        @Test
        @DisplayName("Range should reject inverted bounds and expose contains")
        void rangeInvariants() {
            assertThatThrownBy(() -> new EliteJava21Training.Range(5, 1))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("low > high");

            EliteJava21Training.Range range = EliteJava21Training.Range.parse("1..5");
            assertThat(range.contains(1)).isTrue();
            assertThat(range.contains(5)).isTrue();
            assertThat(range.contains(0)).isFalse();
            assertThat(range.contains(6)).isFalse();
        }

        @Test
        @DisplayName("Records should have value-based equals and readable toString")
        void recordSemantics() {
            EliteJava21Training.Money a = new EliteJava21Training.Money(100, "USD");
            EliteJava21Training.Money b = new EliteJava21Training.Money(100, "USD");
            assertThat(a).isEqualTo(b).hasSameHashCodeAs(b);
            assertThat(a).hasToString("Money[amountCents=100, currency=USD]");
        }
    }

    // ============================================================================
    // SEALED SHAPES
    // ============================================================================

    @Nested
    @DisplayName("Sealed Shape Tests")
    class ShapeTests {

        @Test
        @DisplayName("area should compute all shape variants via record patterns")
        void areaComputesAllVariants() {
            assertThat(EliteJava21Training.area(new EliteJava21Training.Circle(2)))
                    .isCloseTo(Math.PI * 4, within(1e-9));
            assertThat(EliteJava21Training.area(new EliteJava21Training.Rectangle(3, 4)))
                    .isEqualTo(12.0);
            assertThat(EliteJava21Training.area(new EliteJava21Training.Triangle(6, 2)))
                    .isEqualTo(6.0);
        }

        @Test
        @DisplayName("Shapes should reject non-positive dimensions")
        void shapesRejectBadInput() {
            assertThatThrownBy(() -> new EliteJava21Training.Circle(0))
                    .isInstanceOf(IllegalArgumentException.class);
            assertThatThrownBy(() -> new EliteJava21Training.Rectangle(-1, 4))
                    .isInstanceOf(IllegalArgumentException.class);
            assertThatThrownBy(() -> new EliteJava21Training.Triangle(3, 0))
                    .isInstanceOf(IllegalArgumentException.class);
        }
    }

    // ============================================================================
    // PATTERN MATCHING FOR SWITCH
    // ============================================================================

    @Nested
    @DisplayName("Pattern Matching Tests")
    class PatternMatchingTests {

        @Test
        @DisplayName("describeEvent should match every event variant")
        void describeEveryVariant() {
            assertThat(EliteJava21Training.describeEvent(new EliteJava21Training.UserCreated("u-42")))
                    .isEqualTo("user created: u-42");
            assertThat(EliteJava21Training.describeEvent(new EliteJava21Training.UserCreated("  ")))
                    .isEqualTo("user created with blank id");
            assertThat(EliteJava21Training.describeEvent(new EliteJava21Training.PaymentReceived("ord-7", 2500)))
                    .isEqualTo("payment 2500 cents for order ord-7");
            assertThat(EliteJava21Training.describeEvent(new EliteJava21Training.PaymentReceived("ord-8", -5)))
                    .isEqualTo("negative payment for ord-8");
            assertThat(EliteJava21Training.describeEvent(new EliteJava21Training.Heartbeat(20)))
                    .isEqualTo("milestone heartbeat #20");
            assertThat(EliteJava21Training.describeEvent(new EliteJava21Training.Heartbeat(21)))
                    .isEqualTo("heartbeat #21");
        }

        @Test
        @DisplayName("describeEvent should handle null explicitly")
        void handlesNull() {
            assertThat(EliteJava21Training.describeEvent(null)).isEqualTo("null event");
        }

        @Test
        @DisplayName("legacyTypeHandling should demonstrate instanceof patterns")
        void instanceofPatterns() {
            assertThat(EliteJava21Training.legacyTypeHandling("hello"))
                    .isEqualTo("long string: hello");
            assertThat(EliteJava21Training.legacyTypeHandling("hi"))
                    .isEqualTo("something else");
            assertThat(EliteJava21Training.legacyTypeHandling(List.of(1, 2, 3)))
                    .isEqualTo("non-empty list of 3");
            assertThat(EliteJava21Training.legacyTypeHandling(7))
                    .isEqualTo("integer 7");
            assertThat(EliteJava21Training.legacyTypeHandling(new Object()))
                    .isEqualTo("something else");
        }
    }

    // ============================================================================
    // VIRTUAL THREADS
    // ============================================================================

    @Nested
    @DisplayName("Virtual Thread Tests")
    class VirtualThreadTests {

        @Test
        @DisplayName("runConcurrentTasks should complete every submitted task")
        void completesAllTasks() throws Exception {
            assertThat(EliteJava21Training.VirtualThreadDemo.runConcurrentTasks(500))
                    .isEqualTo(500);
        }

        @Test
        @DisplayName("Virtual thread ids should be unique per task")
        void threadIdsUnique() throws Exception {
            List<Long> ids = EliteJava21Training.VirtualThreadDemo.collectThreadIds(100);
            assertThat(ids).hasSize(100);
            assertThat(ids.stream().distinct()).hasSize(100);
        }

        @Test
        @DisplayName("isVirtual should distinguish virtual from platform threads")
        void virtualFlagWorks() {
            Thread virtual = Thread.ofVirtual().unstarted(() -> {});
            Thread platform = Thread.ofPlatform().unstarted(() -> {});

            assertThat(EliteJava21Training.VirtualThreadDemo.isVirtual(virtual)).isTrue();
            assertThat(EliteJava21Training.VirtualThreadDemo.isVirtual(platform)).isFalse();
        }
    }

    // ============================================================================
    // TEXT BLOCKS & INTERPOLATION
    // ============================================================================

    @Nested
    @DisplayName("Text Block Tests")
    class TextBlockTests {

        @Test
        @DisplayName("jsonConfig should render name and port inside a text block")
        void jsonConfigRenders() {
            String json = EliteJava21Training.jsonConfig("payments", 8443);
            assertThat(json).contains("\"name\": \"payments\"");
            assertThat(json).contains("\"port\": 8443");
            assertThat(json).contains("\"features\"");
        }

        @Test
        @DisplayName("interpolate should substitute placeholders in order")
        void interpolateSubstitutes() {
            assertThat(EliteJava21Training.interpolate("Hello {}!", "World"))
                    .isEqualTo("Hello World!");
            assertThat(EliteJava21Training.interpolate("{} + {} = {}", 1, 2, 3))
                    .isEqualTo("1 + 2 = 3");
        }

        @Test
        @DisplayName("interpolate should validate placeholder/value counts")
        void interpolateValidates() {
            assertThatThrownBy(() -> EliteJava21Training.interpolate("{} {}", "only-one"))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Missing value");
            assertThatThrownBy(() -> EliteJava21Training.interpolate("no placeholders", "extra"))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Unused values");
        }
    }

    // ============================================================================
    // SEQUENCED COLLECTIONS
    // ============================================================================

    @Nested
    @DisplayName("Sequenced Collection Tests")
    class SequencedCollectionTests {

        @Test
        @DisplayName("reversedView should reflect source mutations (live view)")
        void reversedViewIsLive() {
            List<String> source = new ArrayList<>(List.of("a", "b", "c"));
            List<String> reversed = EliteJava21Training.reversedView(source);

            assertThat(reversed).containsExactly("c", "b", "a");

            source.add("d");
            assertThat(reversed).containsExactly("d", "c", "b", "a");
        }

        @Test
        @DisplayName("getFirst/getLast should expose both ends")
        void firstAndLast() {
            List<String> seq = new ArrayList<>(List.of("x", "y", "z"));
            assertThat(EliteJava21Training.firstOf(seq)).isEqualTo("x");
            assertThat(EliteJava21Training.lastOf(seq)).isEqualTo("z");
        }

        @Test
        @DisplayName("getFirst on empty sequence should throw")
        void firstOnEmptyThrows() {
            List<String> empty = new ArrayList<>();
            assertThatThrownBy(() -> EliteJava21Training.firstOf(empty))
                    .isInstanceOf(java.util.NoSuchElementException.class);
        }
    }

    // ============================================================================
    // DEMO SMOKE TEST
    // ============================================================================

    @Test
    @DisplayName("demonstrate() should run all Java 21 demos without throwing")
    void demoRunsCleanly() {
        assertThatCode(EliteJava21Training::demonstrate).doesNotThrowAnyException();
    }
}
