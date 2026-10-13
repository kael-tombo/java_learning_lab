# G1 Garbage Collector — Theoretical Foundation

## Core Concept

G1 (Garbage-First, Java 7; default since 9) divides the heap into
equal-sized **regions** (1–32 MB, ergonomically heap/2048) and collects the
*subset with the most garbage first* — hence the name. Young regions
evacuate in stop-the-world pauses; old regions are reclaimed by concurrent
marking + mixed evacuations; objects over half a region go to dedicated
**humongous** regions. The design goal is *predictable pauses*
(`-XX:MaxGCPauseMillis=200` default) rather than maximum throughput.

## Regions, Roles, and Sizes (measured on JDK 23)

- Region size: `G1HeapRegionSize` ergonomic (here: 2 MB at ~8 GB heap, 1 MB
  at 256 MB; always a power of two, 1–32 MB). Roles are fluid — any region
  can be Eden, Survivor, Old, or Humongous at different times (unlike the
  fixed young/old split of Parallel GC).
- Young set: Eden + Survivors, sized adaptively (`G1NewSizePercent`…bounds;
  young length varies per pause to meet the pause target).
- Humongous threshold: objects ≥ half a region (a 2 MB array at 1 MB
  regions spans 2 contiguous humongous regions — verified in this lab's
  logs). Humongous objects are never evacuated by young GC; reclaimed only
  by concurrent cleanup (or full GC).
- Remembered sets (per-region PRTs): track cross-region references so
  evacuating one region finds its roots without scanning the heap —
  maintained concurrently by refinement threads (`Concurrent Refinement
  Workers` in the init log).

## The Collection Cycle

1. **Young-only phase**: Eden fills → `Pause Young (Normal) (G1 Evacuation
   Pause)` — live objects copy to Survivor/Old regions; entirely STW, the
   dominant pause for most apps (2–5 ms in this lab's measurements at
   256 MB).
2. **Concurrent marking**: past `InitiatingHeapOccupancyPercent=45`, G1
   marks live objects concurrently (SATB snapshot-at-the-beginning:
   buffers record reference mutations during marking so the snapshot stays
   consistent) — `Pause Initial Mark` (piggybacked on a young pause) then
   concurrent phases.
3. **Mixed GCs**: after marking, old regions with the most garbage join
   young pauses (`Pause Young (Mixed)`), a few per cycle until reclaimed.
4. **Full GC**: last resort (humongous fragmentation, metaspace pressure,
   `System.gc()` without `ExplicitGCInvokesConcurrent`) — uses parallel
   workers but is still fully stop-the-world; a healthy G1 log shows none.

## SATB in One Paragraph

Snapshot-At-The-Beginning: when concurrent marking starts, G1 logically
snapshots the object graph; every reference *overwritten* during marking is
logged to a SATB buffer (write barrier on field stores), and buffers are
scanned as extra roots. Deleted objects may be marked live spuriously
(floating garbage — reclaimed next cycle), but no live object is ever
missed. Correctness (no live reclamation) traded against precision (some
dead retained one cycle).

## Pause Target vs Reality

`MaxGCPauseMillis=200` is a *goal*, not a guarantee: G1 sizes each young set
predictively (decay-averaged pause model) to fit recent history into the
budget. Sustained allocation spikes, humongous churn, or to-space exhaustion
blow past it — the log's per-pause `Xms` readings (not the flag) are the
ground truth. Tuning starts with reading pauses, not setting flags.

## Key Flags (measured defaults, JDK 23)

| Flag | Default | Meaning |
|---|---|---|
| `UseG1GC` | true (ergonomic) | default collector |
| `MaxGCPauseMillis` | 200 | pause-time goal |
| `G1HeapRegionSize` | heap/2048, clamped 1–32 MB | region size |
| `InitiatingHeapOccupancyPercent` | 45 | marking trigger (% of heap) |
| `ConcGCThreads` / `ParallelGCThreads` | ergonomic (2/8 here) | concurrent/parallel worker counts |

Read your own with `java -XX:+PrintFlagsFinal -version` before quoting —
ergonomic values move with heap and CPU count.

## Key Invariants

1. Every object lives in exactly one region with exactly one role at a time.
2. Young pauses evacuate survivors; liveness for old regions comes from SATB
   marking, never from a full scan.
3. Humongous objects bypass Eden/Survivor entirely and are never young-GC
   evacuated.
4. The pause target shapes young-set sizing; it never vetoes a needed pause.
5. RSet correctness (no missed cross-region edge) is what makes partial
   evacuation sound.
