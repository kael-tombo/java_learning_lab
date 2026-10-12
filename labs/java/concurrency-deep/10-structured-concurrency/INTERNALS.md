# Internals: Enforcement Mechanics (JDK 23)

## Owner tracking

The scope records its creating thread at construction. Every `join()`,
`close()`, and `result()` call checks `Thread.currentThread()` against
that owner and throws `WrongThreadException` on mismatch. Enforcement
is per-call, not per-scope-lifetime: a helper thread cannot join on the
owner's behalf even once, while subtask threads remain free to own
nested scopes of their own.

## Fork-after-close guard

`close()` flips the scope to a closed state before reaping leftovers.
Any later `fork()` observes the flag and throws `IllegalStateException`
without starting a thread. The check precedes binding validation, so a
late fork fails the same way regardless of scoped values.

## Scoped-value binding check

At creation the scope captures the current scoped-value bindings; each
`fork()` compares the forking thread's live bindings and throws
`StructureViolationException` on divergence. This co-design with scoped
values keeps context propagation lexical: a subtask always sees the
bindings its scope block saw, never a mutated or ambient set.

## Subtask state machine

Each `Subtask` moves `UNAVAILABLE` → `SUCCESS` or `UNAVAILABLE` →
`FAILED`, exactly once, on completion of its callable. `state()` exposes
the current value; `get()` returns the value on `SUCCESS` and throws on
anything else; `exception()` returns the failure on `FAILED` and null
otherwise. Transitions are terminal — no handle ever leaves a completed
state.

## Policy hook dispatch

`handleComplete` runs once per subtask completion, on the completing
subtask's thread, with the finished handle as argument. The built-ins
use it to decide shutdown: `ShutdownOnFailure` shuts down on the first
`FAILED` state and records the failure; `ShutdownOnSuccess` shuts down
on the first `SUCCESS` and records the value. Custom overrides must be
thread-safe because completions race each other.

## Shutdown mechanics

`shutdown()` marks the scope shut down exactly once and interrupts every
thread still registered as live. Late completions after shutdown still
record their states (visible via `state()`), but the policy outcome is
already decided — first failure or first success wins, later arrivals
only fill in diagnostics.

## Join and joinUntil blocking

`join()` parks the owner on an internal latch released when all subtasks
complete or shutdown-driven cancellation finishes reaping. `joinUntil`
parks on the same latch with a deadline computed from the given
`Instant`, throwing `TimeoutException` on expiry without disturbing
scope state — a timed-out join may be followed by `close()` cleanup.

## Close path ordering

`close()` first ensures shutdown, then waits for live subtasks to drain,
then releases scope resources. Skipped `join()` collapses into this
path: close still waits and shuts down, which is why control can never
leave the block with running children. Source location for all of the
above: `java.util.concurrent.StructuredTaskScope` in the JDK 23 tree.
