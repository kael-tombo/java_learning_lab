# History: JVM Tuning

Confident facts only.

## Ergonomics lineage

Early JVMs required manual heap sizing (`-Xms`/`-Xmx` or accept tiny
fixed defaults). Ergonomics — deriving `InitialHeapSize` (RAM/64) and
`MaxHeapSize` (RAM/4) from detected memory — made stock JVMs reasonable
on unknown hardware without operator input. Container awareness (reading
cgroup limits instead of host RAM where detected) extended the same idea
to orchestrated deployments; the rule "measure inside the deployment"
dates to that split.

## Generational ratios stability

`NewRatio=2`, `SurvivorRatio=8`, `TargetSurvivorRatio=50` have been the
standing generational geometry across the Parallel/Serial era into the
present: young as one third of heap, Eden at eight tenths of young,
survivors held toward half occupancy by adaptive tenuring. G1 kept the
ratios as its starting young-region counts while adding per-pause
adaptivity atop them; ZGC discarded fixed young geometry structurally.

## TLABs and compressed oops

Thread-local allocation buffers removed the shared-Eden lock from the
fast path (the ~8x structural gap this lab measures); `TLABSize=0`
ergonomic with `MinTLABSize=2048` floor is the settled posture.
Compressed oops (plus compressed class pointers) halved reference
footprint for sub-32 GB heaps — the quiet memory win behind every modern
per-object size claim, with the ~32 GB cliff as its permanent boundary.

## JEP 220 context

JEP 220 (modular run-time images, JDK 9) restructured JDK delivery in the
same release train that defaulted G1 (JEP 248) — independent changes
sharing a version number. Neither explains the other's values; both mark
the JDK 9 line after which modern ergonomics, ratios, and defaults in
this lab apply.

## Method over knobs

The durable invention is procedural, not a flag: objective, baseline
logs, mechanism hypothesis, one change, re-measure. Flag names churn per
release; `PrintFlagsFinal` plus the one-variable experiment transfer
across all of them — which is why this lab teaches the query and the
method rather than a flag list.
