# Common Mistakes: CompletableFuture

## 1. Blocking stages on the common pool

```java
supplyAsync(() -> blockingHttpCall());  // squats common pool worker
```

Under load this starves parallel streams and every other CF user. Fix: pass a
dedicated bounded executor as the last `*Async` argument.

## 2. `CF<CF<U>>` nesting

```java
CF<CF<List<Order>>> nested = user.thenApply(u -> fetchOrdersAsync(u)); // WRONG
CF<List<Order>> flat = user.thenCompose(u -> fetchOrdersAsync(u));     // RIGHT
```

`thenApply` with a future-returning lambda compiles and nests. `thenCompose`
is the flatMap — match the lambda's return shape to the combinator.

## 3. Expecting values from `allOf`

```java
CF<Void> barrier = allOf(a, b, c);
barrier.thenApply(v -> v);  // v is null — no values here
```

Fix: `barrier.thenApply(v -> new Triple(a.join(), b.join(), c.join()))` —
joins cannot block post-barrier.

## 4. Believing `cancel(true)` interrupts

```java
CF<String> f = supplyAsync(() -> slowWork());
f.cancel(true);  // flag IGNORED; slowWork runs to completion
```

Cancel only races an incomplete `result`. To stop running work, own the
`Future` from `ExecutorService.submit` and cancel *that*.

## 5. `getNow` as a timed get

```java
CF<String> f = fetchAsync();
String s = f.getNow("default");  // returns "default" if INCOMPLETE — never waits
```

Fix: `f.get(200, MILLISECONDS)` for bounded waiting; `getNow` is a
non-blocking peek.

## 6. `join()` self-deadlock in tiny pools

```java
Executor one = Executors.newFixedThreadPool(1);
supplyAsync(() -> inner.join(), one);  // thread waits for work needing itself
```

Chain (`thenCompose`) instead of blocking-join inside pool stages.

## 7. Forgetting `orTimeout` returns `this`

```java
CF<String> bounded = fetch.orTimeout(2, SECONDS);  // same object, not a copy
```

Both timeout methods mutate in place. Aliases of `fetch` observe the deadline
too — usually desired, surprising when it is not.

## 8. Swallowing sibling failures in `allOf`

`allOf(...).join()` throws the first-recorded failure; siblings attach as
suppressed. Logging only `getMessage()` hides them — log the full
`CompletionException` with its suppressed chain.
