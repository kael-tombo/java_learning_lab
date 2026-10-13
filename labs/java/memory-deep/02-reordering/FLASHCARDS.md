# Flashcards: Reordering

Q: What is the Dekker litmus shape?
A: T1: x = 1; r1 = y || T2: y = 1; r2 = x; outcome r1 == r2 == 0 is
forbidden under sequential consistency.

Q: What does this lab measure for plain Dekker on x86?
A: The forbidden (0,0) outcome in a large fraction of rendezvoused
iterations (tens of percent; up to ~79% measured) — routine, not rare.

Q: Name the three reordering layers.
A: Compiler (javac + JIT hoisting/sinking/elimination); CPU execution
(out-of-order issue, in-order commit); memory subsystem (store buffers,
forwarding, invalidate queues).

Q: Which layer causes the x86 Dekker anomaly, and how was it proven?
A: The store buffer (layer 3): identical bytecode plus 1 ns parkNanos
drain yields 0/20000 — timing changed, verdict flipped, so compiler
and OoO layers are exonerated here.

Q: State x86-TSO's pair table (Sewell et al., 2010).
A: LoadLoad, LoadStore, StoreStore preserved; exactly StoreLoad may
reorder (store sits buffered while a later load to another address
executes).

Q: Why does plain message-passing usually pass on x86 while Dekker fails?
A: Message-passing needs StoreStore (preserved on TSO); Dekker needs
StoreLoad ordered (the one freed pair). One table row is the whole
difference — accident, not guarantee.

Q: What rendezvous does the anomaly demonstration require?
A: Per-iteration volatile-flag spins (go/done1/done2 with onSpinWait),
daemon racers, main-thread driver resetting x = y = 0 each round.

Q: Why do free-running threads hide the anomaly?
A: They phase-lock or never collide: overlap windows rarely align, so
collision rate collapses while the race (verdict) is unchanged.

Q: Why does barrier phasing hide it?
A: Barriers align iteration starts but their own synchronization trip
spreads execution — windows smear instead of coinciding.

Q: Volatile Dekker result?
A: 0/20000, every run: volatile store/load edges forbid exactly the
exhibited pair, portably.

Q: Monitor Dekker result, and by which mechanism?
A: 0/20000 by mutual exclusion (pairs serialized under one lock), not
by ordering — no overlap, no anomaly.

Q: Release/acquire Dekker result?
A: Still races: 61-90% anomalies measured. Pairwise chains do not
compose into the total order Dekker needs.

Q: Release/acquire message-passing result (snippet 4)?
A: Chain intact over 50000 (true): one-directional edges suffice for
pairwise handoff — sufficient, not universal.

Q: Tomasulo 1967 in one line?
A: Reservation stations issue when operands are ready, reorder buffer
commits in order (IBM 360/91) — OoO execution invisible to one thread,
visible across threads via shared memory.

Q: ARM vs POWER ordering primitives (qualitative)?
A: ARM64: LDAPR (acquire) / STLR (release) / DMB (full); multi-copy
atomic. POWER: lwsync (lightweight) / sync (full, cumulative);
non-MCA propagation possible.

Q: Rates vs verdicts?
A: Rates (36-90%) vary by machine/cores/power; verdicts (nonzero =
race, zero = ordered) are the portable signal. Assert verdicts.
