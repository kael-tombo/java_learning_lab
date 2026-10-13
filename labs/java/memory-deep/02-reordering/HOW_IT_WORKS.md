# How It Works: Reordering

## The mechanism in one paragraph

Each Dekker side executes store-then-load to different addresses. The
store retires into the core's private FIFO (store buffer) instead of
reaching coherent cache; the load issues immediately against cache that
still holds the other side's pre-store value. Both sides do this
simultaneously, both loads read 0, and the forbidden-under-SC outcome
prints — at ~79% of tight rendezvous rounds, because the windows
coincide by construction.

## Why sequential consistency forbids (0,0) absolutely

SC requires one total order over all four operations respecting each
thread's program order, with each read seeing the latest prior write.
Case analysis: if `x = 1` is first, T2's `r2 = x` must see 1; if
`y = 1` is first, T1's `r1 = y` must see 1; simultaneous stores still
order one first. No total order yields (0,0) — the outcome is not rare
under SC, it is *impossible*. Observing it even once refutes SC for the
platform (which is the point: hardware is not SC).

## The rendezvous: manufacturing simultaneity

Daemon racers spin on volatile `go` (`while (!go) onSpinWait()`),
execute exactly one store;load pair, signal volatile `done`, then spin
on `go` clearing. The main thread resets `x = y = 0` and the done
flags, sets `go = true`, spins until both done, samples `r1slot`/`r2slot`,
then clears `go`. Volatile flags make the window edges themselves
ordered (spins cannot hoist, signals are visible), so the two
store;load pairs fire within nanoseconds of each other, thousands of
rounds in a row. Free-running or barrier-phased variants smear the same
windows — same verdict, collapsed rate.

## Elimination: the 1 ns drain that convicts the buffer

`DelayDrains` changes one thing: `parkNanos(1)` between each store and
load. Bytecode identical (nothing new to hoist; nothing was hoisted —
the opaque park call pins order even harder), CPU dependencies
identical, yet anomalies fall from ~79% to 0/20000. The only changed
quantity is *time for the FIFO to drain*. Compiler and OoO theories
predict no change; the buffer theory predicts exactly this. The buffer
is convicted by difference, not by authority.

## Why volatile zeroes it (both sides)

Volatile stores emit the platform's StoreLoad fence (`XCHG` on x86;
fenced release on ARM64) and volatile loads acquire; the JMM's SC
guarantee for the volatile chain forbids precisely the exhibited pair
on every platform. Same threads, same rendezvous, same 20000 rounds —
two keywords, ~15000 anomalies deleted. The delta is ordering
semantics, visible in no other variable.

## Why the monitor zeroes it (differently)

`MonitorFix` wraps each pair in `synchronized (LOCK)`: the two bodies
never overlap, so there is no simultaneity for the buffers to exploit.
Ordering is irrelevant when there is no concurrency to order — the fix
works by *exclusion*. Three resolutions, three mechanisms: volatile
(ordering), drain (timing — diagnostic only), lock (exclusion). Only
the first and third are synchronization.

## Why release/acquire does not (preview of lab 03)

`setRelease`/`getAcquire` build pairwise chains (my release to your
acquire), and Dekker has two independent pairs with no chain between
the cross observations. Each pair orders locally while the cross pair
slips through the buffers: 61-90% anomalies, indistinguishable from
plain. Chains compose for message-passing (snippet 4: 50000 intact);
they do not compose into the total order Dekker demands.
