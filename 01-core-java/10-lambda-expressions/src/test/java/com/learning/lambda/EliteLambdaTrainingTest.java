package com.learning.lambda;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Elite Lambda Expressions & Functional Programming Tests")
class EliteLambdaTrainingTest {

    @Nested
    @DisplayName("1. Custom Functional Interfaces & Exception Handling")
    class ExceptionHandlingAndCustomSamTests {

        @Test
        @DisplayName("TriFunction applies arguments and composes with andThen")
        void testTriFunction() {
            EliteLambdaTraining.TriFunction<String, Integer, Double, String> formatter =
                    (s, i, d) -> String.format("%s-%d-%.1f", s, i, d);

            String result = formatter.apply("Item", 42, 3.14);
            assertThat(result).isEqualTo("Item-42-3.1");

            var composed = formatter.andThen(String::toUpperCase);
            assertThat(composed.apply("item", 1, 2.0)).isEqualTo("ITEM-1-2.0");
        }

        @Test
        @DisplayName("uncheck wraps checked exceptions into RuntimeException")
        void testUncheckThrows() {
            EliteLambdaTraining.CheckedFunction<String, Integer, IOException> parser = s -> {
                if ("bad".equals(s)) {
                    throw new IOException("Simulated disk error");
                }
                return Integer.parseInt(s);
            };

            Function<String, Integer> safeParser = EliteLambdaTraining.uncheck(parser);

            assertThat(safeParser.apply("123")).isEqualTo(123);
            assertThatThrownBy(() -> safeParser.apply("bad"))
                    .isInstanceOf(RuntimeException.class)
                    .hasCauseInstanceOf(IOException.class);
        }

        @Test
        @DisplayName("liftOptional returns Optional.of on success and Optional.empty on exception")
        void testLiftOptional() {
            EliteLambdaTraining.CheckedFunction<String, Integer, Exception> risky = Integer::parseInt;
            var optionalParser = EliteLambdaTraining.liftOptional(risky);

            assertThat(optionalParser.apply("42")).contains(42);
            assertThat(optionalParser.apply("not_a_number")).isEmpty();
        }

        @Test
        @DisplayName("liftResult captures either success value or failure throwable")
        void testLiftResult() {
            EliteLambdaTraining.CheckedFunction<String, Integer, Exception> risky = Integer::parseInt;
            var resultParser = EliteLambdaTraining.liftResult(risky);

            var success = resultParser.apply("100");
            assertThat(success.isSuccess()).isTrue();
            assertThat(success.getValue()).isEqualTo(100);
            assertThat(success.map(v -> v * 2).getValue()).isEqualTo(200);

            // flatMap chained validation
            var chained = success.flatMap(v -> v > 50 ? EliteLambdaTraining.Result.success("Greater") : EliteLambdaTraining.Result.failure(new IllegalArgumentException("Too low")));
            assertThat(chained.getValue()).isEqualTo("Greater");

            var failure = resultParser.apply("invalid");
            assertThat(failure.isSuccess()).isFalse();
            assertThat(failure.getError()).isInstanceOf(NumberFormatException.class);
            assertThat(failure.orElse(0)).isEqualTo(0);
        }
    }

    @Nested
    @DisplayName("2. Currying and Partial Application")
    class CurryingTests {

        @Test
        @DisplayName("Currying converts BiFunction into chain of single-arg functions")
        void testCurryBiFunction() {
            var curriedAdd = EliteLambdaTraining.curry((Integer a, Integer b) -> a + b);
            var addFive = curriedAdd.apply(5);

            assertThat(addFive.apply(10)).isEqualTo(15);
            assertThat(addFive.apply(25)).isEqualTo(30);
        }

        @Test
        @DisplayName("Currying converts TriFunction into 3-level function chain")
        void testCurryTriFunction() {
            var curriedVolume = EliteLambdaTraining.curry((Integer w, Integer h, Integer d) -> w * h * d);
            int volume = curriedVolume.apply(2).apply(3).apply(4);
            assertThat(volume).isEqualTo(24);
        }

        @Test
        @DisplayName("Partial application fixes the first argument")
        void testPartialApplication() {
            var discount = EliteLambdaTraining.partial((Double rate, Double price) -> price * (1.0 - rate), 0.20);
            assertThat(discount.apply(100.0)).isEqualTo(80.0);
            assertThat(discount.apply(50.0)).isEqualTo(40.0);
        }
    }

    @Nested
    @DisplayName("3. Higher-Order Decorators")
    class DecoratorTests {

        @Test
        @DisplayName("Memoize caches results and computes only once per input")
        void testMemoization() {
            AtomicInteger callCount = new AtomicInteger();
            Function<String, Integer> lengthCalculator = s -> {
                callCount.incrementAndGet();
                return s.length();
            };

            var memoized = EliteLambdaTraining.memoize(lengthCalculator);

            assertThat(memoized.apply("hello")).isEqualTo(5);
            assertThat(memoized.apply("hello")).isEqualTo(5);
            assertThat(memoized.apply("world")).isEqualTo(5);

            assertThat(callCount.get()).isEqualTo(2); // "hello" and "world" once each
        }

        @Test
        @DisplayName("withRetry retries until success or maxAttempts exhausted")
        void testWithRetry() {
            AtomicInteger attempts = new AtomicInteger();
            String result = EliteLambdaTraining.withRetry(() -> {
                if (attempts.incrementAndGet() < 3) {
                    throw new IllegalStateException("Not ready yet");
                }
                return "Ready";
            }, 3);

            assertThat(result).isEqualTo("Ready");
            assertThat(attempts.get()).isEqualTo(3);

            // Exhaustion case
            assertThatThrownBy(() -> EliteLambdaTraining.withRetry(() -> {
                throw new RuntimeException("Permanent error");
            }, 2))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("All 2 attempts failed");
        }

        @Test
        @DisplayName("withTiming records elapsed nanoseconds and returns correct result")
        void testWithTiming() {
            var timedFn = EliteLambdaTraining.withTiming((Integer x) -> x * x);
            var record = timedFn.apply(5);

            assertThat(record.result()).isEqualTo(25);
            assertThat(record.elapsedNanos()).isGreaterThanOrEqualTo(0);
        }
    }

    @Nested
    @DisplayName("4. Functional Pipeline Pattern")
    class PipelineTests {

        @Test
        @DisplayName("Pipeline executes stages sequentially")
        void testPipelineExecution() {
            var pipeline = EliteLambdaTraining.Pipeline.<String>create()
                    .addStage(String::trim)
                    .addStage(String::toLowerCase)
                    .addStage(s -> "[" + s + "]");

            String result = pipeline.execute("   Hello World   ");
            assertThat(result).isEqualTo("[hello world]");
            assertThat(pipeline.stageCount()).isEqualTo(3);
        }
    }

    @Nested
    @DisplayName("5. Combinator-based Validator Pattern")
    class ValidatorTests {

        record UserDto(String username, int age, String email) {}

        @Test
        @DisplayName("ValidationRule combinator detects violations accurately")
        void testValidator() {
            var usernameRule = EliteLambdaTraining.<UserDto>rule(
                    u -> u.username() != null && u.username().length() >= 3,
                    "Username must be at least 3 chars"
            );
            var ageRule = EliteLambdaTraining.<UserDto>rule(
                    u -> u.age() >= 18,
                    "Must be an adult"
            );
            var emailRule = EliteLambdaTraining.<UserDto>rule(
                    u -> u.email() != null && u.email().contains("@"),
                    "Valid email is required"
            );

            UserDto validUser = new UserDto("alice", 25, "alice@example.com");
            List<String> validErrors = EliteLambdaTraining.validateAll(validUser, List.of(usernameRule, ageRule, emailRule));
            assertThat(validErrors).isEmpty();

            UserDto invalidUser = new UserDto("al", 16, "invalid-email");
            List<String> invalidErrors = EliteLambdaTraining.validateAll(invalidUser, List.of(usernameRule, ageRule, emailRule));
            assertThat(invalidErrors).hasSize(3)
                    .contains("Username must be at least 3 chars", "Must be an adult", "Valid email is required");

            // Short-circuiting rule combination with .and()
            var combined = usernameRule.and(ageRule);
            assertThat(combined.validate(invalidUser)).contains("Username must be at least 3 chars");
        }
    }

    @Nested
    @DisplayName("6. Trampoline Tail-Call Optimization Tests")
    class TrampolineTests {

        // Deep recursion without Trampoline would throw StackOverflowError for n = 50,000
        static EliteLambdaTraining.Trampoline<Long> sumRecursively(long n, long acc) {
            if (n <= 0) {
                return EliteLambdaTraining.Trampoline.done(acc);
            }
            return EliteLambdaTraining.Trampoline.more(() -> sumRecursively(n - 1, acc + n));
        }

        @Test
        @DisplayName("Trampoline computes 100,000 deep recursion in O(1) stack space without StackOverflowError")
        void testDeepRecursionStackSafety() {
            long n = 100_000L;
            long expected = n * (n + 1) / 2;

            long result = sumRecursively(n, 0L).run();
            assertThat(result).isEqualTo(expected);
        }
    }

    @Nested
    @DisplayName("7. Reader Monad Functional Dependency Injection Tests")
    class ReaderMonadTests {

        record Environment(String dbUrl, int timeoutSec) {}

        @Test
        @DisplayName("Reader injects context through functional composition")
        void testReaderDependencyInjection() {
            EliteLambdaTraining.Reader<Environment, String> getDb = env -> env.dbUrl();
            EliteLambdaTraining.Reader<Environment, Integer> getTimeout = env -> env.timeoutSec();

            EliteLambdaTraining.Reader<Environment, String> configReader = getDb.flatMap(
                    db -> getTimeout.map(to -> String.format("Connecting to %s with timeout=%ds", db, to))
            );

            Environment env = new Environment("jdbc:postgresql://prod-db:5432/app", 30);
            String message = configReader.run(env);

            assertThat(message).isEqualTo("Connecting to jdbc:postgresql://prod-db:5432/app with timeout=30s");
        }
    }

    @Nested
    @DisplayName("8. Functional Circuit Breaker Tests")
    class CircuitBreakerTests {

        @Test
        @DisplayName("Circuit transitions from CLOSED to OPEN after failure threshold and fails fast")
        void testCircuitBreakerTripsAndRecovers() throws InterruptedException {
            EliteLambdaTraining.CircuitBreaker breaker = new EliteLambdaTraining.CircuitBreaker(2, 50); // 50ms reset timeout

            assertThat(breaker.getState()).isEqualTo(EliteLambdaTraining.CircuitBreaker.State.CLOSED);

            var failingAction = breaker.decorate(() -> {
                throw new RuntimeException("Service outage");
            });

            // 1st failure
            var res1 = failingAction.get();
            assertThat(res1.isSuccess()).isFalse();
            assertThat(breaker.getState()).isEqualTo(EliteLambdaTraining.CircuitBreaker.State.CLOSED);

            // 2nd failure -> trips circuit to OPEN
            var res2 = failingAction.get();
            assertThat(res2.isSuccess()).isFalse();
            assertThat(breaker.getState()).isEqualTo(EliteLambdaTraining.CircuitBreaker.State.OPEN);

            // Fast failure without calling downstream
            var fastFail = failingAction.get();
            assertThat(fastFail.isSuccess()).isFalse();
            assertThat(fastFail.getError().getMessage()).contains("Circuit breaker is OPEN");

            // Wait for reset timeout to reach HALF_OPEN
            Thread.sleep(60);
            assertThat(breaker.getState()).isEqualTo(EliteLambdaTraining.CircuitBreaker.State.HALF_OPEN);

            // Success restores circuit to CLOSED
            var recoveryAction = breaker.decorate(() -> "Recovered");
            var recoveredRes = recoveryAction.get();
            assertThat(recoveredRes.isSuccess()).isTrue();
            assertThat(recoveredRes.getValue()).isEqualTo("Recovered");
            assertThat(breaker.getState()).isEqualTo(EliteLambdaTraining.CircuitBreaker.State.CLOSED);
        }
    }
}
