# History: Memory Barriers

## JSR-133 cookbook: the taxonomy's birthplace

Doug Lea's *JSR-133 Cookbook for Compiler Writers* (written for the
Java 5 memory-model rollout, Manson/Pugh/Goetz era, 2004) gave compiler
authors the four-barrier vocabulary — LoadLoad, LoadStore, StoreStore,
StoreLoad — and the lowering table from each hb edge to each platform's
fences. Every barrier sentence in this track descends from that
document: acquire/release assembly, roach-motel movement, and the SC
StoreLoad step are cookbook content, quoted ever since.

## SPARC TSO heritage and the one-hole table

Sun's SPARC specified Total Store Order with exactly StoreLoad free,
plus explicit MEMBAR fences for the rest. The cookbook inherited both
the table and the fence-per-pair discipline. Sewell et al. (2010) later
formalized the same shape for x86 (x86-TSO), confirming the
strong-hardware price list this lab measures: everything cheap except
the one fenced pair.

## ARM and POWER: fences as instructions (qualitative)

ARMv8 made acquire/release one-way instructions (`LDAPR`/`STLR`) with
`DMB` as the full fence, and kept multi-copy-atomicity (a write visible
to one core is visible to all). POWER offered `lwsync` (lightweight,
pairwise) vs `sync` (full, cumulative) at the weakest shipping setting,
without multi-copy-atomicity (IRIW-class litmus in the literature).
Java 9's VarHandle modes (`getAcquire`/`setRelease`/`getOpaque`) expose
exactly this hardware menu in portable spelling — the cookbook's pairs
as API.

## lazySet's lineage

`AtomicX.lazySet` (release store, no StoreLoad fence) predates VarHandle
as the JDK's escape hatch for cheap publication chains (queues,
sequencers, Disruptor-style pipelines). Snippet 3's ~1.3 ns
rock-stable measurement is that lineage quantified: compiler-barrier
ordering at plain-adjacent cost, specified, supported, and deliberately
weaker than `set`.

## Opaque: the Java 9 addition

`getOpaque`/`setOpaque` arrived with VarHandle (Java 9, JEP 193):
atomicity plus eventual visibility with no ordering — weaker than
release/acquire, stronger than plain (which additionally permits
tearing and indefinite staleness). Its use is counters and statistics
where any value is fine and order is meaningless; the cookbook has no
row for it because it emits no barrier at all.

## What this lab's numbers owe to history

- The ladder (plain ~1 ns, release ~1.3-1.9 ns, volatile write ~10 ns,
  volatile read ~1.3 ns) is the cookbook's fence-count prediction
  (0/0/1 on x86) rendered in nanoseconds on one machine.
- The 0/2000 accident is the TSO heritage rendered as false comfort
  (StoreStore preserved); the 61-90% RaDekker rate is the cookbook's
  pairwise-vs-total distinction rendered as counted failure.

## Dates to keep straight

- 2004: JSR-133 + cookbook (Lea; Manson/Pugh/Goetz era) — taxonomy,
  roach motel, SC StoreLoad step.
- 2010: Sewell et al. formalize x86-TSO (three pairs preserved).
- 1967 (Tomasulo) belongs to lab 02's execution layer, not to fences.
- Never invent: no other dates, names, or numbers appear in this lab.
