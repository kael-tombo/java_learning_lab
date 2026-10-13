# Debugging: Memory Barriers

## Timing snippets disagree with the ladder — suspect the harness

Expected within one warmed JVM on x86: plain stores ~1.0-1.2 ns,
release ~1.3-1.4 ns rock-stable, volatile stores clearly above 3x
plain (~10-18 ns), volatile reads within 5x of plain (~1.0-1.4 vs
~0.9-2.2). Deviations diagnose themselves:

- Volatile barely above plain (<3x): frequency still ramping (first
  JVM run) or slots shared (JIT eliminated to registers) — re-run
  warmed with indexed 1024-slot traffic as the snippets do.
- Release far above plain (>3x): different array types per path or
  bounds checks differing — use the identical `AtomicIntegerArray`
  shape for both paths (snippet 3) and re-measure.
- Reads wildly apart (>5x): the `sink` accumulation got optimized
  (dead-code elimination of one path) — keep the `plain[0] = sink`
  escape and the 1024 mask in place.
- Ladder inverted (release slower than volatile): competing load on
  the box (frequency dip mid-run) — rerun quiet, both paths in one
  JVM, back-to-back, and quote the ratio, not the absolute.

## Snippet 4 shows stale reads on x86 (unexpected nonzero)

Plain message-passing should read 0/2000 here (StoreStore preserved).
Nonzero means the environment, not the theory, shifted:

- ARM host or emulated weak memory: StoreStore not preserved —
  verdict still `race`, output now honest about it. Convert to
  volatile and confirm zero with a verdict.
- JIT hoisted the `data` read above the spin (rare at 2000 rounds,
  possible): increase rounds or inspect with `-XX:+PrintAssembly` —
  the hoisted load is the compiler half of the missing edge.
- Thread startup dominated (timeouts tripped): `join(5000)` windows
  hit under extreme load — rerun quiet; the verdict line (`STILL
  race`) is unaffected either way.

## Snippet 5 shows zero anomalies (unexpected for release/acquire)

Release/acquire Dekker should print persistent anomalies (61-90%).
Zero means the harness changed shape:

- Fields accidentally volatile (plain `int` required, accessed only
  via the VarHandle) — a `volatile` keyword on `x`/`y` converts the
  test to full SC silently.
- Handshake flags made plain or driver sleeps added — windows no
  longer coincide; restore the volatile `go`/`done` rendezvous.
- Too few iterations or cold, throttled cores — run the full 20000
  warmed; assert `bad > iters / 100`, not any exact count.

## Proving which fence is missing (elimination)

1. Baseline the verdict (nonzero = race, e.g., snippet 5).
2. Escalate one mode step: release/acquire -> volatile (add the
   StoreLoad fence). Nonzero -> zero convicts the missing StoreLoad.
3. Cross-check orthogonally: volatile -> lock (ordering -> exclusion).
   Zero persists by a different mechanism — confirms the shape needed
   system-wide order, not just pairwise chains.
4. Never "confirm" with a drain: 1 ns parkNanos also zeroes x86 rates
   with no fence at all (lab 02 snippet 3) — timing evidence is
   inadmissible for ordering claims.

## Tools

- `-XX:+PrintAssembly` (hsdis): confirm `XCHG` (or locked op) on the
  volatile path vs bare MOVs on plain/release paths — the one-bit
  visual proof of the ladder's big step.
- jcstress for verdict histograms when hand-rolled 20000-round counts
  are questioned; per-round outcome modes (IRIW-style) for ARM hosts.
- `String.format("%.2f", ...)` with pure-ASCII println (harness rule):
  locale/encoding artifacts in timing output are harness failures —
  keep the format exactly as the snippets do.
