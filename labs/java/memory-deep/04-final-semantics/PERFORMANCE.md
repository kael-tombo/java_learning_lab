# Performance: Final Field Semantics

## The freeze costs nothing on the read path

Final reads after publication need no fence, no volatile load, no
monitor. Ordering rides the address dependence (reference load, then
field load through it), which hardware already respects. The lab's 3000
racy rounds run at plain-field speed with a specification guarantee
attached — the cheapest safe publication available.

## Where the cost actually sits

The implementation cost is compile-time: the JIT must not reorder final
stores past constructor end, and on weakly ordered hardware the JVM
emits StoreStore barriers at the freeze. This is a one-time construction
cost, amortized over every later read. There is no per-read tax, unlike
`volatile` (fence per access) or locking (monitor ops per access).

## Finals vs volatile vs locks (publication costs)

| Mechanism | Covers | Per-read cost |
|---|---|---|
| `final` + no escape | initialization only | zero |
| `volatile` reference | initialization + later mutations | fence per access |
| Lock handoff | compound invariants + mutations | monitor ops |
| Holder / enum install | one-time initialization | one-time class-init lock |

Choose finals for state fixed at construction; pay for volatile or locks
only for state that changes afterward.

## The false economy of the mutable twin

Skipping `final` to "save nothing" (there is no per-read cost to save)
buys an unguaranteed program that happens to pass on x86. No benchmark
can convert weather into theorem: the mutable version's 3000 clean
rounds measure this machine today, not the program's semantics. The
final version's identical timing carries a portability guarantee the
stopwatch cannot show.

## Allocation interplay

Defensive copies (fresh arrays, `List.of` snapshots) cost one allocation
per construction. That is the correct place to spend: construction is
rare, reads are frequent. Aliasing caller-owned arrays "saves" the copy
and destroys the transitive guarantee — the most expensive saving in
this lab.

## Guidance

Make shared snapshots immutable with finals and spend ordering budget
only on genuinely mutable state. If profiling shows publication
overhead, the culprit is the volatile/lock layer around mutations, never
the freeze. Do not microbenchmark the freeze itself: its read-path cost
is definitionally zero.
