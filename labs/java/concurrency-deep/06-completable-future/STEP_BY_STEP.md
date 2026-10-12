# Step by Step: Fetch → Parse → Combine

## Goal

A three-stage CF pipeline with correct executors, error handling, and
deadline — about 40 minutes.

## Step 1 — Supplies on the right pools (10 min)

```java
Executor ioPool = Executors.newFixedThreadPool(20);
CF<String> profile = supplyAsync(() -> fetchProfile(42), ioPool);
CF<String> orders = supplyAsync(() -> fetchOrders(42), ioPool);
```

Blocking fetches never touch the common pool. Print thread names once to prove
placement (expect `pool-N`, never `commonPool-worker`).

## Step 2 — Transform with map (5 min)

```java
CF<String> name = profile.thenApply(Json::parseName);  // sync: runs in completer
```

Pure parse stays sync — no hop needed. Confirm: already-complete input means
the attaching thread runs it.

## Step 3 — Sequence with flatMap (5 min)

```java
CF<List<Item>> items = name.thenCompose(n -> fetchHistoryAsync(n, ioPool));
```

Lambda returns `CF` → `thenCompose`. Write the `thenApply` version once, read
the `CF<CF<...>>` type, delete it — the nesting must be seen to be believed.

## Step 4 — Merge + deadline (10 min)

```java
CF<Page> page = profile.thenCombine(orders, Page::new)
    .orTimeout(2, TimeUnit.SECONDS)
    .exceptionally(ex -> Page.cached());
```

`thenCombine` fires in the last completer; `orTimeout` returns `this`
(assert `==`); `exceptionally` is the fallback. Fail one fetch on purpose and
watch the cached page arrive.

## Step 5 — Barrier variant (5 min)

```java
CF<Void> barrier = allOf(profile, orders);
CF<Page> page2 = barrier.thenApply(v -> new Page(profile.join(), orders.join()));
```

`join()`s cannot block post-barrier. Fail one input and inspect the suppressed
chain on the `CompletionException`.

## Step 6 — Harden (5 min)

Add `whenComplete((v, ex) -> metrics.record(ex))` (observation only), cancel
the losers of any `anyOf` hedge, and replace one `join()` inside a pool stage
with `thenCompose`. Shut down `ioPool` — leaked non-daemon pools hold the JVM.

## Done when

Thread names prove placement, nested-type bug demonstrated and fixed, barrier
values extracted, timeout asserted in-place, fallback verified by fault
injection.
