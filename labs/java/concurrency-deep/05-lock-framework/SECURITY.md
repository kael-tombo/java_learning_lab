# Security: Lock Framework

## Denial of service via lock retention

Any path that skips `unlock` (exception, early return, forgotten `finally`)
wedges `state` and parks all future acquirers — a self-inflicted DoS. Treat
every `lock()` without a `try/finally` as a finding in review. Condition
`await()` in a loop without a timeout on untrusted wakeups has the same shape:
prefer `awaitNanos` with a deadline where the signaller is untrusted.

## Permit inflation as quota bypass

`Semaphore` permits are uncapped: a compromised or buggy client that calls
`release()` without `acquire()` mints permits, defeating rate limits and pool
bounds. Defenses: wrap semaphores behind facades that never expose raw
`release()`; assert `availablePermits()` at quiescence; log permit count on
quota-sensitive paths.

## Fairness and starvation attacks

Nonfair locks let a hot loop starve legitimate waiters — a malicious or greedy
tenant can hold effective ownership by re-barging. Multi-tenant handoffs with
adversarial timing want fair mode (bounded overtaking) plus hold-time budgets
enforced by `tryLock(timeout)` rather than bare `lock()`.

## Information exposure through introspection

`getFirstQueuedThread()`, `getQueueLength()`, `getOwner()`-style probes leak
activity and identity. Do not expose them through management APIs to untrusted
callers; gate lock telemetry behind admin roles.

## Interrupted-thread discipline

`lockInterruptibly()` + swallowed `InterruptedException` breaks cancellation:
shutdown signals vanish and threads park indefinitely. Propagate or restore
the interrupt; never log-and-continue on a lock-acquisition interrupt.

## Condition queue poisoning

`signalAll()` on attacker-reachable conditions wakes herds and burns CPU; a
missing predicate loop turns a spurious wakeup into a logic bypass (consumer
acts on a condition that is false). Always guard `await()` with the `while`
predicate, and prefer targeted `signal()` on the narrowest condition.

## Checklist

- [ ] Every `lock()` paired with `finally { unlock(); }`
- [ ] No raw `Semaphore.release()` reachable by untrusted code
- [ ] Fair mode + timeouts on multi-tenant locks
- [ ] No lock introspection in unprivileged APIs
- [ ] Interrupts propagated, never swallowed
- [ ] All `await()` calls predicate-looped
