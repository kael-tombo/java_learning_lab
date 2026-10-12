# Structured Concurrency — Theoretical Foundation

## Status Banner (read first)

This lab targets the **JDK 23 preview API** (`--enable-preview --release
23` — every snippet states its flags). The trail, all verified: incubator
in 19 (JEP 428) and 20 (JEP 437); previews in 21 (JEP 453) through 25 (JEP
505, *fifth* preview — still not final). JEP 505 reshaped parts of the API,
so code below is pinned to the JDK 23 surface, and the concepts (which are
stable) are called out separately from the syntax (which moved).

## Core Concept

Unstructured concurrency (`thread.start()`, `executor.submit()`) lets a
task outlive its spawner: the parent returns while children still run, fail
silently, or leak. Structured concurrency inverts the default — a
`StructuredTaskScope` is a **lexical scope that owns its subtasks**:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<String> a = scope.fork(() -> fetchA());
    Subtask<Integer> b = scope.fork(() -> fetchB());
    scope.join();              // wait for all (or policy shutdown)
    scope.throwIfFailed();     // rethrow first failure
    return combine(a.get(), b.get());
} // close() waits, then shuts down leftovers — no task escapes the block
```

The `try`-with-resources *is* the structure: subtasks cannot outlive the
block, failures propagate to the join point, and cancellation flows
downward. If it looks like single-threaded code with `fork` sprinkled in,
that resemblance is the entire design goal.

## The Two Policies (JDK 23)

- **`ShutdownOnFailure`**: first failing subtask triggers `shutdown()` —
  siblings are interrupted/cancelled; `join()` then `throwIfFailed()`
  rethrows the *first* exception (wrapping runtime exceptions appropriately).
  Use when subtasks are conjunctive (need all results: fan-out/fan-in).
- **`ShutdownOnSuccess<T>`**: first *successful* subtask triggers shutdown;
  `result()` returns it (throws `ExecutionException` if failures came first
  with no success, `IllegalStateException` if nothing completed). Use for
  hedged/redundant requests (race replicas, first-answer-wins).

Both extend `StructuredTaskScope<T>`; custom policies subclass it and
override `handleComplete` (called per subtask completion — the extension
point for quorum/deadline/partial-result policies).

## Ownership Rules (source-verified, JDK 23)

The source enforces structure with exceptions, not documentation:

- Only the **owner thread** (the one that created the scope) may
  `join()`/`close()`/`result()` — anyone else gets `WrongThreadException`.
  Subtask threads *may* fork nested scopes (nesting composes).
- `fork` after `close` → `IllegalStateException`.
- `fork` requires the same scoped-value bindings as scope creation, else
  `StructureViolationException` (structured concurrency + scoped values are
  co-designed: bindings propagate lexically into subtasks).
- `close()` without prior `join()` still waits/shuts down (the scope never
  leaks threads by falling off the end) — but explicit `join()` first is
  the idiom (join defines *what you wait for*; close defines *cleanup*).

## Cancellation Propagation

`scope.shutdown()` interrupts/cancels all live subtasks; a subtask failure
under `ShutdownOnFailure` triggers it automatically. Interruption flows the
same channel as `ExecutorService` (thread interrupt flag) — subtasks must
still honor it (blocking calls throw, compute loops must poll). What the
scope *adds* over manual bookkeeping: no orphan can survive the block, and
the first-failure-wins policy is three lines instead of latch-and-atomic
machinery.

## Subtask States (JDK 23: UNAVAILABLE / SUCCESS / FAILED)

```java
Subtask.State s = subtask.state();   // UNAVAILABLE (running), SUCCESS, FAILED
subtask.get();        // value or throws (FAILED → exception)
subtask.exception();  // the failure or null
```

Inspect states after `join()` for partial-result patterns (custom policies);
the two built-in policies hide this layer behind `throwIfFailed`/`result`.

## vs CompletableFuture Chains vs ExecutorService.invokeAll

| | Scope | CF chains | invokeAll |
|---|---|---|---|
| Lifetime bound | lexical block (compiler-visible) | manual (or leaks) | call return |
| Failure policy | built-in (failure/success) + custom | hand-rolled exceptionally/handle | first exception, others cancelled |
| Cancellation | automatic downward | manual per-stage | `cancel(true)` each |
| Threading | per-subtask thread (virtual-thread-first design) | pool-dependent | pool |
| Nesting | natural (scopes in subtasks) | works, unstructured | works, unstructured |

The conceptual debt CF chains accumulate (who owns which stage, who cancels
leftovers — lab 06's pitfalls) is exactly what the scope pays off. The price:
preview status and the virtual-thread-first threading model (each subtask
wants its own thread — platform-thread-per-subtask at scale is wasteful;
virtual threads are the intended carrier).

## Key Invariants

1. No subtask outlives its scope's block (close guarantees it).
2. Only the owner joins/closes/reads results (`WrongThreadException`
   otherwise).
3. First failure (ShutdownOnFailure) or first success (ShutdownOnSuccess)
   decides the scope; leftovers are shut down.
4. `fork` after close, or under changed scoped-value bindings, is rejected.
5. Subtask threading is thread-per-task — size with virtual threads, not
   platform threads.
