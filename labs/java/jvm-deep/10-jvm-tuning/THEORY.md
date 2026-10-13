# JVM Tuning — Theoretical Foundation

## Core Concept

Tuning is *measurement-driven flag setting*: the JVM exposes ~1000 flags,
ergonomics choose defaults from RAM/CPU counts, and your job is to (1) read
the actual values off *your* JVM, (2) change one thing, (3) re-measure.
Every number below was read off JDK 23 on a 16 GB / 8-CPU box via
`PrintFlagsFinal` — re-run the queries on your hardware before quoting
them anywhere.

## Heap Sizing Ergonomics (measured)

| Quantity | Value here | Rule |
|---|---|---|
| `InitialHeapSize` | 256 MB | RAM/64 |
| `MaxHeapSize` | 4 GB | RAM/4 (unless `-Xmx`) |
| Explicit `-Xmx256m` | honored exactly (268,435,456) | command line beats ergonomics |

`-Xms` = `-Xmx` (fixed heap) avoids resize pauses and is the standard
production posture for latency work; the cost is committing the full heap
up front. Containers: ergonomics read cgroup limits (when the JDK detects
them), not host RAM — a "16 GB default" box with a 1 GB container limit
sizes from 1 GB. Verify inside the deployment, not on your laptop.

## Generational Ratios (measured defaults)

- `NewRatio = 2` → old : young = 2:1 (young is 1/3 of heap).
- `SurvivorRatio = 8` → Eden : one-survivor = 8:1 (each survivor is 1/10
  of young). `TargetSurvivorRatio = 50` (% occupancy desired after each
  young GC — tenuring adapts around it).
- These ratios govern the *Parallel/Serial* layout directly; G1 translates
  them into initial young-region counts, then adapts per pause history
  (lab 07); ZGC ignores them structurally (no fixed young).

## TLABs: Why Allocation Is ~10 Instructions

Each thread allocates from its own **Thread-Local Allocation Buffer**
(~1% of Eden each, `TLABSize = 0` = ergonomic sizing, `MinTLABSize` =
2048 bytes floor): bump-the-pointer, no lock. Only TLAB refill takes the
Eden lock. Measured: 3M small objects in ~35 ms with TLABs vs ~250–315 ms
without (`-XX:-UseTLAB`) — a 7–9x tax for shared allocation. Disabling
TLABs exists for diagnosis, never production.

## Compressed Oops (measured on)

`UseCompressedOops` + `UseCompressedClassPointers` default true under 32 GB
heaps: 64-bit references stored as 32-bit offsets (3- or 8-byte shifted
base), halving reference footprint. Turn-off threshold: heaps above ~32 GB
can't address with 32-bit shifted offsets (or explicitly
`-XX:-UseCompressedOops`). Object headers: 12 bytes compressed (8 mark +
4 klass) vs 16 uncompressed — the arithmetic behind every per-object size
claim in the collections labs.

## Code Cache and Metaspace (measured)

- `ReservedCodeCacheSize` = 240 MB: JIT-compiled native code lives here;
  exhaustion stops compilation (code runs interpreted — a silent
  performance cliff; watch `CodeCache` MXBean fullness, not just GC logs).
- `MetaspaceSize` ≈ 21 MB initial trigger for first metadata GC;
  `MaxMetaspaceSize` = unlimited (`18446744073709551615` = 2⁶⁴−1);
  `CompressedClassSpaceSize` = 1 GB reserved for Klass structures.
  Metaspace pressure (classloader leaks, generated-code churn) surfaces as
  metadata GCs, not heap pressure — different graph, different fix (leak
  the loader, not the objects).

## Large Pages (measured off)

`UseLargePages = false` default: standard 4 KB pages. Enabling (with OS
huge-page pool configured: Linux `hugetlbfs`/transparent hugepages, Windows
lock-memory privilege) cuts TLB misses for big heaps — and *wastes* memory
for small ones (2 MB granularity rounds every mapping up). Opt-in with OS
support verified first; the flag alone on an unconfigured OS silently does
nothing (or fails fast depending on version).

## The Tuning Method (the actual lab skill)

1. Establish the objective (p99? throughput? footprint?) and the load
   generator — no objective, no tuning.
2. Baseline with logs (`-Xlog:gc*`, JFR) — pauses, rates, causes.
3. Form a hypothesis naming a mechanism (not "make it faster": "young pauses
   dominate p99; shrink young by lowering NewRatio... " — then test whether
   the mechanism responds).
4. Change ONE flag, re-measure. Two flags = confounded experiment.
5. Prefer fewer knobs: explicit `-Xmx`, right collector, pause target —
   exotic flags last. Most "tuned" JVMs in the wild differ from defaults in
   ≤3 flags.

## Key Invariants

1. Ergonomics derive from the *deployment* environment — measure there.
2. Flags are read off the JVM (`PrintFlagsFinal`), never quoted from memory.
3. One change per experiment; logs before and after.
4. TLABs make uncontended allocation nearly free — protect that path.
5. Compressed oops halve reference footprint below 32 GB; code cache and
   Metaspace are separate capacity planes from the heap.
