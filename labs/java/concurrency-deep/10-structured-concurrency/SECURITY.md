# Security: Scopes and Least Surprise

## Containment limits blast radius

A compromised or buggy subtask cannot outlive its block: `close()`
reaps it even on exceptional exit. Long-lived exfiltration threads
planted inside scoped work die with the scope, unlike strays from raw
`start()`/`submit()` that persist for the JVM lifetime.

## Owner-only control blocks hijack

`WrongThreadException` rejects any non-owner driving `join()`,
`close()`, or `result()`. An attacker thread sharing the heap cannot
prematurely join a victim's scope, steal its `result()`, or close it
early — control stays with the creator by exception enforcement.

## Binding checks prevent context confusion

`StructureViolationException` on fork under diverging scoped-value
bindings stops privilege or tenant context from silently changing
mid-scope. A subtask always runs under the bindings its scope captured,
so tenant IDs, credentials, and locale handles propagate lexically
rather than ambiently.

## Failure messages as information channels

`throwIfFailed()` and per-handle `exception()` expose backend failure
detail (class names, messages, causes). Log them server-side; do not
forward raw causes to untrusted callers — wrap in a generic error at
trust boundaries so replica topology and backend identity stay hidden.

## Cancellation as denial-of-service hygiene

Fail-fast and deadline (`joinUntil`) scopes bound how long attacker-
slow backends can hold threads. A hung replica under `ShutdownOnSuccess`
loses to faster answers and is interrupted; under `ShutdownOnFailure` a
hung sibling dies with the first failure. Always pair untrusted fan-out
with either a policy that shuts down or an explicit deadline.

## Interrupt-ignoring subtasks as hold-open risk

A subtask that swallows interrupts extends block exit indefinitely,
which a malicious or pathological callable can exploit to pin threads.
Treat interrupt-honoring as a security property: audit subtask code for
flag polling, prefer interruptible calls, and keep `joinUntil`
deadlines on any scope touching untrusted work.

## Custom handleComplete runs on attacker-influenced threads

The hook executes on completing subtask threads, which race. Keep it
free of shared mutable state beyond properly synchronized counters —
an unsynchronized override is both a correctness bug and a vector for
inconsistent shutdown decisions under adversarial timing.

## Nesting and privilege layering

Inner scopes inherit the subtask thread's context, so a privileged
outer block must not fork untrusted callables where inner scopes could
observe ambient authority. Structure untrusted work as leaves with
minimal bindings; keep secret-bearing bindings above scopes that never
fork outside trusted code.
