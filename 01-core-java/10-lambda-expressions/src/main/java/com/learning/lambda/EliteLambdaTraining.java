package com.learning.lambda;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.*;
import java.util.stream.Stream;

/**
 * Elite Lambda Expressions & Functional Programming Training
 *
 * This module demonstrates production-grade functional programming patterns in Java:
 * - Advanced Functional Interfaces & TriFunction
 * - Exception Wrapping in Lambdas (Checked Functions, Either/Result monad pattern)
 * - Currying and Partial Application
 * - Higher-Order Functions (Memoization, Retry Decorator, Execution Timer)
 * - Fluent Functional Pipeline & Middleware Pattern
 * - Combinator-based Validator Pattern
 * - Tail-Call Optimization via Trampoline (Stack-safe recursion)
 * - Functional Dependency Injection via Reader Monad
 * - Functional Circuit Breaker Pattern
 */
public class EliteLambdaTraining {

    // ============================================================================
    // SECTION 1: CUSTOM FUNCTIONAL INTERFACES & EXCEPTION HANDLING
    // ============================================================================

    @FunctionalInterface
    public interface TriFunction<T, U, V, R> {
        R apply(T t, U u, V v);

        default <W> TriFunction<T, U, V, W> andThen(Function<? super R, ? extends W> after) {
            Objects.requireNonNull(after);
            return (t, u, v) -> after.apply(apply(t, u, v));
        }
    }

    @FunctionalInterface
    public interface CheckedFunction<T, R, E extends Throwable> {
        R apply(T t) throws E;
    }

    @FunctionalInterface
    public interface CheckedSupplier<T, E extends Throwable> {
        T get() throws E;
    }

    /**
     * Converts a checked function into a standard Function by wrapping checked exceptions
     * in an unchecked RuntimeException.
     */
    public static <T, R> Function<T, R> uncheck(CheckedFunction<T, R, ?> checkedFunction) {
        return t -> {
            try {
                return checkedFunction.apply(t);
            } catch (RuntimeException | Error e) {
                throw e;
            } catch (Throwable ex) {
                throw new RuntimeException("Checked exception wrapped in uncheck", ex);
            }
        };
    }

    /**
     * Converts a function throwing exceptions into one returning an Optional (empty on failure).
     */
    public static <T, R> Function<T, Optional<R>> liftOptional(CheckedFunction<T, R, ?> fn) {
        return t -> {
            try {
                return Optional.ofNullable(fn.apply(t));
            } catch (Throwable ex) {
                return Optional.empty();
            }
        };
    }

    // Result/Either container for functional error handling
    public static final class Result<T> {
        private final T value;
        private final Throwable error;

        private Result(T value, Throwable error) {
            this.value = value;
            this.error = error;
        }

        public static <T> Result<T> success(T value) {
            return new Result<>(value, null);
        }

        public static <T> Result<T> failure(Throwable error) {
            return new Result<>(null, Objects.requireNonNull(error));
        }

        public boolean isSuccess() {
            return error == null;
        }

        public T getValue() {
            if (!isSuccess()) {
                throw new NoSuchElementException("Result is a failure: " + error.getMessage());
            }
            return value;
        }

        public Throwable getError() {
            return error;
        }

        public <U> Result<U> map(Function<? super T, ? extends U> mapper) {
            if (!isSuccess()) {
                return Result.failure(error);
            }
            try {
                return Result.success(mapper.apply(value));
            } catch (Throwable ex) {
                return Result.failure(ex);
            }
        }

        public <U> Result<U> flatMap(Function<? super T, Result<U>> mapper) {
            if (!isSuccess()) {
                return Result.failure(error);
            }
            try {
                return Objects.requireNonNull(mapper.apply(value));
            } catch (Throwable ex) {
                return Result.failure(ex);
            }
        }

        public T orElse(T fallback) {
            return isSuccess() ? value : fallback;
        }
    }

    public static <T, R> Function<T, Result<R>> liftResult(CheckedFunction<T, R, ?> fn) {
        return t -> {
            try {
                return Result.success(fn.apply(t));
            } catch (Throwable ex) {
                return Result.failure(ex);
            }
        };
    }

    // ============================================================================
    // SECTION 2: CURRYING & PARTIAL APPLICATION
    // ============================================================================

    /**
     * Curries a BiFunction into nested unary functions: (A, B) -> C becomes A -> (B -> C).
     */
    public static <A, B, C> Function<A, Function<B, C>> curry(BiFunction<A, B, C> biFunction) {
        return a -> b -> biFunction.apply(a, b);
    }

    /**
     * Curries a TriFunction into A -> (B -> (C -> D)).
     */
    public static <A, B, C, D> Function<A, Function<B, Function<C, D>>> curry(TriFunction<A, B, C, D> triFunction) {
        return a -> b -> c -> triFunction.apply(a, b, c);
    }

    /**
     * Partially applies the first argument of a BiFunction.
     */
    public static <A, B, C> Function<B, C> partial(BiFunction<A, B, C> biFunction, A fixedFirstArg) {
        return b -> biFunction.apply(fixedFirstArg, b);
    }

    // ============================================================================
    // SECTION 3: HIGHER-ORDER DECORATORS (MEMOIZATION, RETRY, TIMING)
    // ============================================================================

    /**
     * Thread-safe memoization decorator for deterministic functions.
     */
    public static <T, R> Function<T, R> memoize(Function<T, R> fn) {
        Map<T, R> cache = new ConcurrentHashMap<>();
        return key -> cache.computeIfAbsent(key, fn);
    }

    /**
     * Retries a supplier up to maxAttempts on failure.
     */
    public static <T> T withRetry(CheckedSupplier<T, ?> supplier, int maxAttempts) {
        if (maxAttempts < 1) {
            throw new IllegalArgumentException("maxAttempts must be >= 1");
        }
        Throwable lastError = null;
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                return supplier.get();
            } catch (Throwable t) {
                lastError = t;
            }
        }
        throw new RuntimeException("All " + maxAttempts + " attempts failed", lastError);
    }

    public record ExecutionRecord<R>(R result, long elapsedNanos) {}

    /**
     * Measures the execution time of a function in nanoseconds.
     */
    public static <T, R> Function<T, ExecutionRecord<R>> withTiming(Function<T, R> fn) {
        return arg -> {
            long start = System.nanoTime();
            R result = fn.apply(arg);
            long elapsed = System.nanoTime() - start;
            return new ExecutionRecord<>(result, elapsed);
        };
    }

    // ============================================================================
    // SECTION 4: FLUENT PIPELINE & MIDDLEWARE CHAIN
    // ============================================================================

    public static final class Pipeline<T> {
        private final List<UnaryOperator<T>> stages;

        private Pipeline(List<UnaryOperator<T>> stages) {
            this.stages = new ArrayList<>(stages);
        }

        public static <T> Pipeline<T> create() {
            return new Pipeline<>(Collections.emptyList());
        }

        public Pipeline<T> addStage(UnaryOperator<T> stage) {
            List<UnaryOperator<T>> next = new ArrayList<>(this.stages);
            next.add(Objects.requireNonNull(stage));
            return new Pipeline<>(next);
        }

        public T execute(T initial) {
            T current = initial;
            for (UnaryOperator<T> stage : stages) {
                current = stage.apply(current);
            }
            return current;
        }

        public int stageCount() {
            return stages.size();
        }
    }

    // ============================================================================
    // SECTION 5: COMBINATOR-BASED VALIDATOR PATTERN
    // ============================================================================

    @FunctionalInterface
    public interface ValidationRule<T> {
        Optional<String> validate(T target);

        default ValidationRule<T> and(ValidationRule<T> other) {
            return target -> {
                Optional<String> firstResult = this.validate(target);
                return firstResult.isPresent() ? firstResult : other.validate(target);
            };
        }
    }

    public static <T> ValidationRule<T> rule(Predicate<T> predicate, String errorMessage) {
        return target -> predicate.test(target) ? Optional.empty() : Optional.of(errorMessage);
    }

    public static <T> List<String> validateAll(T target, List<ValidationRule<T>> rules) {
        List<String> errors = new ArrayList<>();
        for (ValidationRule<T> rule : rules) {
            rule.validate(target).ifPresent(errors::add);
        }
        return Collections.unmodifiableList(errors);
    }

    // ============================================================================
    // SECTION 6: TRAMPOLINE FOR TAIL-CALL OPTIMIZATION (TCO)
    // ============================================================================

    /**
     * Trampoline enables stack-safe recursion in Java by deferring execution
     * into thunks executed iteratively in heap memory.
     */
    @FunctionalInterface
    public interface Trampoline<T> {
        Trampoline<T> bounce();

        default boolean isComplete() {
            return false;
        }

        default T result() {
            throw new UnsupportedOperationException("Computation not completed");
        }

        default T run() {
            Trampoline<T> current = this;
            while (!current.isComplete()) {
                current = current.bounce();
            }
            return current.result();
        }

        static <T> Trampoline<T> done(final T result) {
            return new Trampoline<>() {
                @Override
                public boolean isComplete() {
                    return true;
                }

                @Override
                public T result() {
                    return result;
                }

                @Override
                public Trampoline<T> bounce() {
                    throw new NoSuchElementException("Already completed");
                }
            };
        }

        static <T> Trampoline<T> more(final Supplier<Trampoline<T>> next) {
            return next::get;
        }
    }

    // ============================================================================
    // SECTION 7: READER MONAD (FUNCTIONAL DEPENDENCY INJECTION)
    // ============================================================================

    /**
     * Reader monad represents a computation that reads from an environment/context C
     * to produce a result of type A without global state or mutable context passing.
     */
    @FunctionalInterface
    public interface Reader<C, A> {
        A run(C context);

        default <B> Reader<C, B> map(Function<? super A, ? extends B> f) {
            return context -> f.apply(run(context));
        }

        default <B> Reader<C, B> flatMap(Function<? super A, Reader<C, B>> f) {
            return context -> f.apply(run(context)).run(context);
        }

        static <C, A> Reader<C, A> of(A value) {
            return context -> value;
        }

        static <C> Reader<C, C> ask() {
            return context -> context;
        }
    }

    // ============================================================================
    // SECTION 8: FUNCTIONAL CIRCUIT BREAKER
    // ============================================================================

    public static final class CircuitBreaker {
        public enum State { CLOSED, OPEN, HALF_OPEN }

        private final int failureThreshold;
        private final long resetTimeoutNanos;
        private final AtomicInteger failureCount = new AtomicInteger(0);
        private final AtomicLong lastStateChangeNanos = new AtomicLong(System.nanoTime());
        private volatile State state = State.CLOSED;

        public CircuitBreaker(int failureThreshold, long resetTimeoutMs) {
            this.failureThreshold = failureThreshold;
            this.resetTimeoutNanos = resetTimeoutMs * 1_000_000L;
        }

        public synchronized State getState() {
            if (state == State.OPEN && (System.nanoTime() - lastStateChangeNanos.get()) >= resetTimeoutNanos) {
                state = State.HALF_OPEN;
                lastStateChangeNanos.set(System.nanoTime());
            }
            return state;
        }

        public <T> Supplier<Result<T>> decorate(Supplier<T> supplier) {
            return () -> {
                State current = getState();
                if (current == State.OPEN) {
                    return Result.failure(new IllegalStateException("Circuit breaker is OPEN"));
                }
                try {
                    T value = supplier.get();
                    onSuccess();
                    return Result.success(value);
                } catch (Throwable t) {
                    onFailure();
                    return Result.failure(t);
                }
            };
        }

        private synchronized void onSuccess() {
            failureCount.set(0);
            if (state == State.HALF_OPEN) {
                state = State.CLOSED;
                lastStateChangeNanos.set(System.nanoTime());
            }
        }

        private synchronized void onFailure() {
            int count = failureCount.incrementAndGet();
            if (state == State.HALF_OPEN || count >= failureThreshold) {
                state = State.OPEN;
                lastStateChangeNanos.set(System.nanoTime());
            }
        }
    }
}
