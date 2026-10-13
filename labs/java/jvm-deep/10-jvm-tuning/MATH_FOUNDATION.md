# Math Foundation: JVM Tuning

Defensible content only; numbers measured on JDK 23 (16 GB / 8-CPU).

## Ergonomic equations

`Initial = RAM/64`: 16 GiB / 64 = 256 MiB exactly. `Max = RAM/4`: 16 / 4
= 4 GiB exactly. Tolerance form: `|init - phys/64| < phys/64` and `|max -
phys/4| < phys/8` (container rounding absorbed). Exactness form: `-Xmx256m`
implies `MaxHeapSize == 256 * 1048576 == 268435456` with zero tolerance.

## Generational partition

Heap H, NewRatio 2: young = H/3, old = 2H/3. SurvivorRatio 8 within young
Y: Eden = 8Y/10, each survivor = Y/10. At H = 3 GB: young 1 GB, Eden 800
MB, survivors 100 MB each. TargetSurvivorRatio 50: post-GC survivor fill
aims at 50 MB per 100 MB space; tenuring threshold moves to hold it.

## TLAB contention arithmetic

3M allocations at ~35 ms TLAB vs ~280 ms shared: per-allocation ~12 ns vs
~93 ns, delta ~80 ns of atomic/lock overhead each. Throughput ratio ~8x;
lab asserts >3x (2.6x safety under the observation). Scaling: delta grows
with thread count on the shared path (CAS retries), stays flat on TLABs.

## Compression savings

Reference array of N entries: 8N bytes uncompressed vs 4N compressed,
saving 4N (1M-entry table saves 4 MB). Object with two references: header
16 + 16 = 32 bytes uncompressed vs 12 + 8 = 20 bytes compressed (~38%
smaller). Cliff: heaps just over ~32 GB pay the uncompressed layout for
marginal extra capacity — worst bytes-per-GB in the sizing space.

## Code cache exhaustion rate

240 MB ceiling against steady compiled-code residency R plus churn C per
deploy: headroom = 240 - R MB absorbs C until full, then compilation
stops and interpreted fallback steps throughput down with no GC signal.
The instrument is CodeHeap-pool fullness percentage, not any pause line.

## One-flag inference logic

ParallelGC counts: small-heap pauses S, big-heap pauses B, prediction S >
B with all else equal. Observation S > B confirms the fixed-fraction
mechanism; S ~= B under G1 confirms adaptivity absorbing the lever. Both
outcomes are findings because the prediction was registered before the
run — the experiment cannot fail, only distinguish mechanisms.
