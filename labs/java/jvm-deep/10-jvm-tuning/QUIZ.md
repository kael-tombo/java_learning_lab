# Quiz: JVM Tuning

Real Q&A; numbers measured on JDK 23 (16 GB / 8-CPU reference box).

## 1. What heap do ergonomics derive, and what overrides them?

`InitialHeapSize` RAM/64 (256M here), `MaxHeapSize` RAM/4 (4G here).
Explicit `-Xmx256m` lands exactly on 268435456. Containers derive from
cgroup limits — verify inside the deployment, never on the laptop.

## 2. What geometry do the three ratios define?

`NewRatio=2`: young = 1/3 heap. `SurvivorRatio=8`: Eden 8/10 of young,
each survivor 1/10. `TargetSurvivorRatio=50`: survivors held toward half
full by adaptive tenuring. Parallel/Serial build this directly; G1 starts
here then adapts; ZGC ignores fixed young structurally.

## 3. What is the TLAB result, structurally?

3M small nodes: ~35 ms with TLABs (per-thread bump-pointer, ~10
instructions, no lock) vs ~250-315 ms with `-XX:-UseTLAB` (shared Eden
top, atomic per allocation) — ~8x, asserted >3x. The off-switch is
diagnostic-only; production keeps TLABs unconditionally.

## 4. State the compression and plane numbers.

`UseCompressedOops` + `UseCompressedClassPointers` on (sub-32 GB):
references halved, headers 12 vs 16 bytes. `ReservedCodeCacheSize=240M`
(full stops compilation silently — watch CodeHeap pools).
`MetaspaceSize` ~21M first trigger, `MaxMetaspaceSize` unlimited,
`CompressedClassSpaceSize=1G`. `UseLargePages=false` default.

## 5. Describe the one-flag experiment and both outcomes.

Identical churn under ParallelGC at `-Xmx128m` vs `-Xmx512m`, counting
`Pause Young (` lines in `-Xlog:gc`: smaller heap collects more often
(fixed young fraction = clean lever). Same pair under G1 reads flat —
adaptivity absorbs the lever, which is itself the finding. One variable
changed; both outcomes distinguish mechanisms.

## 6. What is the tuning method, in order?

Objective plus load generator; baseline (`gc*` logs, JFR); mechanism
hypothesis (not "make it faster"); exactly one flag; re-measure. Knob
order: explicit `-Xmx`, collector, pause target — exotic flags last.
Most production JVMs sit within 3 flags of default.

## 7. Where does pressure in each plane surface?

Heap: `gc` pause lines and heap pools. Code cache: CodeHeap-pool
fullness near 240M with throughput drop and no GC signal. Metaspace:
Metaspace-pool growth with metadata-GC causes. Raising `-Xmx` for a
non-heap plane wastes memory and hides the real graph.

## 8. What fails when large pages or explicit GC are mishandled?

Large pages without OS pool/privilege: silently inert (or fast failure);
small heaps waste memory at 2 MB granularity. Unrestricted `System.gc()`:
caller-triggered full STW spikes — gate with `DisableExplicitGC` where
untrusted paths exist.
