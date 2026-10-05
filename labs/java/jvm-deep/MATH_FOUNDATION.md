# Math Foundation — JVM

## 1. Heap Partition
`heap = eden + 2×survivor + old + humongous`. G1: regions 2048 default; region = heap/2048.

## 2. Alloc Rate
`alloc_MB/s = bytes_mutator / time`. 500MB/s × 10s = 5GB → young GC cadence = eden/rate.

## 3. Pause Budget
`pause% = pause×freq`. 20ms × 5/s = 10% throughput loss. Goal < 1%.

## 4. Amdahl (GC threads)
More ParallelGCThreads helps to N=cores; beyond → contention. `T_gc ≈ serial/N + sync`.

## 5. Thread Stack Math
`stack_total = N × Xss`. 5k × 1MB = 5GB virtual — cap threads or lower Xss (512k).

## 6. Direct + Heap Cap
`heap + direct + metaspace + stacks < container`. 1g+512m+256m+stacks < 2Gi? No — resize.

## 7. Little's Law (queues)
`inflight = λ × W`. λ=2k rps, W=50ms → 100 concurrent; size pools ≥ 2×.

## 8. CodeCache
Default 240MB; full → JIT stops. `usage% = used/240`. Bump `ReservedCodeCacheSize` if > 85%.

## Recap
```
region = heap/2048
pause% = pause·freq
stacks = N·Xss
container ≥ heap+direct+meta
```
Drill: eden 400MB, alloc 200MB/s → young GC every? 2k threads Xss=1MB total?
