# Internals: What the JVM Emits (and Doesn't Expose)

## No user-level fences in java.*

Java offers ordering through `volatile`, monitors, `final`, and
`VarHandle` modes (`getAcquire`/`setRelease`/`getOpaque`) — never a raw
"emit fence here" intrinsic for application code. `Unsafe`
(`jdk.internal.misc`) does carry `loadFence`/`storeFence`/`fullFence`,
but those are library internals (AQS, `StampedLock` validation, atomic
classes); reaching past the API to fence by hand forfeits the JMM
verdicts this lab measures.

## What the JIT does at synchronization actions

- At a volatile access or monitor operation the JIT inserts the
  platform's required barrier *and* forbids moving memory operations
  across it (compiler side of the contract). Plain accesses get neither
  treatment: hoisting, sinking, and elimination apply freely.
- Snippet 1's racer bodies compile to bare store;load (plain MOVs on
  x86) with no fence between — the hardware is then free to exhibit
  exactly what it exhibits. Snippet 2's bodies compile with the
  StoreLoad fence after each store (`XCHG` on x86) — the anomaly has
  nowhere to come from.
- The rendezvous spins (`while (!go) onSpinWait()`) compile against
  volatile loads, which the JIT cannot hoist out of the loop — the
  property the whole 20000-round driver depends on.

## What the hardware does with the emitted code (x86)

- Plain store retires to the per-core store buffer (FIFO); the following
  load to another address issues immediately against coherent cache.
  Store-to-load forwarding applies only to the core's *own* pending
  store (same address) — Dekker's loads are to the *other* address, so
  no forwarding rescues them; they read stale cache instead.
- Invalidate queues defer coherence acknowledgments, widening the
  window in which the peer's store is invisible. The 1 ns drain lets
  both queues settle: same instructions, ordered observation.

## ARM64/POWER lowering (qualitative, same verdicts)

- Volatile read/write lower toward `LDAPR`/`STLR` plus `DMB` where the
  JMM's SC-for-volatiles demands a full fence; plain accesses stay bare
  loads/stores. Release/acquire modes use the one-way primitives
  without the full fence — cheaper, and insufficient for Dekker, on
  every platform.
- POWER's `lwsync` vs `sync` is the same tradeoff at its weakest
  setting: lightweight orders pairs, full (cumulative) orders systems.
  The lab does not measure POWER rates — verdicts (volatile/lock zero,
  release/acquire nonzero) are the portable claims.

## Why the driver design is load-bearing

Daemon racers plus a main-thread driver with volatile handshake flags
keep all rendezvous synchronization in *ordered* operations while the
measured bodies stay *plain*. Any "simplification" that makes the
handshake plain (or merges driver and racer) contaminates the
measurement with the very reordering under test. The harness is part of
the instrument — modify bodies, never the handshake.
