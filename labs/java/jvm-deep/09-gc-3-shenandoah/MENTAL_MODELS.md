# Mental Models: Shenandoah GC

## 1. Forwarder as a mail redirect [JEP]

Every object is a resident with a forwarding address card (Brooks word).
Movers relocate the resident and update the card atomically; visitors
(readers) always check the card first. Mail (reads) never arrives at an
empty house — at worst one redirect hop to the new address.

## 2. CAS as one winner per move [JEP]

Several movers may race to copy the same object. The forwarder CAS
elects exactly one winner; losers discard their copies and use the
winner's. Like parallel cooks plating one dish — one plate serves, the
rest are bussed, nobody eats twice or half.

## 3. Pacing as a moving walkway limit [JEP]

`ShenandoahPacing` [JEP] is the walkway that slows foot traffic
(allocation) to the speed of the cleaning crew (evacuation). Without it,
runners outpace cleaners and the corridor jams (allocation stall). The
walkway never stops anyone — it paces them so cleaning finishes ahead.

## 4. SATB as footnotes again [JEP]

Same photograph-with-footnotes as G1: overwritten references during
marking log to SATB buffers and develop as extra roots. Ghosts (floating
garbage) wait one cycle; the living are never cropped. Sharing the
mechanism with G1 is deliberate — one correct snapshot design, two
evacuation strategies atop it.

## 5. Availability as a shipping manifest [measured]

Shenandoah on a given JVM is cargo on a manifest: present on Temurin /
Semeru / RH line items, absent on the Oracle line. The probe reads the
manifest at startup ("not supported" vs `Using Shenandoah`) instead of
assuming every ship carries every crate because the catalog is new.

## 6. Generational default as continuity [JEP]

JEP 521 keeping single-generation default while generational
productizes is the "don't move the furniture" rule: existing deployments
keep their behavior, opt-in workloads trial minors-for-young. Convergence
with G1 regions and ZGC `ZGenerational` happens by choice, not surprise.
