# Interview: Memory Barriers

## Q: Name the four barriers and assemble the three orderings.

A: LoadLoad, LoadStore, StoreStore, StoreLoad (JSR-133 cookbook).
Acquire = LoadLoad + LoadStore after the op; release = LoadStore +
StoreStore before it; SC adds StoreLoad after each volatile store —
the Dekker fence, the expensive one (~10 ns on x86).

## Q: State the roach-motel rule and its publication consequence.

A: Plain ops check in, never out: acquire pins successors (predecessors
may drift in from above); release pins predecessors (successors may
drift in from below). Consequence: `data`-before-`flag` publication is
safe (release keeps the prefix ordered), but observation-after-the-fact
is unordered — the motel admits traffic, it does not dispatch it.

## Q: Price the x86 ladder from this lab's measurements.

A: Plain stores ~1 ns; release (`lazySet`) ~1.3-1.4 ns rock-stable;
volatile stores ~10-18 ns (XCHG StoreLoad fence); volatile reads ~1.3
ns vs plain ~1 ns (acquire nearly free on TSO). Quote ratios (>3x
write fence, <5x read parity, >3x release saving) and fence counts
(0/0/1) — never absolutes — because nanoseconds are platform-relative.

## Q: lazySet vs set — when is each correct?

A: `lazySet` (release) where a one-directional chain suffices
(sequencing, pipelines — lab 02's 50000-intact chain) at ~1.3 ns;
`set` (volatile) where a total order is needed (Dekker, flags guarding
data) at ~10 ns. Same eventual visibility, different ordering
contract, ~8x gap — match the mode to the shape.

## Q: Plain message-passing passes 0/2000. Ship it?

A: No: verdict still `race`. TSO preserves StoreStore (accident), the
compiler may hoist the data read above the spin, ARM may reorder the
stores. Output identical to the volatile version, guarantee absent —
convert the flag (volatile/latch) and change the verdict while the
output stays put.

## Q: Release/acquire Dekker races at 61-90%. Why, structurally?

A: Pairwise chains do not compose into a total order: each
release->acquire pair orders locally while the cross observations slip
through the store buffers (on x86 both compile to bare MOVs). Only
StoreLoad fences on both sides (volatile, 0/20000) or exclusion (lock,
0/20000) close Dekker. Ordering modes are not a strength ladder where
"better sounding" suffices.

## Q: What is opaque, and where does it belong?

A: Atomic + eventually visible + unordered (Java 9 VarHandle): no
barrier in either direction. Progress counters and lossy statistics
only — never publication (no StoreStore), never guarding flags (no
LoadLoad/LoadStore). Below release, above plain (which additionally
tears and stales indefinitely).

## Q: How do you test barrier code?

A: Timing paths warmed 2M in-JVM, measured 20M back-to-back over
indexed 1024-slot traffic, asserting ratios (>3x, <5x) — never
absolutes, never cold, never single-location loops. Verdict paths
(2000/20000 rounds) asserting zero vs nonzero. Print pure ASCII;
`String.format("%.2f", ...)` exactly as the snippets do.
