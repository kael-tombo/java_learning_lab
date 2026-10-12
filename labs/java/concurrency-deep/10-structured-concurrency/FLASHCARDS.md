# Flashcards: Structured Concurrency

## Q: Which JDK and flags does this lab pin to?
A: JDK 23 preview — `javac --release 23 --enable-preview`, `java
--enable-preview`. Re-verify on later releases; the API is not final.

## Q: What JEP trail brought structured concurrency here?
A: Incubator JEP 428 (19) and JEP 437 (20); preview from JEP 453 (21)
through the JDK 22–24 rounds to JEP 505, fifth preview in JDK 25.

## Q: What is the containment invariant in one sentence?
A: No subtask forked inside a scope's `try` block outlives `close()`.

## Q: When do you choose ShutdownOnFailure?
A: Conjunctive fan-out — every subtask result is needed; first failure
shuts down siblings and `throwIfFailed()` rethrows it.

## Q: When do you choose ShutdownOnSuccess?
A: Disjunctive race — one answer suffices (hedged replicas); first
success shuts down the rest and `result()` returns it.

## Q: How do you write a custom policy?
A: Extend `StructuredTaskScope`, override `handleComplete` (called per
completion), call `shutdown()` when your quorum/threshold predicate holds.

## Q: Who may call join/close/result?
A: Only the thread that created the scope — anyone else gets
`WrongThreadException`.

## Q: What does fork-after-close throw?
A: `IllegalStateException`, without starting any thread.

## Q: What does fork under changed scoped-value bindings throw?
A: `StructureViolationException` — bindings must match scope creation.

## Q: What are the three subtask states?
A: `UNAVAILABLE` (running), then terminal `SUCCESS` or `FAILED`.

## Q: Which accessors are legal in each state?
A: `get()` on `SUCCESS`; `exception()` non-null on `FAILED`; `state()`
anytime. `get()` on non-`SUCCESS` throws.

## Q: What does joinUntil(Instant) do on expiry?
A: Throws `TimeoutException`; the scope stays cleanable via `close()`.

## Q: What if close() runs without a prior join()?
A: It still waits for and shuts down leftovers — cleanup is guaranteed,
explicit `join()` first stays the idiom.

## Q: How does shutdown() cancel subtasks?
A: By interrupting live subtask threads; interruptible calls wake at
once, compute loops must poll the flag.

## Q: Why must subtasks honor interruption?
A: Otherwise they linger until `close()` reaps them, delaying block
exit — prompt cancellation needs cooperative subtasks.

## Q: What threading model does fork assume?
A: Thread-per-subtask, sized for virtual threads; platform threads work
for small scopes but waste ~1 MB stacks each at scale.

## Q: How does nesting compose?
A: A subtask thread may own a child scope; inner `throwIfFailed()`
converts child failure into the outer scope's one failed unit.

## Q: CompletableFuture.orTimeout returns what?
A: `this` — the same stage, mutated in place; unlike deriving
combinators (`thenApply`), which return new stages.

## Q: What is the scope analogue of orTimeout?
A: `joinUntil(Instant)` — bounded wait with `TimeoutException`, without
mutating any subtask.

## Q: What does result() throw when nothing succeeded?
A: `ExecutionException` if only failures arrived; `IllegalStateException`
if nothing was ever forked or completed.
