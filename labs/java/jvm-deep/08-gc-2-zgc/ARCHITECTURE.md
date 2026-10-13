# Architecture: ZGC

## Colored pointers

Each reference carries color bits (mark states, remapped flag) alongside
the address. Color is the GC's per-reference metadata: it records which
view of the object the reference holds. Relocation updates the object;
references heal lazily, one load at a time, instead of all at once.

## Load barriers

Every reference load executes a barrier that checks color. A stale ("bad"
color) reference traps into a slow path that forwards it to the current
copy before the application proceeds. The fast path costs a few
instructions per load — always on, the permanent throughput tax — and the
slow path runs only for references that lost a race with a mover.

## Why relocation needs no stop-the-world

Movers copy objects concurrently and leave forwarding state behind.
Application threads that touch a moved object either see the new copy or
heal through the barrier on next load. No phase ever needs to find and
fix all references simultaneously, so the STW beats shrink to handshakes
at mark/relocate boundaries (measured tens of microseconds).

## Generational split (default, measured true)

Young generation absorbs allocation churn through minor collections;
old generation holds survivors through majors. Minors log as `Minor
Collection (High Usage)` / `(Allocation Rate)` / `(Timer)`; majors
interleave `Y:` and `O:` phase lines. `-XX:-ZGenerational` restores the
original single-generation whole-heap cycle.

## Triggers

Allocation rate predicts exhaustion, high usage marks occupancy, warmup
commissions the first major at startup, and `ZCollectionInterval` (default
0 = off) fires periodic majors independent of allocation. Store barriers
on old-to-young references keep young liveness sound without disturbing
the load-healing core.

## Headroom constraint

Concurrent relocation must outrun allocation. Sustained allocation past
the concurrent budget stalls mutators — the one pause-equivalent in an
otherwise size-independent design, and the reason ZGC wants heap
headroom rather than tight sizing.
