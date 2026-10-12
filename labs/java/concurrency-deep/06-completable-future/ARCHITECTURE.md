# Architecture: CompletableFuture Pipelines

## Pipeline topology

```text
supplyAsync(fetch) ---> thenApply(parse) ---> thenCompose(enrich) ---> handle(fallback)
      |                        |                       |
   executor E1           completing thread      completing thread (or E2 if *Async)
```

Each arrow is a `Completion` node pushed on the upstream's stack. Completion
pops the stack and fires nodes — depth-first, in the completing thread, unless
a node names another executor.

## Stage kinds

- Transform: `thenApply` / `thenApplyAsync` (map).
- Sequence: `thenCompose` / `thenComposeAsync` (flatMap).
- Merge-two: `thenCombine`, `thenAcceptBoth`, `runAfterBoth`.
- Merge-N: `allOf` (barrier, `CF<Void>`), `anyOf` (race, `CF<Object>`).
- Recover: `exceptionally`, `handle`, `whenComplete`.
- Bound: `orTimeout`, `completeOnTimeout` (in-place, return `this`).
- Bridge: `complete`, `completeExceptionally`, `cancel`, `getNow`, `join`/`get`.

## Executor placement rules

```text
CPU-bound transforms .... completing thread or common pool (*Async default)
Blocking I/O stages ..... dedicated bounded pool (NEVER common pool)
Latency-critical merge .. same executor as the heavier upstream
```

The common pool is shared with parallel streams — a blocking CF stage there
is a cross-team incident. Size I/O pools by concurrency (`threads ≈
parallelism × (1 + wait/compute)`), not by core count.

## allOf value-extraction pattern

```text
CF<A> a; CF<B> b; CF<C> c;
allOf(a, b, c).thenApply(v -> new Triple(a.join(), b.join(), c.join()))
```

`join()` inside the barrier continuation cannot block (all complete) and
cannot wrap new checked exceptions (`CompletionException` only on failure,
which `allOf` already signals).

## anyOf hedging pattern

```text
anyOf(primary, replica).thenApply(o -> (Response) o)
```

Cast the `Object` back; cancel the loser explicitly (`loser.cancel(false)`)
or it keeps consuming resources — `anyOf` never cancels stragglers.

## Failure-flow architecture

Failures travel downstream until a handler: `exceptionally` converts to a
value, `handle` converts to a unified type, `whenComplete` observes and
rethrows implicitly. Unhandled terminal failure surfaces at `join()`
(`CompletionException`) or `get()` (`ExecutionException`).
