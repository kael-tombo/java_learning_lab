# MINI PROJECT — Off-Heap Memory: Zero-Copy Tile Cache

## Goal (2 weeks, ~8–10h)
Build an image-tile cache serving 256KB tiles from mmap + pooled
direct buffers with an FFM metadata sidecar — flat GC, flat NMT, and
a leak test that would catch a forgotten slice.

## Requirements
### Functional
1. `TileCache.get(id)`: mmap-backed file store (`FileChannel.map`) →
   pooled `ByteBuffer.allocateDirect` handoff; Caffeine-style LRU with
   max-bytes (not count) eviction; direct high-water metric.
2. Pool: fixed direct-buffer pool (power-of-two classes, leak-tracked
   acquire/release with stack on leak); double-release throws.
3. FFM sidecar: tile header (`id,width,height,checksum`) as
   `MemorySegment` in confined `Arena`; checksum via `MemorySegment`
   read — no `Unsafe`.
4. Zero-copy read path: `FileChannel.transferTo` / gathering-write
   option for bulk export; JFR alloc comparison vs heap-copy path.
5. Cleaner discipline: no reliance on GC timing; explicit
   `arena.close()` + pool `release()` in try-with-resources; test
   forces leak (skip release) and detector fires.
6. Eviction proof: fill past cap → oldest evicted, direct usage flat
   at cap ±5%, heap GC pauses unaffected (gc.log excerpt).

### Non-functional
- 14+ tests: pool accounting, double-release, arena-close frees,
  eviction bound, checksum mismatch, concurrent get (32 threads).
- Artifacts: NMT baseline/diff, JFR `DirectBufferStatistics` +
  `ObjectAllocation` excerpts, `BufferPoolMXBean` chart.
- 1h soak script: direct flat, RSS flat, zero leak-detector hits.
- README: byte-ownership map (who allocates/frees each buffer).

## Starter Layout
```
src/main/java/com/lab49/tiles/{TileCache,DirectPool,TileStore,MmapReader}.java
src/test/java/.../{PoolTest,EvictionTest,ArenaTest,LeakTest}.java
scripts/soak.sh  results/{nmt,jfr}
```

## Phases
### Week 1 — Store + Pool (4–5h)
- mmap reader, direct pool with leak tracking, LRU cap.
- Deliverable: cache serves tiles with pool accounting green.
### Week 2 — FFM + Soak (4–5h)
- FFM headers, zero-copy export, soak + NMT proof.
- Deliverable: leak-free soak report with charts.

## Test Plan
- Leak injection: 100 unreleased acquires → detector reports 100
  with allocation stacks.
- Slice hazard: dupe/slice then release parent → test defines the
  (safe) contract explicitly.
- Concurrency: 32-thread get storm, pool count exact, no corruption.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Pool | Tracked + tested | Pooled | allocateDirect per req |
| mmap/zero-copy | Measured alloc win | Used | Heap copies only |
| FFM | Arena-scoped, no Unsafe | Works | Raw addresses |
| Eviction/cap | Byte-cap + flat proof | Count cap | Unbounded |
| Leak proof | NMT + soak + detector | NMT only | No proof |

Pass ≥ 70. Stretch: shared-arena concurrent reader with
`Arena.ofShared`; `MaxDirectMemorySize` breach drill + alert.

## Demo Checklist
- [ ] NMT direct line flat during soak (live)
- [ ] Leak injection → detector stack in seconds
- [ ] Alloc flame: heap-copy path vs zero-copy side by side
- [ ] Eviction: cap hit → oldest gone, usage flat

## Common Traps
Forgetting `Cleaner` lag, slicing without retaining parent, mixing
heap/direct in one pool — all auto-fail.
