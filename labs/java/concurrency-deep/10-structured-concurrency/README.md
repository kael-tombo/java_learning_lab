# Structured Concurrency (Lab 10)

JDK 23 preview API: compile with `javac --release 23 --enable-preview`
and run with `java --enable-preview`. Pinned to the JDK 23 surface
because JEP 505 reshaped parts of the API later; concepts below are
stable, syntax is version-pinned.

## What this lab covers

`java.util.concurrent.StructuredTaskScope` treats concurrent subtasks as
owned by a lexical block. The `try`-with-resources block is the structure:
nothing forked inside may outlive `close()`, failures route to the join
point, and cancellation flows downward to live subtasks.

## The two built-in policies

- `ShutdownOnFailure` — conjunctive fan-out. Fork N subtasks, `join()`,
  then `throwIfFailed()` rethrows the first failure. First failure calls
  `shutdown()` so siblings are cancelled instead of orphaned.
- `ShutdownOnSuccess<T>` — disjunctive race. First success triggers
  shutdown; `result()` returns the winner. Use for hedged or replicated
  requests where one answer is enough.

Custom policies extend `StructuredTaskScope` and override `handleComplete`,
invoked once per subtask completion. Quorum, deadline, and partial-result
shapes all build on that single hook.

## Ownership in one paragraph

Only the thread that created a scope may `join()`, `close()`, or read
`result()`; any other thread gets `WrongThreadException`. Forking after
`close()` throws `IllegalStateException`. Forking under different
scoped-value bindings than creation throws `StructureViolationException`.
Subtask threads may fork nested scopes — nesting composes level by level.

## Subtask handles

Each `fork()` returns a `Subtask` with `state()` (`UNAVAILABLE` while
running, then `SUCCESS` or `FAILED`), `get()` (value, unchecked after a
successful join), and `exception()` (the failure or null). The built-in
policies usually hide this layer behind `throwIfFailed()` / `result()`.

## Bounded waits and cleanup

`joinUntil(Instant)` waits until a deadline and throws `TimeoutException`
on expiry. `close()` without a prior `join()` still waits for and shuts
down leftovers — explicit `join()` first stays the idiom because join
states what you wait for while close only guarantees cleanup.

## Threading model

One thread per subtask. That design assumes cheap threads: size scopes
with virtual threads, not platform threads. Hundreds of platform-thread
subtasks waste roughly a megabyte of stack each; virtual threads make
thread-per-subtask affordable and let nesting scale.

## How to work this lab

Read THEORY.md, then CODE_DEEP_DIVE.md — both are source-verified
against JDK 23 and never contradicted here. Then pick a path: HOW_IT_WORKS
for the lifecycle, STEP_BY_STEP for a guided build, EXERCISES for runnable
preview-API tasks, QUIZ and FLASHCARDS for recall, DEBUGGING for the four
enforcement exceptions, PERFORMANCE for sizing numbers.
