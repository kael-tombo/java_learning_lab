# Refactoring: CompletableFuture

## Blocking gets → chains

Before:

```java
Future<User> fu = exec.submit(() -> fetchUser(1));
Future<List<Order>> fo = exec.submit(() -> fetchOrders(1));
User u = fu.get(); List<Order> o = fo.get();  // two blocked threads
merge(u, o);
```

After:

```java
CF<User> u = supplyAsync(() -> fetchUser(1), ioPool);
CF<List<Order>> o = supplyAsync(() -> fetchOrders(1), ioPool);
CF<Page> page = u.thenCombine(o, Page::new).orTimeout(2, SECONDS);
```

No thread waits; the merge runs in whichever fetch finishes last.

## Nested futures → flatMap

Before: `u.thenApply(x -> fetchAsync(x))` giving `CF<CF<X>>` plus manual
unwrapping. After: `u.thenCompose(x -> fetchAsync(x))`. Grep for
`CF<CF<` — every hit is this bug.

## Try/catch fallback → exceptionally

Before:

```java
try { return fetchAsync().join(); }
catch (CompletionException e) { return cached(); }
```

After: `fetchAsync().exceptionally(ex -> cached())`. The fallback lives in
the pipeline, composable with timeouts and merges downstream.

## Two-path branching → handle

Before: separate success/failure handling with duplicated merge logic. After:

```java
fetchAsync().handle((v, ex) -> ex == null ? Result.ok(v) : Result.err(ex));
```

One downstream type; logging goes in `whenComplete` (observation only).

## Unbounded waits → in-place deadlines

Before: bare `join()` hanging forever on a lost producer. After:
`.orTimeout(2, SECONDS)` / `.completeOnTimeout(fallback, 2, SECONDS)` on the
same future — remember both return `this`, so existing aliases inherit the
deadline (verify that is what you want).

## Default-pool blocking → dedicated pool

Before: `supplyAsync(() -> blockingCall())`. After:
`supplyAsync(() -> blockingCall(), ioPool)`. Mechanical, mandatory — audit
every `supplyAsync`/`thenApplyAsync` call site without an explicit executor
for blocking bodies.
