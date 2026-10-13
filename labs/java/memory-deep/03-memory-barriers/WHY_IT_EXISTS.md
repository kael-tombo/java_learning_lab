# Why It Exists: Memory Barriers

## The problem it solves

Labs 01-02 leave two questions adjacent but unjoined: edges order
(contract) and buffers disorder (phenomenon) — but *how* does one
become the other, and what does each unit of order cost? Without the
join, engineers either fence everything (correct, ~10x overpriced
writes) or nothing (fast, Dekker at 61-90%). The barrier taxonomy is
the exchange rate between verdicts and nanoseconds: four cells, three
assemblies, one ladder, two boundaries — the complete pricing desk.

## Why four barriers and not one "fence"

A single fence instruction would force every handoff to pay the
system-wide price (StoreLoad flush per operation) for pairwise needs
(publication chains, sequencing). Decomposing into LoadLoad/LoadStore/
StoreStore/StoreLoad lets the JIT buy per shape: compiler-only pins
where TSO already orders (acquire reads, release stores at ~1.3 ns),
hardware fences only where the table has a hole (volatile stores at
~10 ns). The cookbook's decomposition is an economic instrument, not a
taxonomy exercise — snippet 3's ~8x gap is the money it saves.

## Why the roach motel (and not "Volatile freezes everything")

Beginners imagine synchronization as a wall: nothing crosses either
way. The motel's one-way generosity (drift in, never out) is what makes
one-shot publication cheap — predecessors join the release, successors
join the acquire, and no side pays to hold back traffic that only adds
witnesses. A wall model would fence both directions everywhere (the
over-fencing this lab's ladder disproves); the motel fences exactly
the escape directions. Every safe-publication idiom (volatile
reference, latch graph, DCL in lab 05) is a motel application.

## Why the two boundary exhibits

The accident (plain MP 0/2000, still race) exists to break the equation
"green = correct" with a counted, explained, still-green counterexample
— the cheapest possible disproof of output-based reasoning. RaDekker
(61-90% under release/acquire) exists to break "stronger-sounding =
sufficient" with a counted failure of a real, useful, insufficient
mode. One exhibit attacks testing naivete, the other attacks
vocabulary naivete; together they bound the territory where judgment
(not slogans) operates.

## Why opaque exists (the floor below release)

Not every shared number is a message: progress counters and statistics
need atomicity and eventual delivery with no order at all. Forcing them
through release would buy unneeded pins; leaving them plain risks
tearing and indefinite staleness. Opaque names the bottom rung
honestly (atomic, eventual, unordered) so the cheapest correct choice
is expressible — and so its misuse for publication is visibly a rung
error, not a judgment call.

## The one-sentence version

Barriers exist so that order is purchased per pair, per direction, at
the cheapest fence that closes the shape — with the receipt (ladder
row) itemized and the two most instructive non-purchases (accident,
chains) on display beside it.
