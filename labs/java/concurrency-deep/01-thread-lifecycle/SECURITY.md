# Security: Thread Lifecycle

## Threat 1 — uninterruptible blocking as DoS surface
Threads stuck entering `synchronized` ignore interrupts; an attacker-controlled path that funnels requests onto one monitor lets a slow holder starve the fleet. Mitigate with bounded entry (`tryLock` with timeout) on untrusted paths and monitor-contention alerts.

## Threat 2 — daemon abandonment losing audit/finalize work
Security-relevant writes (audit logs, token revocation) on daemon threads vanish at JVM exit. Run them non-daemon with explicit shutdown + join, and flush in shutdown hooks.

## Threat 3 — thread-dump information exposure
Dumps print thread names, stack frames, and held locks — often package paths and request identifiers. Restrict `jstack/jcmd` to operators, scrub dumps before attaching to tickets.

## Threat 4 — interrupt-status mishandling breaking cancellation
Swallowed `InterruptedException` (catch-and-continue without restore) makes worker pools ignore shutdown, keeping compromised tasks alive. Always restore (`Thread.currentThread().interrupt()`) or propagate.

## Checklist
- [ ] Untrusted paths never block uninterruptibly on one monitor. [ ] Audit writes non-daemon + joined. [ ] Dumps access-controlled. [ ] Interrupts propagated, never silently cleared.

## Threat 5 — getState-driven control as a race primitive
- Branching security logic on another thread's sampled state (e.g. "worker is WAITING, so secrets are sealed") races the sampler: the state flips between check and act.
- Gate releases on join/latch/future completion, never on observed states — completion is final, samples are stale on arrival.
- Health endpoints may *report* states; they must never *authorize* on them.

## Threat 6 — un-cancellable park loops holding sensitive work
- Park-based waits that never poll `Thread.interrupted()` ignore shutdown; a stuck task keeps handles, locks, or decrypted buffers alive past revocation time.
- Every park loop needs an interrupt/cancel poll plus a bounded wait — unbounded `park()` on a security-sensitive path is a retention bug.
- Convert `catch (InterruptedException)` swallows on these paths into restore-and-abort; continuing after cancel extends exposure.

## Threat 7 — carrier pinning as a noisy-neighbor amplifier
- On virtual-thread runtimes, attacker-triggerable paths through a `synchronized` hot spot pin carriers and convert one slow holder into fleet-wide starvation.
- Keep untrusted paths off `synchronized` monitors; prefer interruptible locks with timeouts there so a slow holder is bounded, not contagious.
- Count pinning with JFR `jdk.VirtualThreadPinned` on exposed endpoints before and after the swap.

## Detection
- Alert on BLOCKED-thread count per monitor address (from `jstack` scrapes or JFR `jdk.JavaMonitorEnter` rates): a rising single-address cluster is contention turning into denial of service.
- Alert on shutdown duration: pools that ignore interrupts show join timeouts plus swallowed status — log interrupt-restore discipline in review.
- Review every `catch (InterruptedException)` for restore-or-propagate; a bare `ignored` on a worker loop is a cancellation bypass until proven otherwise.
- Gate dumps (`jstack`/`jcmd`) behind operator roles; audit who pulled thread text containing request IDs or secrets-adjacent frames.
- Load-test the untrusted path at 10x expected concurrency and watch carrier counts, not just latency — pinning hides in averages.

## Checklist additions
- [ ] Security decisions join on completion, never on sampled states.
- [ ] Every park loop polls interruption and has a bound.
- [ ] Untrusted paths use interruptible locks with timeouts, not bare `synchronized`.
- [ ] Interrupt catches restore or propagate; none swallow silently.
- [ ] Dump access logged and scrubbed before tickets.
- [ ] Pinning events (21+) reviewed on exposed endpoints after migration.
