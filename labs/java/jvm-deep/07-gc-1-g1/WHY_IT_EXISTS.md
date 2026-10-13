# Why It Exists: G1 GC

Fixed young/old splits force one geometry on every workload: size the
young for throughput and old pauses spike, or size for pauses and
throughput sags. Heaps kept growing past what a single full collection
could pause for, and humongous objects in old collectors promoted
prematurely or fragmented permanently.

G1 answers by cutting the heap into uniform regions and letting roles
float. The young set becomes a per-pause decision rather than a startup
geometry: each evacuation picks as many Eden/Survivor regions as the
pause model affords. Old regions are reclaimed incrementally by mixed
collections ordered garbage-first, so the worst regions die first and
fragmentation pressure stays bounded without a full compact.

Concurrent SATB marking supplies the liveness data that makes partial
old collection sound — no full scan, no missed cross-region edge, thanks
to remembered sets maintained by refinement threads. Humongous regions
give oversized objects a home that bypasses copying they would never
survive, at the cost of making humongous churn the new pathology.

The 200 ms pause value is part of the same bargain: instead of promising
maximum throughput, G1 promises to *try* to fit each pause into a stated
budget and to adapt young sizing when history says otherwise. Predictable
pauses for region-organized heaps is the design center; absolute
minimum pause belongs to the concurrent-evacuation collectors of labs
08-09, which pay a permanent barrier tax G1 avoids.

Without floating roles the design collapses back to fixed geometry: a
full young would need a full-heap scan to reclaim, and humongous objects
would promote through copying they cannot survive. Fluid regions plus
remembered sets are what let each pause cover exactly the regions worth
covering — the garbage-first policy made executable rather than merely
aspirational.

The SATB choice carries the same bargain upward: one cycle of floating
garbage is the standing price of never missing a live object, and the
remembered-set refinement threads are the standing price of never scanning
the whole heap per pause. Both prices read as background CPU and one-cycle
retention rather than pause time — the shape of throughput traded for
predictability that defines the collector.
