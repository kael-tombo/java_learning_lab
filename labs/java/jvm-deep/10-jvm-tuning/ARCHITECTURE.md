# Architecture: JVM Tuning

## Ergonomics as input function

~1000 flags take defaults from detected RAM and CPU counts (cgroup limits
inside containers, not host RAM). `PrintFlagsFinal` is the readout of
that function on your machine: `InitialHeapSize` RAM/64, `MaxHeapSize`
RAM/4, worker counts from cores. The command line overrides exactly
(`-Xmx256m` lands on 268,435,456) — ergonomics propose, flags dispose.

## Generational geometry

`NewRatio=2` splits heap old:young 2:1 (young is one third). Within young,
`SurvivorRatio=8` splits Eden:single-survivor 8:1 (each survivor one tenth
of young). `TargetSurvivorRatio=50` sets desired survivor occupancy after
each young GC; tenuring thresholds adapt around it. These ratios govern
Parallel/Serial layouts directly; G1 translates them into starting
young-region counts then adapts per pause history; ZGC ignores them
structurally (no fixed young).

## Allocation fast path

TLABs give each thread a private Eden slice (~1% each, `TLABSize=0` means
ergonomic sizing, `MinTLABSize=2048` floor): allocation is a pointer bump
of ~10 instructions, no lock. Only TLAB refill takes the shared Eden
lock. Disabling (`-XX:-UseTLAB`) forces atomic allocation on the shared
top — the ~8x measured gap — and exists for diagnosis only.

## Reference compression

Under 32 GB heaps, `UseCompressedOops` plus `UseCompressedClassPointers`
store 64-bit references as shifted 32-bit offsets, halving reference
footprint. Headers shrink 16 to 12 bytes (8 mark + 4 klass). Past ~32 GB
the offsets cannot address the heap and compression switches off — the
threshold behind every per-object size claim in the collections labs.

## Separate capacity planes

Heap (object storage, `-Xmx`), code cache (240 MB, JIT native code —
exhaustion silently stops compilation), Metaspace (class metadata, ~21M
first-trigger, unlimited max, 1 GB compressed class space). Pressure in
one plane never explains growth in another; each has its own MXBeans and
graphs (CodeHeap pools, Metaspace pool, heap pools).

## Large pages posture

`UseLargePages=false` default: 4 KB pages. Enabling needs OS huge-page
pool plus privilege; on an unconfigured OS the flag is silently inert or
fails fast. Benefit (fewer TLB misses on big heaps) versus granularity
waste (2 MB rounding on small heaps) decides per deployment.
