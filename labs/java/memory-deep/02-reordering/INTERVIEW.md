# Interview: Reordering

## Q: What is the Dekker litmus, and what does (0,0) prove?

A: T1: `x = 1; r1 = y` vs T2: `y = 1; r2 = x`. Under sequential
consistency (0,0) is impossible (whichever store is first, the other's
load must see it). Observing (0,0) even once proves the platform is not
SC — on x86 it appears in a large fraction of rendezvoused rounds
(measured up to ~79%).

## Q: Which hardware structure causes it on x86?

A: The per-core store buffer: each store sits in a private FIFO while
the core's next load to another address executes immediately against
stale cache. Proof by elimination: identical bytecode plus 1 ns
`parkNanos` drain flips ~79% anomalies to 0/20000 — only a timing
sensitive buffer explains the difference.

## Q: State the x86-TSO pair table and its source.

A: LoadLoad, LoadStore, StoreStore preserved; exactly StoreLoad may
reorder (Sewell, Sarkar, Owens, Nardelli, Myreen, 2010; SPARC
heritage). Dekker is the StoreLoad pair, which is why it is x86's
signature anomaly while plain message-passing (StoreStore) passes by
accident on the same machine.

## Q: Why must the demo rendezvous per iteration?

A: The anomaly needs overlapping store;load windows. Free-running
threads phase-lock or miss; barrier phasing aligns starts but smears
windows through the barrier trip. The volatile-flag spin (`go`/`done`
with `onSpinWait`) aligns the windows tightly — rate is a harness
property, and this harness maximizes it.

## Q: Volatile vs monitor vs drain — three fixes compared?

A: Volatile (0/20000) works by ordering: StoreLoad fences on both
sides, portable. Monitor (0/20000) works by exclusion: pairs never
overlap, so ordering is moot. Drain (0/20000) is diagnostic only: same
race, hidden by timing, broken on ARM and under load. Ship the first
or third according to whether you need flags or exclusion.

## Q: Why does release/acquire fix message-passing but not Dekker?

A: Release/acquire builds pairwise chains (writer release to reader
acquire — snippet 4 intact over 50000). Dekker needs a total order over
two independent pairs; two chains do not compose into one (lab 03
measures 61-90% anomalies under release/acquire Dekker). Match the mode
to the shape: chains for handoff, SC (volatile) or exclusion for
mutual observation.

## Q: What did Tomasulo contribute (1967)?

A: Out-of-order issue with in-order commit (IBM 360/91): reservation
stations fire operations when operands are ready; the reorder buffer
retires in program order. Invisible to one thread, observable across
threads through shared memory — the execution layer beneath the memory
subsystem's buffers.

## Q: How do ARM64 and POWER differ from x86 here?

A: Qualitatively weaker: in principle any pair may reorder, with order
from explicit instructions (ARM64 `LDAPR`/`STLR`/`DMB`; POWER
`lwsync`/`sync`). ARMv8 is multi-copy-atomic, POWER is not (IRIW-class
litmus distinguishes them in research). Java volatile lowers to the
appropriate primitives per platform with identical verdicts.
