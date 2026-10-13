# Flashcards: JVM Tuning

Q: What are the heap ergonomic rules, and what overrides them?
A: `InitialHeapSize` RAM/64, `MaxHeapSize` RAM/4 (measured 256M/4G at 16
GB); explicit `-Xmx` wins exactly (256m -> 268435456). Containers derive
from cgroup limits, not host RAM.

Q: What geometry do NewRatio/SurvivorRatio/TargetSurvivorRatio define?
A: NewRatio 2: old:young 2:1 (young is 1/3 heap). SurvivorRatio 8:
Eden:single-survivor 8:1. TargetSurvivorRatio 50: desired survivor
occupancy after each young GC; tenuring adapts around it.

Q: What are TLABs, and what is the measured win?
A: Per-thread Eden slices for lock-free bump-pointer allocation
(`TLABSize=0` ergonomic, `MinTLABSize=2048` floor). Measured ~35 ms vs
~250-315 ms for 3M nodes (~8x); `-XX:-UseTLAB` is diagnostic-only.

Q: When are compressed oops on, and what do they save?
A: On under ~32 GB heaps (`UseCompressedOops` + `UseCompressedClassPointers`):
32-bit shifted offsets halve reference footprint; headers 12 vs 16 bytes.
Past ~32 GB compression drops — the sizing cliff.

Q: Name the three capacity planes and their numbers.
A: Heap (`-Xmx`), code cache (`ReservedCodeCacheSize=240M` — full stops
compilation silently), Metaspace (`MetaspaceSize` ~21M first trigger,
`MaxMetaspaceSize` unlimited, `CompressedClassSpaceSize=1G`).

Q: What is the tuning method?
A: Objective + load generator; baseline logs/JFR; mechanism hypothesis;
exactly one flag changed; re-measure. Most fleets sit within 3 flags of
default: explicit `-Xmx`, collector, pause target first.

Q: Why did the heap-size lever read flat under G1?
A: G1 adaptivity absorbs it: young-region counts resize per pause history
toward the pause goal. ParallelGC's fixed young fraction exposes the
lever (smaller heap, more pauses); G1's cruise control hides it.

Q: What is `UseLargePages` default, and what does enabling need?
A: Default false. Needs OS huge-page pool + privilege (Linux hugetlbfs/THP,
Windows lock-memory); without support the flag is silently inert.

Q: Which JEPs frame this lab's era?
A: JEP 220 (modular images, 9) and JEP 248 (G1 default, 9) — independent
changes sharing the release train that modern defaults date from.

Q: What proves allocation contention vs GC pressure?
A: The TLAB on/off delta in staging: a large gap implicates the shared
allocation path (fix: fewer/smaller allocations, reused large buffers),
not the collector. Production keeps TLABs on unconditionally.

Q: What does `-Xms=-Xmx` buy, and what does it cost?
A: Removes resize pauses (fixed heap, standard latency posture); costs
committing the full heap up front.

Q: Where do code-cache and Metaspace pressure surface?
A: CodeHeap-pool fullness (compilation cliff) and Metaspace-pool growth
with metadata-GC causes — never the heap `gc` pause lines. Graph each
plane separately.
