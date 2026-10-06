# Lab 06: AI Pipeline Orchestration — Code Deep Dive

## 1. Project Structure

```
lab06/
  src/com/aiengineering/lab06/
    stage/Stage.java, StageResult.java, StageFailure.java
    stage/FailureClass.java
    stage/Policy.java               FAIL, SKIP, RETRY, DEGRADE
    exec/StageExecutor.java         bounded concurrency, queue limit, timeout
    exec/Pipeline.java              linear chain
    exec/DagPipeline.java           dependency graph, critical path
    exec/Saga.java                  side effects with compensation
    route/TypeRouter.java           type-driven dispatch
    cache/StageCache.java           (stage, inputHash, configHash)
    spec/PipelineSpec.java          stage versions + config hashes
    metrics/StageMetrics.java       per-stage latency/errors/hits
    metrics/Bottleneck.java         critical path + utilization
    test/Properties.java, GoldenTest.java
    Main.java
```

## 2. Stage Contract

```java
public interface Stage<I, O> {
    String name();
    String version();
    String configHash();

    StageResult<O> run(I input, StageContext ctx);

    /** Declarative contract: what to do on each failure class. */
    default Policy policy(FailureClass cls) {
        return switch (cls) {
            case TRANSIENT -> Policy.RETRY;
            case DATA -> Policy.DEGRADE;
            case POLICY, PERMANENT -> Policy.FAIL;
        };
    }
    default int maxAttempts()  { return policy(TRANSIENT) == RETRY ? 3 : 1; }
    default Duration timeout() { return Duration.ofSeconds(5); }
    default boolean idempotent() { return true; }
}

public record StageResult<T>(T value, Failure failure, boolean degraded) {
    public static <T> StageResult<T> ok(T v)          { return new StageResult<>(v, null, false); }
    public static <T> StageResult<T> degraded(T v)    { return new StageResult<>(v, null, true); }
    public static <T> StageResult<T> fail(Failure f)   { return new StageResult<>(null, f, false); }
}
```

The policy defaults encode a judgement: transient failures retry, data failures
degrade, permanent ones stop the chain. Putting these in the interface means a new stage
gets sensible behaviour without anyone remembering to configure it.

## 3. Typed Pipeline

```java
public final class Pipeline<I, O> {

    private final List<StageNode> nodes = new ArrayList<>();

    public <T> Pipeline<I, O> then(Stage<I, T> next, Class<T> outType) {
        nodes.add(new StageNode<>(next, outType));
        return cast();
    }

    public O execute(I input, StageContext ctx) {
        Object current = input;
        for (StageNode node : nodes) {
            if (!node.outType().isInstance(current))
                throw new PipelineException("stage %s expected %s but received %s"
                        .formatted(node.stage().name(), node.outType().getSimpleName(),
                                   current.getClass().getSimpleName()));
            StageResult<?> r = invokeWithPolicy(node.stage(), current, ctx);
            if (r.failure() != null && node.stage().policy(r.failure().cls()) == Policy.FAIL)
                throw new StageException(node.stage().name(), r.failure());
            current = r.value();
        }
        @SuppressWarnings("unchecked")
        O out = (O) current;
        return out;
    }
}
```

The runtime `isInstance` check is a belt-and-braces guard; the compile-time guarantee
comes from `then(Stage<I,T>, Class<T>)`. Together they make a mis-wire either a compile
error or an immediate, explicit exception.

## 4. Policy Application

```java
private StageResult<?> invokeWithPolicy(Stage<?, ?> stage, Object input, StageContext ctx) {
    StageResult<?> result = null;
    Failure last = null;

    for (int attempt = 1; attempt <= stage.maxAttempts(); attempt++) {
        try {
            result = stage.run(input, ctx);
            if (result.failure() == null) { ctx.metrics().record(stage, attempt); return result; }
            last = result.failure();
        } catch (StageTimeout e) {
            last = new Failure(FailureClass.TRANSIENT, "TIMEOUT", e.getMessage());
        }

        Policy p = stage.policy(last.cls());
        if (p == Policy.FAIL) return StageResult.fail(last);
        if (p == Policy.SKIP) return StageResult.ok(null);
        if (p == Policy.RETRY) {
            // non-idempotent side effects must NOT be silently retried
            if (!stage.idempotent() && !ctx.allowNonIdempotentRetry(stage.name())) {
                ctx.metrics().suppressedRetry(stage, last);
                return StageResult.fail(last);
            }
            sleep(backoffWithJitter(attempt, ctx.rng()));
        }
    }
    return stage.policy(last.cls()) == Policy.DEGRADE ? StageResult.degraded(null)
                                                      : StageResult.fail(last);
}
```

The non-idempotency guard is the substantive part. A stage that sends an email must not
be retried just because it declared `RETRY` for transient failures; doing so is how
duplicate side effects happen.

## 5. Bounded Executor

```java
public final class StageExecutor implements AutoCloseable {

    private final Semaphore slots;
    private final AtomicInteger queued = new AtomicInteger();
    private final int queueDepth;

    public <T> CompletableFuture<T> submit(Stage<?, ?> stage, Object input, StageContext ctx) {
        if (queued.get() >= queueDepth) {                       // explicit backpressure
            ctx.metrics().rejected(stage);
            return CompletableFuture.failedFuture(new OverloadedException(stage.name()));
        }
        queued.incrementAndGet();
        return CompletableFuture.supplyAsync(() -> {
            slots.acquireUninterruptibly();                     // bounded concurrency
            try {
                return runWithTimeout(stage, input, ctx);
            } finally {
                slots.release();
                queued.decrementAndGet();
            }
        }, pool);
    }

    private <T> T runWithTimeout(Stage<?, ?> stage, Object input, StageContext ctx) {
        var pool = dedicatedPool(stage.name(), stage.maxConcurrency());
        try {
            return pool.submit(() -> stage.run(input, ctx).value()).get(stage.timeout().toMillis(), MS);
        } catch (TimeoutException e) {
            pool.shutdownNow();                                 // do not wait for a stuck stage
            throw new StageTimeout(stage.name(), stage.timeout());
        } catch (ExecutionException e) { throw unwrap(e); }
        catch (InterruptedException e) { Thread.currentThread().interrupt(); throw new StageAborted(); }
    }
}
```

Two mechanisms, both necessary: a queue-depth check that **rejects explicitly** rather
than queueing without limit, and a dedicated per-stage pool so a stuck stage's threads
do not starve the rest of the pipeline.

## 6. Stage Cache

```java
public final class StageCache {

    /** configHash in the key makes downstream invalidation automatic. */
    public String key(Stage<?, ?> stage, Object input) {
        return stage.name() + "|" + stage.version() + "|" + stage.configHash()
             + "|" + sha256(canonicalize(input));
    }

    @SuppressWarnings("unchecked")
    public <T> T get(Stage<?, ?> stage, Object input, StageContext ctx) {
        if (!stage.idempotent() || stage.usesClock() || stage.usesRandomness())
            return null;                                        // never cache impure stages
        String k = key(stage, input);
        CacheEntry e = map.get(k);
        if (e == null || e.isExpired()) { ctx.metrics().cacheMiss(stage); return null; }
        hits.merge(stage.name(), 1L, Long::sum);
        return (T) e.value();
    }

    /** Bump configHash on a config change; every downstream entry stops matching. */
    public void invalidateDownstreamOf(String stageName) {
        map.keySet().removeIf(k -> k.startsWith(stageName + "|"));
    }
}
```

Refusing to cache stages that declare clock or randomness use is the guard that keeps a
cache from silently freezing non-deterministic behaviour into what looks like a stable
system.

## 7. Type-Driven Router

```java
public final class TypeRouter<I, O> {

    private final Map<Class<?>, Stage<I, O>> bindings = new LinkedHashMap<>();
    private final Stage<I, O> fallback;

    public <T> TypeRouter<I, O> bind(Class<T> inputType, Stage<I, O> stage) {
        bindings.put(inputType, stage);
        return this;
    }

    public StageResult<O> route(Object input, StageContext ctx) {
        // most specific type wins: walk the class hierarchy
        for (var e : bindings.entrySet())
            if (e.getKey().isInstance(input)) return invoke(e.getValue(), input, ctx);
        return fallback == null ? StageResult.fail(new Failure(UNSUPPORTED, "NO_STAGE", null))
                               : invoke(fallback, input, ctx);
    }
}
```

Adding a stage is a `bind` call. The failure mode of an `if/else` router — a new type
silently hitting a default branch — disappears.

## 8. DAG and Critical Path

```java
public record Node(String name, Duration duration, List<String> dependsOn) {}

public List<String> criticalPath(Collection<Node> nodes) {
    Map<String, Duration> finish = new HashMap<>();
    Map<String, String> prev = new HashMap<>();
    for (Node n : topologicalOrder(nodes)) {
        Duration earliest = Duration.ZERO;
        String from = null;
        for (String dep : n.dependsOn())
            if (finish.getOrDefault(dep, Duration.ZERO).compareTo(earliest) > 0) {
                earliest = finish.get(dep);
                from = dep;
            }
        finish.put(n.name(), earliest.plus(n.duration()));
        prev.put(n.name(), from);
    }
    // walk back from the latest-finishing node
    String end = finish.entrySet().stream().max(Map.Entry.comparingByValue()).map(Map.Entry::getKey).orElseThrow();
    LinkedList<String> path = new LinkedList<>();
    for (String c = end; c != null; c = prev.get(c)) path.addFirst(c);
    return path;
}
```

`criticalPath` is what stops the classic mistake of optimizing a parallel branch that
is not on the path and then observing no change.

## 9. Saga with Compensation

```java
public final class Saga {

    public record Step<T>(Stage<?, T> forward, Stage<?, T> compensate, String name) {}

    public <T> T execute(List<Step<?>> steps, Object input, StageContext ctx) {
        Deque<Runnable> undo = new ArrayDeque<>();
        Object current = input;
        try {
            for (Step<?> step : steps) {
                StageResult<?> r = step.forward().run(current, ctx);
                if (r.failure() != null) throw new StageException(step.name(), r.failure());
                undo.push(() -> step.compensate().run(current, ctx));  // LIFO
                current = r.value();
            }
            return (T) current;
        } catch (RuntimeException e) {
            while (!undo.isEmpty()) undo.pop().run();           // unwind in reverse
            ctx.metrics().compensated(steps.size());
            throw e;
        }
    }
}
```

The `Deque` gives LIFO compensation automatically, which is the required order when step
2's compensation must precede step 1's.

## 10. Pipeline Spec

```java
public record PipelineSpec(String schemaVersion, List<StageSpec> stages) {

    public record StageSpec(String name, String version, String configHash) {}

    /** Recorded with every result so a quality change is attributable. */
    public String hash() {
        String canonical = stages.stream()
                .map(s -> s.name() + "@" + s.version() + "#" + s.configHash())
                .sorted()                                   // order-independent
                .collect(joining(","));
        return sha256(schemaVersion + "|" + canonical);
    }

    public List<String> diff(PipelineSpec other) {
        Map<String, StageSpec> mine = byName(stages);
        List<String> changed = new ArrayList<>();
        for (StageSpec theirs : other.stages()) {
            StageSpec s = mine.get(theirs.name());
            if (s == null) changed.add("+" + theirs.name());
            else if (!s.version().equals(theirs.version()) || !s.configHash().equals(theirs.configHash()))
                changed.add("~" + theirs.name() + " (" + s.version() + " -> " + theirs.version() + ")");
        }
        for (StageSpec s : stages)
            if (other.byName().get(s.name()) == null) changed.add("-" + s.name());
        return changed;
    }
}
```

`diff` gives the first answer to "what changed": a single-stage list. Without it, a
quality regression sends people hunting through commit logs.

## 11. Stage Metrics and Bottleneck

```java
public record StageMetrics(String stage, long calls, long errors, long retries,
                           long cacheHits, long cacheMisses,
                           Histogram latency, long inputItems, long outputItems) {

    public double errorRate()   { return errors / (double) calls; }
    public double hitRate()     { return cacheHits / (double) (cacheHits + cacheMisses); }
    public double itemsPerMs()  { return inputItems / Math.max(1, latency.totalMs()); }
}

public record Bottleneck(List<String> criticalPath, Map<String, Double> utilization) {
    /** Report stages with high utilization AND on the critical path: those are the targets. */
    public List<String> targets() {
        return criticalPath.stream()
                .filter(s -> utilization.getOrDefault(s, 0.0) > 0.7)
                .toList();
    }
}
```

`targets()` intersects high utilization with the critical path, so the report points at
stages where optimization would actually help rather than at whatever is busy.

## 12. Golden and Property Tests

```java
public static void golden(GoldenCase c) {
    Object actual = pipeline().execute(c.input(), ctx(c.seed()));
    assertEquals(c.expected(), actual, "golden mismatch for " + c.id());
}

public static void properties(Random rnd, int iterations) {
    for (int i = 0; i < iterations; i++) {
        Object out = pipeline().execute(randomInput(rnd), ctx(rnd.nextLong()));
        assertAll(Objects::nonNull,                                   // never null
                  o -> countItems(o) <= MAX_ITEMS,                    // bounded growth
                  o -> !PiiPatterns.matches(text(o)));               // no PII leaks
    }
}
```

The PII invariant is the one worth copying into any production pipeline: it catches a
class of bug (a stage echoing a raw field) that example-based tests enumerate poorly.

## Self-Check

1. Why does `Stage` declare policy defaults rather than requiring configuration?
2. What happens if a non-idempotent stage is retried after a transient failure?
3. Why does the executor use a dedicated pool per stage?
4. What does including `configHash` in the cache key buy?
5. Why does `Bottleneck.targets()` intersect with the critical path?