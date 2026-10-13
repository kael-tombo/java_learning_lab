# Why It Matters: Memory Barriers

## It converts ordering taste into ordering arithmetic

"Use volatile here" is advice; "this handoff needs StoreStore before
the flag (release, ~1.3 ns) while that gate needs StoreLoad after both
stores (SC, ~10 ns)" is engineering. The taxonomy plus the ladder lets
every handoff review cite cells and prices instead of preferences —
and lets the resulting diffs (lazySet for chains, volatile for gates,
latch for one-shots) defend themselves with numbers from this lab's
own runs.

## It saves the ~8x that blanket fencing wastes

Write-heavy pipelines sequenced through volatile pay the StoreLoad
flush per step for pairwise needs; the release conversion (snippet 3:
~10 ns to ~1.3 ns rock-stable, lab 02 snippet 4: 50000 intact) keeps
the verdict the shape needs at near-plain cost. At millions of stores
per second the gap is cores, watts, and tail latency — the most common
nine-nanosecond bill in concurrent Java, itemized here for the first
time in the track.

## It kills the two arguments that ship races

"This passed 2000 runs" (snippet 4: accident, still race — StoreStore
luck on TSO, red on ARM) and "we used the stronger mode"
(release/acquire Dekker: 61-90%, chains not systems) are the sentences
behind most reordering incidents. Both die here with counted exhibits,
so the next review can answer each in one line with a snippet number
instead of relitigating the model.

## It makes reads-first design rational on TSO

Acquire's near-freedom (~1.3 ns vs ~1 ns) means guard patterns
(DCL singletons, memoized snapshots, flag-gated data) pay once per
publish and read ordered forever after — the economic shape lab 05's
idiom exploits. Teams that learn the directionality stop rationing
reads (the cheap direction) and start rationing fenced stores (the
taxed one), which is the entire performance art of shared-state design
in one sentence.

## It is the vocabulary labs 04-05 spend

Final-field freeze (lab 04) is a StoreStore-backed publication with a
constructor-scoped release; volatile-DCL (lab 05) is the read-cheap/
write-fenced asymmetry amortized over an application's lifetime. Both
are one-paragraph applications of this lab's card (taxonomy, motel,
ladder, chains-caveat) — without it they read as idioms to memorize,
with it as invoices to verify.

## Portability as the price list changes

ARM64 re-prices every row (STLR vs DMB, LDAPR vs bare loads) while
keeping the taxonomy fixed: code written in cells (acquire here,
release there, SC for the gate) recompiles correctly with new prices;
code written in anecdotes ("plain was fine on x86") recompiles into
failures. Learning barriers now is buying the only part of performance
knowledge that survives the next hardware migration — the structure,
not the nanoseconds.
