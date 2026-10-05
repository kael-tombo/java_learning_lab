# VISION — Off-Heap Memory & Direct Buffers

## Vision Statement
**Escape the heap when the heap is the problem** — direct buffers,
mmap, and the FFM API trade GC freedom for manual lifecycle: own
every byte, free every byte, prove every leak with NMT + JFR.

---
## Mental Models
### 1. Direct ≠ Free
`allocateDirect` lives outside GC reach; cleaner frees it late or
never if you slice/dupe carelessly. NMT + `BufferPoolMXBean` count it.
### 2. Arena = Lifetime
FFM `Arena.ofConfined/Shared/Auto` binds native memory to a scope —
close the arena, free the bytes. Same discipline as structured concurrency.
### 3. Zero-Copy Has Edges
mmap + `FileChannel` + direct move GBs without heap churn, but page
faults, `mlock` limits, and unmapping (`Cleaner`) bite at 2 a.m.
### 4. Unsafe Is Debt
`Unsafe`/`VarHandle` off-heap hacks are fast and unportable. Prefer
FFM (`MemorySegment`) unless a benchmark forces otherwise.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Large cached blobs? | Direct/mmap + size cap + eviction |
| Native interop? | FFM Arena + Segment, never raw long addr |
| Small short-lived? | Stay on-heap (escape will save you) |
| Leak suspect? | NMT diff + DirectBufferStatistics first |

---
## Career Trajectory
- **L1:** Direct vs heap buffers, Cleaner basics, NMT reading.
- **L2:** mmap files, pooling, BufferPoolMXBean monitoring.
- **L3:** FFM segments/arenas, zero-copy pipelines, leak forensics.
- **L4:** Off-heap cache/storage architecture with capacity math.

---
## 4-Week Path
```
W1: Direct-buffer kata — alloc/free, slice hazards, NMT proof.
W2: mmap log/image pipeline with pooled buffers.
W3: FFM Arena port — native struct read/write + scope tests.
W4: Off-heap tile/image cache with eviction + leak soak.
```
## Success Metrics
- [ ] NMT direct delta explained to the byte for one workload
- [ ] FFM arena closes with zero residual (test-proven)
- [ ] 24h soak: direct flat, no Cleaner backlog
- [ ] Zero-copy path 3x less alloc with JFR proof

## What This Is Not
"Off-heap = faster." It is GC-pressure engineering with manual risk.

> Mantra: **Every native byte has an owner and a funeral.**
