# How CompletableFuture Works

## The completion event

A CF holds a `result` field (value, `AltResult` failure wrapper, or null =
incomplete) plus a stack of dependent `Completion` nodes. `complete(v)` CASes
`result` non-null and runs `postComplete()`: pop each dependent, fire it.
First completion wins; late calls return `false`.

## The thread rule, precisely

1. Dependent attached to an *already-complete* future with a sync method
   (`thenApply`): runs immediately in the *attaching* thread — no pool.
2. Dependent attached to an *incomplete* future: runs in *whatever thread
   completes it* (`complete()` caller, `supplyAsync` worker, timeout thread).
3. `*Async` without executor: submitted to `ForkJoinPool.commonPool()` — when
   `USE_COMMON_POOL` holds (parallelism > 1); otherwise a fresh thread per task.
4. `*Async` with executor: runs there, always.

## Map vs flatMap

```java
CF<User> u = supplyAsync(() -> fetch(1));
CF<String> name = u.thenApply(User::name);            // T -> U
CF<List<Order>> orders = u.thenCompose(x -> fetchOrders(x)); // T -> CF<U>
```

`thenApply(x -> fetchOrders(x))` yields `CF<CF<List<Order>>>` — compiles,
wrong shape. The compiler cannot warn you; the type nesting is the signal.

## Combining mechanics

- `thenCombine(other, (a, b) -> ...)`: fires when both complete; runs in
  whichever completes *last* (sync) or the named executor (async).
- `allOf(a, b, c)`: internal counter ticks per completion; the barrier CF
  completes (with `null` value) when the count hits zero. Values stay in
  `a`, `b`, `c` — pull with `join()` (non-blocking now).
- `anyOf(...)`: first completion (value OR exception) completes the
  `CF<Object>`; stragglers keep running unless cancelled.

## Error-handler firing

- `exceptionally(f)`: only on failure; `f`'s return becomes the value; `f`
  throwing keeps the chain exceptional.
- `handle((v, ex) -> ...)`: always; exactly one of `v`/`ex` is meaningful.
- `whenComplete((v, ex) -> ...)`: always; return ignored; outcome unchanged.
- `orTimeout(t)`: a scheduler completes *this* exceptionally on expiry;
  `completeOnTimeout(v, t)` completes *this* with `v` instead. Both return `this`.

## Cancel mechanics

`cancel(b)` CASes an `AltResult(CancellationException)` into `result` — the
`b` flag is never consulted (no owned thread exists). Dependents observe
`CancellationException`; an already-running `supplyAsync` body runs to its end.
