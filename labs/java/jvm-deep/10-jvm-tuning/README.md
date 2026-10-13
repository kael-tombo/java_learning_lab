# README — JVM Tuning

Tuning is measurement-driven flag setting: read values off your JVM,
change one thing, re-measure. Every number below was read off JDK 23 on
a 16 GB / 8-CPU box — re-run the queries on your hardware before quoting.

## What you will observe [measured]

- `InitialHeapSize` 256M (RAM/64), `MaxHeapSize` 4G (RAM/4); explicit
  `-Xmx256m` honored exactly (268,435,456 bytes).
- `NewRatio=2` (old:young 2:1), `SurvivorRatio=8` (Eden:survivor 8:1),
  `TargetSurvivorRatio=50`; `TLABSize=0` ergonomic, `MinTLABSize=2048`.
- 3M small objects in ~35 ms with TLABs vs ~250-315 ms without
  (`-XX:-UseTLAB` diagnostic-only): ~8x structural gap, asserted >3x.
- `UseCompressedOops` + `UseCompressedClassPointers` on;
  `ReservedCodeCacheSize=240M`, `CompressedClassSpaceSize=1G`,
  `MetaspaceSize` ~21M, `MaxMetaspaceSize` unlimited, `UseLargePages=false`.
- One-flag experiment: ParallelGC young-pause counts fall as `-Xmx` grows
  (128m vs 512m); with G1 the same experiment reads flat because adaptive
  young-sizing absorbs the lever.

## Method (the actual skill)

Objective plus load generator first; baseline with `gc*` logs and JFR;
hypothesis naming a mechanism; exactly one flag changed; re-measure.
Most production JVMs differ from defaults in at most 3 flags — prefer
explicit `-Xmx`, right collector, pause target; exotic flags last.

## Exit criteria

You can derive heap defaults from RAM, explain the TLAB win structurally
(lock-free bump-pointer vs shared Eden lock), separate the three capacity
planes (heap, code cache, Metaspace), and run a one-variable experiment.

## Numbers pocket reference

Heap: RAM/64 initial, RAM/4 max, `-Xmx` exact. Ratios: NewRatio 2,
SurvivorRatio 8, TargetSurvivorRatio 50. TLAB: size 0 ergonomic, min 2048,
~8x win. Compression on sub-32G. CodeCache 240M, ClassSpace 1G, Metaspace
~21M first-trigger unlimited max. LargePages off. One flag per trial.
