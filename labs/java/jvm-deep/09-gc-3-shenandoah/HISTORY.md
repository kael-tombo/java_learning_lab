# History: Shenandoah GC

Confident facts only; all JEP numbers from primary sources.

## JEP 189 — Experimental Shenandoah (JDK 12) [JEP]

Flood/Kennke's concurrent-evacuation design entered OpenJDK as
experimental: Brooks forwarding pointer, SATB marking shared with G1,
read plus write barriers, root-sized pauses. The JEP's own contrast line
names the gap: "G1 does some parallel and concurrent work, but it does
not do concurrent evacuation." The PPPJ2016 paper is the algorithm
reference behind the JEP.

## Downstream-first shipping [JEP]

Red Hat shipped Shenandoah in 8u/11u downstream builds before upstream
integration — the uncommon backport-first history recorded in JEP 379's
text. Availability has therefore always been a distribution property,
which the lab's Oracle-build refusal [measured] demonstrates from the
other side.

## JEP 379 — Production Shenandoah (JDK 15) [JEP]

Production status (Shipilёv; cosmetic flag-class change). No
default-collector change — G1 stays default. Promotion without
disruption: existing deployments keep behavior, new adopters opt in.

## JEP 404 / JEP 521 — Generational path [JEP]

JEP 404 integrated generational mode as experimental in 24; JEP 521
tracks its productization. JEP 521's standing line: "By default,
Shenandoah will continue to use a single generation" — generational
(`-XX:+UseGenerationalShenandoah` where shipped) stays opt-in, mirroring
the industry convergence (G1 regions, ZGC `ZGenerational`).

## JEP 220 context

JEP 220 (modular run-time images, JDK 9) is release-train background for
placing 12/15/24 on one timeline; it shares no mechanism with Brooks
pointers or SATB.

## What the probes add [measured]

The primary trail explains what Shenandoah is; the Oracle-build probes
prove where it is not. That negative result (refusal text, single
surviving flag) is the historically honest footnote: a collector can be
production upstream and absent downstream-of-choice simultaneously.
