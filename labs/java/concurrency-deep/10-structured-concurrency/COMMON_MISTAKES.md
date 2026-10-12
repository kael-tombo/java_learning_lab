# Common Mistakes: Structured Concurrency

## 1. Compiling without preview flags

Symptom: `StructuredTaskScope` appears missing despite the import.
Fix: `javac --release 23 --enable-preview` and `java --enable-preview`
on every snippet. The "missing import" reading is always wrong here.

## 2. Calling get() before knowing the state

`get()` on `UNAVAILABLE` or `FAILED` throws. After `join()`, either
route through the policy first (`throwIfFailed()` then `get()`, or
`result()`) or branch on `state()` for partial-result handling.

## 3. Joining from a helper thread

Passing the scope to another thread for `join()`/`result()` throws
`WrongThreadException`. Pass result values or handles out, never the
scope's control methods. Only the creator drives the lifecycle.

## 4. Forking after close

Reusing a scope across blocks throws `IllegalStateException` on the
late `fork()`. Scopes are single-block objects: one `try` block, one
lifetime, then a fresh scope for new work.

## 5. Rebinding scoped values mid-scope

Changing bindings between construction and `fork()` throws
`StructureViolationException`. Set bindings around the whole scope, not
between forks, so every subtask inherits the same lexical context.

## 6. Ignoring interrupts in compute subtasks

A spinning loop that never polls the interrupt flag survives
`shutdown()` and delays `close()`. Poll `Thread.currentThread()
.isInterrupted()` per chunk or use interruptible waits so fail-fast
actually goes fast.

## 7. Assuming JDK 25 spelling on JDK 23

JEP 505 reshaped parts of the API after this lab's pin. A method that
exists on 25 may not exist on 23 and vice versa — verify against the
release you run, flagged exactly as this lab does.

## 8. Platform-thread fan-out at scale

Hundreds of platform-thread subtasks burn roughly a megabyte of stack
each and scheduling overhead to match. Default to virtual threads for
any fan-out above trivial size; reserve platform threads for tiny,
bounded scopes.

## 9. Treating join() as cleanup

`join()` waits; `close()` cleans. Skipping `close()` is impossible in
`try`-with-resources, but skipping `join()` and reading handles right
after `fork()` observes `UNAVAILABLE` everywhere. Join first, then read.

## 10. Confusing orTimeout with derived stages

`CompletableFuture.orTimeout`/`completeOnTimeout` return `this` — the
same stage with a timer — while `thenApply`/`handle` derive new stages.
Porting timeout habits to scopes? Use `joinUntil(Instant)` on the scope
instead of per-subtask timers.
