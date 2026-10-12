# Phaser — Security

## Threat: unarrived-slot exhaustion (barrier hold-open)

Any party that can `register()` but never arrive stalls every phase
forever — a single malicious or buggy participant denies service to all
survivors. Mitigations: register only trusted components directly; bound
untrusted participation behind timeouts (`awaitAdvanceInterruptibly` with
timeouts on the waiting side); run a supervisor that `forceTermination()`
when phase latency exceeds a deadline; always pair registration with a
`try/finally` deregistration path.

## Threat: premature termination via onAdvance abuse

A subclassed `onAdvance` returning true early ends the computation for
everyone while stragglers assume rendezvous happened — downstream phases
run on uncoordinated state. Keep phaser construction (including the
`onAdvance` override) in trusted code; never accept phaser instances or
overrides from untrusted callers. Log `(phase, parties)` per advance so
early termination is auditable.

## Threat: forceTermination as a weapon

`forceTermination()` opens the gate permanently — anyone holding a
reference can end synchronization for all parties silently. Do not share
mutable phaser references across trust boundaries; expose narrow
arrival/await facades instead of the object, and treat unexpected negative
phases as termination events to handle, not errors to ignore.

## Information exposure

`getPhase()`, `getRegisteredParties()`, and arrival return values reveal
computation progress and participant counts. In multi-tenant harnesses,
scope observability per tenant rather than sharing one phaser's
introspection globally.

## Denial-of-service via tiering

Each `new Phaser(parent)` consumes one parent slot; unbounded child
creation by untrusted code pins the parent open. Cap tier fan-out, own the
parent in trusted code, and deregister empty children promptly.

## Logging guidance

Log phase advances (counts, not payloads), termination events with their
cause (predicate, zero parties, forced), and phase-latency outliers. Never
log in a way that blocks the advance path — logging inside `onAdvance`
stalls every party; emit from a waiter released by the advance instead.
