# Debugging: Volatile Semantics

## Capture
- Code search: every `volatile` declaration; every array-typed one is suspect (elements plain).
- Every `++`/`+=`/check-then-act on a volatile field is a race until proven otherwise.
- Every DCL-shaped null check must show the `volatile` keyword, the holder idiom, or an enum.

## Decode symptoms
- Stale flag (reader never sees update) -> missing volatile/edge on the flag.
- Half-constructed object via DCL -> field not volatile.
- Lost increments under load -> volatile counter instead of AtomicLong/LongAdder.
- Element-visibility failure -> volatile array reference mistaken for volatile elements.
- ARM-only failure -> barrier assumption tuned to x86 TSO; recheck edges, not timings.

## Triage recipe
1. Draw the intended edge: payload writes -> volatile write -> volatile read -> payload reads. Label each hop with its JLS 17.4 rule.
2. If any hop is missing (plain field, wrong flag, misordered statements), the fix is the edge, not a sleep/retry.
3. Confirm with a stress loop (`jshell` + threads) rather than a single run; races hide in single runs.

## Five-minute checklist
- [ ] Every cross-thread flag volatile? [ ] No compound ops on volatiles? [ ] DCL fields volatile? [ ] Array elements handled? [ ] long/double tearing covered?

## Sources
- JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9). Keep THEORY.md open; every diagnosis ends by naming the violated invariant.

## Edge-drawing protocol (the core move)
- For every visibility complaint, write the intended chain on paper: payload writes -po-> volatile write -hb-> volatile read -po-> payload reads; label each hop with its JLS 17.4 rule number.
- Missing-hop catalog: plain flag (no vol edge at all), flag written after the payload read needs it (order swapped), DCL field without the keyword (publication without edge), array elements behind a volatile reference (edge ends at the handle).
- A chain with all four hops present is a proof; anything shorter is a hypothesis — never "fix" a full chain with sleeps or retries.

## Hoisting forensics (stale-flag hangs)
- Spinner on a plain flag that never observes the write after OSR compilation: the JIT hoisted the read out of the loop — legal (no synchronization action forces reload), fatal to the design.
- Confirm by adding `volatile` and re-running the same harness: early exit vs run-to-bound (CODE_DEEP_DIVE.md snippet 1's structural assertion) separates visibility bugs from logic bugs.
- Shutdown-flag variant: service ignores stop requests under load but obeys them in tests — the hot loop got OSR-compiled in production only; volatile (or interrupt/latch) is the fix, not a shorter poll interval.

## Cross-architecture triage
- Fails on ARM, passes on x86 with identical bytecode: a barrier assumption tuned to TSO — some ordering your code relied on needs an explicit edge (volatile write/read pair, lock, or VarHandle mode) that x86 supplied for free.
- Never "fix" by weakening the x86 test load: the ARM failure names a missing edge in the chain; draw it, add the keyword, re-run on both.
- Long/double corruption on any platform: check volatility first (JLS 17.7 tearing permission) — half-old values mean the access was never atomic, regardless of what HotSpot usually does.

## Stress-loop confirmation
- Single-run passes prove nothing for races: loop DCL/piggyback/counter harnesses across thousands of iterations with thread starts jittered (`CountDownLatch` gate), and require the exact/fresh assertions from CODE_DEEP_DIVE.md.
- Record which configurations fail (thread count, architecture, JIT tier): a race that needs 8 threads to show is still a race at 2 — it just bills you later.
