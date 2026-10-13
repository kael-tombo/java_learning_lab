# History: ZGC

Confident facts only; JEP numbers verified against the primary trail.

## JEP 333 — Experimental ZGC (JDK 11)

ZGC arrived as an experimental collector: colored pointers, load
barriers, and fully concurrent marking plus relocation with
sub-millisecond STW handshakes. Single-generation whole-heap cycles;
opt-in behind `-XX:+UseZGC` on supported platforms.

## JEP 377 — Production ZGC (JDK 15)

Production status without changing the architecture: same barrier and
color core, hardened and supported. The opt-in flag and the pause
character (handshakes, never heap walks) carry through unchanged.

## What the MXBean split records

The four-collector surface (Minor/Major x Cycles/Pauses) plus the two
pools is itself history: it mirrors the generational routing JEP 439
added. Pre-generational ZGC logs show whole-heap cycles without the
young/old distinction — the `y`/`Y`/`O` prefixes and the pool pair are
the visible fossils of the generational split in every current log.

## JEP 439 — Generational ZGC (JDK 21)

Generational mode split young and old: minors reclaim the young set
(where most garbage is), majors coordinate young plus old phases. The
MXBean surface grew into the measured four collectors (`ZGC Minor/Major
Cycles`, `ZGC Minor/Major Pauses`) and two pools (`ZGC Young/Old
Generation`). Default on the JDK 23 measured here (`ZGenerational=true`);
`-XX:-ZGenerational` restores single-generation behavior.

## JEP 220 context

JEP 220 (modular run-time images, JDK 9) predates the ZGC trail and
shares no mechanism with it; it matters only as release-train background
for readers placing JDK 11/15/21 on one timeline.

## Stable core across the trail

Colored pointers plus load barriers never changed role: metadata in the
reference, healing on load, relocation without rendezvous. What changed
is cycle routing (single versus generational) and production status —
the STW story (microsecond handshakes at phase boundaries) held from JEP
333 to the 0.010-0.026 ms measurements in this lab.
