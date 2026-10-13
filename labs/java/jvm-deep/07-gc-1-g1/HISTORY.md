# History: G1 GC

Confident facts only.

## Origin and default status

G1 (Garbage-First) shipped as an experimental collector in JDK 7 (update
4 era) for heaps where a single full collection pause had become
unacceptable. JEP 248 made G1 the default collector in JDK 9, replacing
Parallel as the out-of-the-box choice — which is why `UseG1GC` reads true
with no flags on the JDK 23 measured here.

## What JEP 248 changed

The default switch, not the algorithm: region organization, SATB marking,
remembered sets, and mixed collections already existed. JEP 248's
significance is operational — every stock JVM since 9 inherits the
200 ms pause goal and 45% IHOP trigger unless configured otherwise.

## JEP 220 context

JEP 220 (modular run-time images, JDK 9) restructured the JDK delivery
around modules in the same release that defaulted G1. The two are
independent changes sharing a release train; G1's default status does not
derive from modularity, and neither explains the other's numbers.

## Stable surface since

Region sizing (heap/2048, 1-32 MB), the humongous half-region rule, the
young/mixed/full phase structure, and the MXBean names (`G1 Young
Generation`, `G1 Concurrent GC`, `G1 Old Generation`) have been stable
across the versions this module measures. Ergonomic worker counts move
with hardware; the phase names in the logs do not.

## Relation to later collectors

ZGC (JEP 333/377/439) and Shenandoah (JEP 189/379/404/521) kept G1's
concurrent-marking ideas (SATB especially) and replaced its STW
evacuation with concurrent evacuation. G1 remains the throughput-friendly
default; the newer collectors trade barrier tax for size-independent
pauses on top of the same marking foundation.
