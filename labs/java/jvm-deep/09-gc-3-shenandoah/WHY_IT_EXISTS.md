# Why It Exists: Shenandoah GC

G1 and CMS mark concurrently but always stop the world to move objects
[JEP 189: "G1 does some parallel and concurrent work, but it does not do
concurrent evacuation"]. Evacuation pauses therefore grow with live bytes
moved — milliseconds in this module's G1 measurements [measured]. Heaps
kept growing; pausing to copy was the remaining size-dependent term.

Shenandoah removes that term with concurrent evacuation [JEP]: movers
copy while the application runs, coordinated through the Brooks
forwarder, leaving only root-scan handshakes on the pause path. Pauses
become root-sized like ZGC's, by a different mechanism (per-object word
versus in-reference bits) with a different tax shape (read indirection
versus per-load barrier).

Pacing exists for the same race ZGC's headroom answers [JEP]:
evacuation must outrun allocation, so `ShenandoahPacing` throttles
allocators against concurrent progress instead of stalling them late.
Uncommit (`ShenandoahUncommit`, 5-minute delay) returns idle regions to
the OS [JEP] because a collector that never stops the world should also
never hoard memory it no longer touches.

Generational mode follows the industry-wide convergence [JEP 404/521]:
most garbage dies young in every collector studied, so minors for the
young gen keep full-heap evacuations rare. Single-generation stays
default per JEP 521 while the generational path productizes — continuity
first, optimization opt-in.

The pacing and uncommit mechanisms complete the picture [JEP]: pacing
keeps the concurrent machinery ahead of producers without late stalls,
and uncommit keeps the headroom the design needs from becoming permanent
resident memory on idle services. Evacuation concurrency solves the pause
term; pacing plus uncommit solve the throughput and footprint terms that
concurrency introduces — three mechanisms for the three costs of the same
bargain.
