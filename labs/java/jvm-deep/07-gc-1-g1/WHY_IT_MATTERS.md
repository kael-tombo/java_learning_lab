# Why It Matters: G1 GC

G1 is the default collector (`UseG1GC` ergonomic true), so its pauses are
your application's pauses unless you opted out. Every service on stock
JDK 23 inherits the 200 ms pause goal, the 45% marking trigger, and the
heap/2048 region geometry — understanding them is operating the default,
not specializing.

The pause target shapes capacity work directly. Young pauses measured
2-5 ms at 256 MB leave two orders of magnitude of headroom under the
goal, which tells you this heap is nowhere near its pause limit; a log
showing 150 ms young pauses on a larger live set tells the opposite
story. The per-pause readings, not the flag, drive the decision to grow
the heap, shrink the young, or split humongous workloads out.

Humongous awareness prevents a specific production failure: caches of
multi-MB arrays on small regions fragment the old set faster than mixed
GCs clean it, and the default info log never names the cause. Knowing to
sample `gc+humongous=debug` turns "old gen grows for no reason" into a
counted list of spanning arrays with sizes.

MXBean names matter for dashboards: pools `G1 Eden Space`/`G1 Survivor
Space`/`G1 Old Gen` and collectors `G1 Young Generation`/`G1 Concurrent
GC`/`G1 Old Generation` are the keys your monitoring joins on. A
dashboard hardcoded to these names goes blind the day the service moves
to ZGC — enumerate collectors instead, as lab 08's probe shows.

Finally the method transfers: pin `-Xmx`, join log tags with `+`, count
pauses before theorizing. Those three habits work on every collector in
this module, and they are cheapest to learn on G1 because its logs are
the most explicit about what each pause did.

The remembered-set lesson transfers furthest: any partial-collection
design stands or falls on finding cross-partition references without
scanning everything. When you later meet card tables, store barriers, or
ZGC's load healing, recognize each as the same completeness problem G1's
PRTs solve — different rendezvous, identical soundness requirement.
