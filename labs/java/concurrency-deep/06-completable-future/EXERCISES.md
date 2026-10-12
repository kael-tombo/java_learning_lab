# Exercises: CompletableFuture

All snippets compile on JDK 9+ with no dependencies.

## 1. Who-runs-it probe

```java
String main = Thread.currentThread().getName();
completedFuture("x").thenApply(v -> {
    System.out.println("sync == caller: " + Thread.currentThread().getName().equals(main));
    return v;
});
CountDownLatch done = new CountDownLatch(1);
completedFuture("x").thenApplyAsync(v -> {
    System.out.println("async == common pool: "
        + Thread.currentThread().getName().startsWith("ForkJoinPool.commonPool-worker"));
    done.countDown(); return v;
});
done.await();
```

Expect `true`/`true`. Then attach `thenApply` to an *incomplete* gate
completed by a named thread — confirm the dependent runs in that thread.

## 2. Map vs flatMap fix

```java
CF<User> u = supplyAsync(() -> fetchUser(1));
// BROKEN: CF<CF<List<Order>>> nested = u.thenApply(x -> fetchOrdersAsync(x));
CF<List<Order>> flat = u.thenCompose(x -> fetchOrdersAsync(x));
```

Write both, print `nested.getClass()` vs `flat` element type. Rule: lambda
returns `CF` → `thenCompose`, always.

## 3. allOf extraction

```java
CF<String> a = supplyAsync(() -> "a");
CF<Integer> b = supplyAsync(() -> 1);
CF<String> all = allOf(a, b).thenApply(v -> a.join() + b.join());
System.out.println(all.join()); // "a1"
```

Then fail one input exceptionally and show: `allOf.join()` throws, cause is
the first failure, sibling in suppressed.

## 4. anyOf hedge + loser cancel

Race `primary` vs `replica` with `anyOf`, cast the `Object` result, and
explicitly cancel the loser. Prove the loser kept running without the cancel
(counter increment) and stops counting with it.

## 5. Handler contracts

One failing future through three terminals: `exceptionally(ex -> fallback)`
(value recovers), `handle((v, ex) -> ex == null ? v : fallback)` (unifies),
`whenComplete((v, ex) -> log(...))` (original failure preserved — `join`
still throws). Assert all three behaviors in one test.

## 6. Timeout in-place + cancel race

Assert `f.orTimeout(2, SECONDS) == f` (identity). Then: gate future + slow
`supplyAsync`; `cancel(false)` before completion returns `true` and
dependents see `CancellationException`; `cancel(true)` on a running body still
lets the body finish (log from inside the body proves it).
