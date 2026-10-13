# Internals: What the JIT Emits per Mode

## Mode to machine code (x86-64 measured; ARM64 qualitative)

```
plain read/write:      MOV / MOV            (no compiler fence effect on opt.)
opaque:                MOV / MOV            (atomicity only; no ordering edges)
acquire read:          MOV + compiler fence (no CPU fence on TSO)
release write:         MOV + compiler fence (no CPU fence on TSO; ~1.3 ns)
volatile read:         MOV + compiler fence (~1.3 ns; LDAPR on ARM64)
volatile write:        XCHG (lock prefix)   (StoreLoad fence; ~10 ns)
monitor enter/exit:    acquire / release around body + lock-word atomics
```

`PrintAssembly` (hsdis) shows the ladder's big step directly: the
volatile store path alone contains the locked instruction. Everything
else differs only in compiler-barrier annotations invisible in the
disassembly — which is why microbenchmarks are the honest way to price
the small steps and why verdict tests (not instruction-gazing) prove
the ordering.

## Compiler-side movement rules (roach motel, enforced in IR)

- Plain memory operations may be hoisted, sunk, commoned, or eliminated
  across each other freely within as-if-serial limits.
- At an acquire (volatile read, monitor entry, `getAcquire`), later
  memory ops cannot move above it; earlier plain ops MAY move below it
  (drift in from above). At a release (volatile write, monitor exit,
  `setRelease`), earlier ops cannot move below it; later plain ops MAY
  move above it (drift in from below).
- Opaque operations are atomic but movement-transparent: the JIT treats
  them like plain accesses for ordering (no pin), unlike volatiles.
  That single IR distinction is why opaque never publishes.
- Snippet 4's hoisting hazard is one legal motion: the `data` load
  drifting above the `flag` spin, with no acquire pin to stop it.
  Adding volatile/latch/opaque-free acquire inserts the pin.

## Why indexed 1024-slot traffic (harness internals)

- Distinct slots per iteration (`i & 1023`) defeat store-coalescing,
  load-commoning, and dead-store elimination: every iteration is honest
  memory traffic, not a register increment the JIT deletes.
- 1024 ints (4 KB) sit in L1: measurements price fences and L1 hits,
  not DRAM — fence effects isolated from memory-wall noise.
- 2M warmup both paths in the same JVM settles frequency scaling and
  completes TieredCompilation before the 20M measured window; running
  paths back-to-back cancels drift. First-run-wide spreads are the
  documented reason, not an excuse to skip warmup.

## VarHandle mode lattice (what each step buys)

```
plain < opaque < release/acquire < volatile < lock(exclusion+order)
atomic?  N       Y        Y                 Y          Y
visible? maybe   eventual pairwise-chained   SC-chain   mutual
ordered? never   never    pairs              total      serialized
x86 pay  ~1 ns   ~1 ns    ~1.3 ns            ~10 wr     tens of ns
```

Each step adds exactly one guarantee class for its price; skipping a
step (opaque for publication, release for Dekker) fails structurally,
not probabilistically. The snippets are placed to exhibit three of the
four boundaries: plain-vs-volatile (1), release-vs-volatile (3),
accident-vs-verdict (4), pairwise-vs-total (5).

## Where fences live in the JDK (library internals)

AQS state volatiles, `StampedLock` validation fences, and atomic-class
`Unsafe.fullFence` usage are the JDK's own applications of this
taxonomy — specified edges built from the same cookbook rows user code
gets via volatile/latch/VarHandle. Application code must not call the
fence intrinsics directly: same silicon effect, no JMM verdict, no
portability when ARM needs different placement.
