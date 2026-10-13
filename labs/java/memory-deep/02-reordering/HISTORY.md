# History: Reordering

## 1967: Tomasulo and out-of-order execution

Robert Tomasulo's algorithm for the IBM System/360 Model 91 introduced
reservation stations (issue when operands are ready) plus an in-order
commit buffer. Single-threaded semantics stay exact while independent
operations overlap stalls. Every modern OoO core descends from this
design — and with it, the possibility that other cores observe shared
memory effects out of source order.

## SPARC heritage: Total Store Order

Sun's SPARC architecture specified TSO: loads and stores (except
store-followed-by-load to a different address) appear in order, with
explicit fences for the rest. The vocabulary — StoreLoad as the one
free pair — became the industry's way of describing "strong" hardware.
x86 inherited the shape behaviorally long before it was formalized.

## 2010: x86-TSO formalized (Sewell et al.)

Sewell, Sarkar, Owens, Nardelli, and Myreen gave x86 a precise
memory-model formalization ("x86-TSO"): three pairs preserved, exactly
StoreLoad free. The paper turned folklore ("x86 is strong") into a
table with one hole — and Dekker is the program that falls through
exactly that hole. This lab's pair language comes from that work.

## 2004 (context): JSR-133 already assumed hardware like this

Manson, Pugh, and the JSR-133 group (Java 5) specified the JMM's
volatile and monitor edges to compile to whatever fences each platform
needs — precisely so one Java program is ordered on TSO *and* on weaker
hardware. The contract predates the x86 formalization and covers it.

## ARM and POWER: the weak-model lineage (qualitative)

ARMv8 (with LDAPR/STLR acquire/release and DMB fences;
multi-copy-atomic) and POWER (lwsync/sync; non-multi-copy-atomic
propagation in research litmus like IRIW) represent the weak end: in
principle any pair may reorder, and order is opt-in per instruction.
Java's volatile maps onto these primitives per platform (lab 03's
story) — same source verdicts, different machine code.

## What this lab's numbers owe to history

- The ~79% (and 36%+ across configurations) anomaly rates are what
  TSO-plus-store-buffers predicts for tightly rendezvoused StoreLoad
  pairs: not a bug in any chip, the specified shape of x86.
- The volatile 0/20000 and monitor 0/20000 are what JSR-133 promised in
  2004: edges that order (or serialize) regardless of platform
  weakness. The 61-90% release/acquire Dekker rate is the predicted
  gap between pairwise chains and total order.

## Dates to keep straight

- 1967: Tomasulo OoO (IBM 360/91).
- 2004: JSR-133 (Manson/Pugh/Goetz era) specifies portable edges.
- 2010: Sewell et al. formalize x86-TSO (three pairs preserved,
  StoreLoad free).
- Never invent: no other dates, names, or percentages appear in this
  lab; rates quoted are this lab's own x86 measurements.
