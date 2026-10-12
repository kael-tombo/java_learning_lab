# StampedLock — Security

## Stamps are not capabilities

The javadoc states stamps are not cryptographically secure and may be
guessable. They are sequential version values in a finite field — an
attacker who observes traffic can predict nearby stamps. Never use a stamp
as an auth token, session permit, or proof of identity across trust
boundaries. A guessed stamp passed to `unlock`/`validate` operates on the
lock, not on the guesser, so the blast radius is lock-state corruption.

## Threat: stamp guessing to corrupt lock state

`unlockRead`/`unlockWrite`/`unlock` accept any `long`. Code that exposes
stamp values (logs, exceptions, APIs returning raw stamps) lets a caller
feed crafted stamps back in: double-unlock drifts the reader count,
unlocking a foreign hold releases exclusion early. Mitigation: never let
stamps cross a trust boundary — keep them as method-local variables paired
in `try/finally`, and expose Lock views (which hide stamps) at API edges.

## Threat: unvalidated data driving security decisions

Optimistic reads may observe torn snapshots. If an authorization check,
bounds check, or cryptographic comparison runs on unvalidated fields, a
concurrent write can flip the outcome (time-of-check shape). Rule: every
security-relevant decision uses validated-or-pessimistic data only; audit
that checks sit strictly after `validate`.

## Threat: optimistic bodies with observable side effects

Network calls, file writes, or permission changes issued on torn data
cannot be rolled back when validation fails. Keep optimistic bodies to
local copies; emit effects only post-validation. Review test: delete the
fallback path mentally — any remaining effect is a bug.

## Denial-of-service considerations

A writer that holds the lock across slow I/O starves optimistic validity
(every validation fails) and blocks pessimistic readers outright. Bound
write-hold durations, never block inside a write hold, and monitor
validation-failure rates as a starvation signal.

## Logging guidance

Log validation-failure counts and conversion refusals (rates, not stamps).
Never log raw stamp values — they are guessable lock internals, and
logging them teaches nothing while expanding the guessing oracle.
