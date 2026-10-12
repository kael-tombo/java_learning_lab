# Security: CompletableFuture

## Common-pool exhaustion as DoS

Attacker-triggered fan-out (`supplyAsync` per request on the default pool)
with blocking bodies starves the shared pool — parallel streams and unrelated
CF chains stall. Defenses: dedicated bounded I/O pools with queue limits;
`orTimeout` on every external-facing future; reject (don't queue unboundedly)
past the bound.

## Exception leakage

`join()`/`get()` messages propagate upstream causes — including SQL text,
paths, or internal hostnames wrapped in `CompletionException`. Sanitize at the
`handle`/`exceptionally` boundary facing untrusted callers; log full chains
server-side, return typed errors client-side.

## Cancellation is not containment

`cancel()` never stops running work — a malicious or runaway `supplyAsync`
body keeps consuming CPU/connections after "cancellation." Contain with
executor shutdown (`shutdownNow` interrupts `FutureTask` runners), timeouts,
and resource-scoped try-with-resources — not CF cancel.

## Timeout ≠ revocation

`orTimeout` completes *this* exceptionally but the upstream keeps running and
may still mutate shared state or exfiltrate after the caller gave up. Pair
deadlines with explicit upstream cancel + idempotency guards where side
effects matter.

## `getNow` default confusion

Using `getNow(safeDefault)` on attacker-paced gates returns the default for
incomplete futures — downstream code may authorize on a value that is not the
real one. Treat `getNow` as untrusted-peek; use bounded `get(t, unit)` where
correctness depends on the true outcome.

## Unbounded `anyOf` hedging

Hedging multiplies backend load per request — attacker-amplified hedging is a
self-DoS multiplier. Cap hedge fan-out, hedge only past p95 (not always), and
cancel losers immediately.

## Checklist

- [ ] Blocking stages on bounded pools with queue limits
- [ ] `orTimeout` on external-facing futures
- [ ] Error boundaries sanitize causes for untrusted callers
- [ ] Upstream cancel paired with every deadline on side-effecting work
- [ ] No authorization on `getNow` defaults
- [ ] Hedge fan-out capped, losers cancelled
