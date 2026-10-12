# Architecture: Scope as Lexical Owner

## The containment invariant

A `StructuredTaskScope` owns every subtask forked inside its
`try`-with-resources block. `close()` waits for and shuts down anything
still live, so no subtask can escape the block by falling off the end,
returning early, or throwing. Lexical nesting in source equals lifetime
nesting at runtime — the compiler-visible block is the unit of reasoning.

## Components and their roles

- Scope object: created by the owner thread, holds the subtask set, the
  policy hook, and the shutdown latch. One owner, many subtasks.
- `fork(Callable)`: registers a subtask, starts its thread, returns a
  `Subtask` handle immediately without blocking.
- `Subtask` handle: `state()` reports `UNAVAILABLE`, `SUCCESS`, or
  `FAILED`; `get()` yields the value; `exception()` yields the failure.
- `join()`: blocks the owner until all subtasks finish or the policy
  shuts the scope down early.
- `joinUntil(Instant)`: same wait with a deadline; `TimeoutException`
  on expiry, scope still cleanable via `close()`.
- `shutdown()`: interrupts and cancels live subtasks; invoked manually
  or automatically by the built-in policies.
- `close()`: final containment — reaps leftovers even if `join()` was
  skipped or threw.

## Policy layer

`ShutdownOnFailure` implements fail-fast conjunction: first `FAILED`
completion triggers `shutdown()`, and `throwIfFailed()` rethrows that
first failure after `join()`. `ShutdownOnSuccess<T>` implements
first-answer-wins disjunction: first `SUCCESS` triggers `shutdown()`,
and `result()` returns it. Both inherit the same fork/join/close
machinery; only the completion reaction differs.

## Extension point

Custom policies subclass `StructuredTaskScope` and override
`handleComplete`, called once per subtask completion on its thread.
Decide inside: count completions, record partial results, call
`shutdown()` when a quorum, deadline, or threshold is met. The base
class handles registration, ownership checks, and cleanup around it.

## Nesting architecture

A subtask thread may create and own a child scope, forking grandchild
subtasks inside it. Failures propagate level by level: inner
`throwIfFailed()` converts a child failure into the subtask's own
failure, which the outer scope observes as one failed unit. Each level
contains its own children, so a deep tree still has no orphans.

## Threading substrate

Thread-per-subtask is the structural assumption: each forked callable
runs on its own thread rather than a shared worker. The intended carrier
is the virtual thread — cheap stacks, scheduler-managed parking — so a
fan-out of hundreds stays affordable. Platform threads work for small
scopes but their per-thread stack cost makes large fan-outs wasteful.

## Data flow shape

Fan-out at `fork` time (handles collected), rendezvous at `join()`
(owner blocks), read-out after the policy method (`get()` per handle
under `ShutdownOnFailure`, single `result()` under `ShutdownOnSuccess`).
No queues, no latches, no manual future bookkeeping between those three
phases — the scope object carries all coordination state.
