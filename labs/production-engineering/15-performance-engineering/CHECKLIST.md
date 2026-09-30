# CHECKLIST: High-Performance Production Readiness
## Lab 15 | Production Engineering Academy

---

## 1. Hardware & CPU Alignment
- [ ] Hot loops operate over contiguous arrays to maximize CPU L1/L2 prefetching.
- [ ] Shared concurrent atomic variables padded to 64 bytes to eliminate False Sharing.
- [ ] Critical polymorphic call sites audited to ensure monomorphic or bimorphic dispatch ($\le 2$ implementations).
- [ ] Branch mispredictions minimized by sorting input data or branch-free algorithms where appropriate.

## 2. Memory & Zero-Allocation Hygiene
- [ ] No object allocations inside hot processing loops (buffers reused or off-heap).
- [ ] Primitive collections (FastUtil / Agrona) used for large primitive numeric maps to avoid `Integer`/`Long` auto-boxing overhead.
- [ ] Netty `ByteBuf` operations audited to prevent buffer leaks (`ReferenceCountUtil.release()`).

## 3. Benchmarking & Verification
- [ ] JMH used for microbenchmarking with warmups and `Blackhole` consumption.
- [ ] CPU cache miss rate verified via `perf stat` ($< 10\%$).
