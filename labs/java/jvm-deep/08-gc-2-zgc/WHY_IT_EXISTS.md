# Why It Exists: ZGC

G1's evacuation stops the world and copies; pause time grows with live
bytes moved (milliseconds in this module's measurements). Services with
tight tail-latency budgets or multi-GB heaps needed pauses decoupled
from heap size — a design where collecting a terabyte costs the same STW
time as collecting a gigabyte.

ZGC buys that decoupling with concurrency plus per-load healing. Marking
and relocation run alongside the application; only root-scan handshakes
stop it. The price moves from pause time to throughput: barriers on
every load plus background copying cost single-digit percent on
allocation-heavy shapes, and relocation must outrun allocation (headroom,
not tight sizing).

Generational mode exists because most objects die young here too:
reclaiming the young set in minors keeps the far more expensive major
work rare. The single-generation whole-heap cycle survives behind
`-XX:-ZGenerational` for comparison and special cases, but the default
measured on JDK 23 splits young and old.

The timer trigger (`ZCollectionInterval`, default off) closes the last
gap: an idle latency-sensitive service accumulates garbage between
requests with no allocation pressure to schedule collection. Periodic
majors keep the heap hygienic so the next burst never pays for the last
one's garbage.

Without generational routing the design would still work but waste its
best property: whole-heap cycles spend old-gen effort on young garbage
every time. Minors concentrate the concurrent machinery where mortality
is highest, so majors stay rare and the throughput tax buys the most
reclamation per barrier executed — effort matched to garbage, not spread
uniformly across the heap.

Single-generation mode survives behind the flag for the workloads that
want it (uniform mortality, whole-heap cadence), but the default reflects
measured reality: most objects die young under every collector studied,
and routing collection effort accordingly is the oldest win in GC design
restated with colored pointers.
