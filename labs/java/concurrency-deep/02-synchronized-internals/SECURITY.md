# Security: Synchronized Internals

## Threat 1 — lock-ordering deadlocks from untrusted call graphs
Nested `synchronized` on attacker-influenced objects in inconsistent order deadlocks the service. Enforce a global lock order, keep nesting shallow, and prefer one guard per request path.

## Threat 2 — monitor-identity spoofing via shared/interned locks
Locking on attacker-visible objects (string literals, boxed integers, passed-in parameters) lets outsiders hold your monitor and stall you. Lock only on private final guards you allocate.

## Threat 3 — alien calls under exclusion (TOCTOU + reentrancy abuse)
Overridable/callback code inside `synchronized` runs with your invariants half-open; hostile overrides mutate guarded state mid-section. Snapshot inputs, validate, exclude alien calls from the block.

## Threat 4 — wait/notify signal manipulation
`notify` (single arbitrary wakeup) on a shared monitor can be consumed by the wrong waiter, stranding the right one. Use `notifyAll` + `while`-recheck so a stolen signal cannot strand progress; bound waits with timeouts on untrusted inputs.

## Checklist
- [ ] Private final guards only. [ ] Global lock order documented. [ ] No alien calls inside blocks. [ ] wait-in-while + notifyAll + timeouts on exposed paths.

## Threat 5 — shared-identity locks as cross-tenant channels
- Locking on interned strings, boxed integers, or `Class` objects lets unrelated code (or tenants) synchronize on your monitor — contention becomes a cross-tenant signal or stall vector.
- Allocate `private final Object` guards per protected invariant; never lock on values that cross trust boundaries (parameters, deserialized keys, literal pool entries).
- Audit with identity logging: any guard whose `identityHashCode` collides across tenants is a shared channel until re-scoped.

## Threat 6 — `notify()` as a signal-theft primitive
- On a monitor with mixed waiters, a single `notify()` wakes one arbitrary thread — hostile or merely unlucky scheduling strands the security-critical waiter (timeout expiry, credential refresh) indefinitely.
- Default to `notifyAll()` plus `while`-recheck on every monitor reachable from untrusted inputs; bound every wait with a timeout so a stolen signal delays but never strands.
- Log wait-duration outliers per monitor: repeated near-timeout wakes on one guard are the observable shape of signal theft or notifier starvation.

## Threat 7 — monitor-held I/O as an amplification point
- Request paths that hold a `synchronized` monitor across network/disk I/O let one slow downstream stall every contender — attacker-paced slow responses convert into fleet-wide BLOCKED queues.
- Move I/O outside the block (snapshot-then-act); where exclusion must span I/O, use `tryLock(t)` with timeouts and fail open safely instead of queueing unboundedly.
- Cap EntryList exposure: bounded queues plus backpressure ahead of the guard turn unbounded BLOCKED growth into counted rejections.

## Detection
- Scrape `jstack` for BLOCKED counts grouped by monitor address: a single address dominating across captures is the guard to split or bound.
- Track JFR `jdk.JavaMonitorEnter` stall rates per guard in dashboards; alert on rate steps after deploys, not on absolute values.
- Review lock-order documentation per service: any new nested acquisition needs its order rank written down before merge — undocumented nesting is a deadlock PR away.
- Fuzz wait/notify paths with randomized notifier delays in tests; `if`-wait and bare-`notify` fail fast under jitter while `while`+`notifyAll` stays exact.

## Checklist additions
- [ ] Guards are private-final and never cross trust boundaries.
- [ ] Global lock order documented; new nesting ranks recorded.
- [ ] notifyAll + while-recheck + timeouts on all exposed monitors.
- [ ] No I/O, sleep, or alien calls inside request-path blocks.
- [ ] Contention alerts per guard address wired and tested.
