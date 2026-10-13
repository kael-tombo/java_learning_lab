# Reordering — README

Source order is a suggestion. The JIT reorders within as-if-serial
freedom, the CPU issues out of order around stalls, and store buffers
hold writes invisibly before coherent cache. This lab *measures* the
consequence: the Dekker litmus (`x = 1; r1 = y` vs `y = 1; r2 = x`),
whose `(0,0)` outcome sequential consistency forbids absolutely —
observed on real x86 hardware in a large fraction of rendezvoused
iterations.

## What you will learn

- The three reordering layers (compiler, CPU execution, memory
  subsystem) and which one causes this lab's anomaly (the store
  buffer — proven by elimination in snippet 3).
- x86-TSO: LoadLoad, LoadStore, and StoreStore preserved; only
  StoreLoad escapes (Sewell et al., 2010). Dekker is StoreLoad's
  signature.
- Why ARM/POWER reorder more (any pair in principle; order from
  `LDAPR`/`STLR`/`DMB` and `lwsync`/`sync`), and why `volatile` fixes
  the litmus portably on all of them.
- Why demonstrating the anomaly needs a volatile-flag rendezvous per
  iteration — and why free-running threads or barrier phasing hide it.
- Which "fixes" are real (volatile: 0/20000; monitor: 0/20000) and
  which are diagnostic only (1 ns `parkNanos` drain) or insufficient
  (release/acquire still races).

## The five runnable demos (JDK 9+, verified on JDK 23)

| # | Class | Shape | Verdict on x86 |
|---|-------|-------|----------------|
| 1 | `DekkerAnomaly` | plain Dekker, rendezvoused | forbidden `(0,0)` routine (measured up to ~79%) |
| 2 | `VolatileFix` | identical, `volatile int` fields | `0/20000`, ordering holds |
| 3 | `DelayDrains` | snippet 1 + 1 ns `parkNanos` drain | `0/20000`, anomaly gone (timing, NOT a fix) |
| 4 | `ReleaseAcquire` | `setRelease`/`getAcquire` chain, 50000 | chain intact: `true` (sufficient here, not universal) |
| 5 | `MonitorFix` | Dekker pair under one lock | `0/20000`, exclusion forbids the anomaly |

Rates vary by machine, cores, and power state; verdicts (nonzero vs
zero) are the portable signal. The 1% assertion bar in snippets 1 and
5's cousins holds at large margins, not near them.

## How to work this lab

1. Read `THEORY.md` (three layers, x86-TSO, ARM/POWER qualitative,
   what the JVM emits, Dekker explained by elimination).
2. Read `CODE_DEEP_DIVE.md` with the sources: note the rendezvous
   design (volatile `go`/`done` flags, daemon racers, main-thread
   driver) shared by snippets 1-3 and 5.
3. Run snippet 1 first and confirm `reordering observed: true`; then 2,
   3, 5 and confirm each zero-claim. Read snippet 4 as the contrast
   (chains that hold for message-passing but do not order Dekker).
4. Do `EXERCISES.md`: convert rendezvous to free-running and watch the
   anomaly vanish without changing the verdict; swap barrier phasing
   in; apply the release/acquire Dekker variant from lab 03's snippet 5
   (61-90% anomalies) to feel pairwise-vs-total ordering.
5. Finish with `QUIZ.md`, `INTERVIEW.md`, `REFLECTION.md`.

## Where this fits

- Previous: `01-jmm-foundations` (the edges this lab deliberately
  omits in snippet 1 and restores in snippets 2/5).
- Next: `03-memory-barriers` (the fence taxonomy that explains *why*
  volatile costs ~10 ns and release/acquire still races Dekker).
- Requires: comfort with hb chains; this lab is the no-edge control
  group for the whole track.
