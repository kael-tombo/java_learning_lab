# Flashcards: Memory Barriers

Q: Name the four barrier types and what each forbids.
A: LoadLoad (load passing load); LoadStore (store passing load);
StoreStore (store passing store); StoreLoad (load passing store) —
the JSR-133 cookbook taxonomy.

Q: Assemble acquire, release, and SC from the four.
A: Acquire = LoadLoad + LoadStore AFTER the op. Release = LoadStore +
StoreStore BEFORE it. SC adds StoreLoad AFTER each volatile store.

Q: Which barrier is the expensive one on x86, and why?
A: StoreLoad: the only one needing a hardware fence on TSO (XCHG with
lock prefix, ~10 ns) — the Dekker fence, paid per volatile store.

Q: State the roach-motel rule in one sentence.
A: Plain ops drift INTO sync regions, never OUT: acquire pins
successors (predecessors may enter from above); release pins
predecessors (successors may enter from below).

Q: Why is publication (data before flag) safe under the motel?
A: Release keeps preceding plain stores before the flag publish; the
acquiring reader then sees the ordered prefix — check in, never out.

Q: Measured x86 ladder (this lab)?
A: Plain stores ~1 ns; release (lazySet) ~1.3-1.4 ns rock-stable;
volatile stores ~10-18 ns; volatile reads ~1.3 ns vs plain ~1 ns
(nearly free). Ratios port; absolutes do not.

Q: lazySet vs set: same or different guarantees?
A: Different: lazySet (release) orders publication pairs only;
set (volatile) adds the StoreLoad total-order step. ~8x price gap on
x86 for the skipped fence.

Q: Plain message-passing 0/2000 on x86 — verdict?
A: Still a data race: StoreStore is preserved on TSO (accident), the
compiler may hoist the read, ARM may reorder the stores. Green output,
no guarantee.

Q: Release/acquire Dekker result?
A: Races at 61-90% anomalies: pairwise chains (my-release to
your-acquire) do not compose into the total order Dekker needs. Only
StoreLoad both sides (volatile) or exclusion (lock) closes it.

Q: What does opaque (getOpaque/setOpaque) guarantee?
A: Atomic access + eventual visibility + ZERO ordering edges. Counters
and statistics only — never publication, never guarding flags.

Q: Fence counts across plain/release/volatile on x86?
A: 0/0/1 — the structural reason the ladder has exactly one big step,
and why release Dekker compiles to the same MOVs as plain.

Q: ARM64 vs x86 pricing (qualitative)?
A: Same taxonomy, different price list: STLR (release) cheaper than
DMB-fenced stores; LDAPR (acquire) cheap like x86 reads. Verdicts
identical, machine code differs.

Q: What must println output be, and why?
A: Pure ASCII: non-ASCII in console output breaks the harness decoding
(prose files may be UTF-8; program output must not be).

Q: When is release/acquire the RIGHT choice?
A: One-directional handoff chains (sequencing, pipelines — lab 02's
50000-intact chain): pairwise ordering suffices, ~8x cheaper per
store than SC.
