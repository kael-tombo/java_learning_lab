# Performance: JVM Tuning

## Heap sizing posture

`-Xms` = `-Xmx` (fixed heap) removes resize pauses at the cost of
committing the maximum up front — the latency standard. Ergonomic heaps
(RAM/4 max) suit mixed fleets; explicit heaps suit measured services.
In containers verify inside the limits: a 16 GB host with a 1 GB cgroup
sizes from 1 GB, and laptop-derived numbers mislead by 16x.

## Young geometry effects

Larger young (lower NewRatio) stretches time between young pauses and
lengthens each (more live bytes per copy); smaller young does the
reverse. Survivor sizing via SurvivorRatio plus TargetSurvivorRatio 50
controls aging room: undersized survivors promote prematurely (old-gen
pressure, mixed/full work), oversized ones waste Eden. The ParallelGC
128m-vs-512m probe isolates this cleanly because its young fraction is
fixed; G1's adaptivity deliberately muddies it.

## Allocation economics

TLAB path (~35 ms per 3M nodes) versus shared path (~250-315 ms): the
7-9x structural gap means allocation is rarely the bottleneck with
defaults, and pooling small objects usually loses (pool bookkeeping over
an already lock-free path). Pool large/reused buffers (humongous-adjacent,
direct, contended) where lifecycle control — not pointer bumps — is the
win.

## Compression and cache ceilings

Compressed oops halve reference footprint below 32 GB — the cheapest
memory win in the JVM, already on. Code cache 240M is a cliff, not a
slope: full cache ends compilation and steady-state throughput steps
down silently. Metaspace unbounded means leaks grow until the OS objects;
cap it (`MaxMetaspaceSize`) only with a measured headroom number, never
by feel, and alert on its growth rate separately from heap.

## Large pages judgment

Worth enabling for multi-GB heaps on configured hosts (TLB reach matters
when the heap spans millions of 4 KB pages); wasteful for small heaps (2
MB granularity rounds every mapping up). OS pool verification first, flag
second — order reversed is the standard failure.
