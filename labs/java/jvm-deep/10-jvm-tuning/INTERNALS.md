# Internals: JVM Tuning

## Heap ergonomic equations

`InitialHeapSize = RAM/64`, `MaxHeapSize = RAM/4` (measured 256M/4G at
16 GB, wide tolerances for container rounding). Both derive per launch
from detected memory; `-Xmx`/`-Xms` replace the derivation exactly. The
`HeapErgo` probe asserts ratios plus exactness together so neither half
of the contract goes unverified.

## Ratio arithmetic

`NewRatio=2`: young = heap/3, old = 2*heap/3. `SurvivorRatio=8`: each
survivor = young/10, Eden = 8*young/10. `TargetSurvivorRatio=50`: after
each young GC the JVM retunes tenuring so survivors sit half full —
overfull survivors promote faster (raise effective threshold pressure),
underfull ones let objects age longer. Read the three flags as one
coupled geometry, not three independent knobs.

## TLAB sizing

`TLABSize=0` means ergonomic per-thread sizing (~Eden/threads with waste
heuristics); `MinTLABSize=2048` floors tiny-thread waste. Refill takes
the Eden lock; allocation between refills is lock-free. The 7-9x measured
tax for `-XX:-UseTLAB` is contention plus atomic overhead per object,
which is why disabling is diagnostic-only — no production shape benefits.

## Compressed oops mechanics

Base-plus-shift decoding: stored 32-bit offset, 3- or 8-byte shift,
added to the heap base on load. Zero-based compressed oops skip the base
add when the heap sits low. Above ~32 GB the shifted 32-bit range cannot
span the heap and the JVM drops compression (headers grow, references
double) — the cliff behind "don't size just over 32 GB" guidance.

## Code cache and Metaspace numbers

`ReservedCodeCacheSize` 251658240 bytes (240 MB): compiled code plus
dependencies; full cache stops compilation (interpreted fallback, silent
performance cliff — watch CodeHeap MXBean fullness). `MetaspaceSize`
~21M: first metadata-GC threshold, not a cap. `MaxMetaspaceSize`
2^64-1: unlimited. `CompressedClassSpaceSize` 1073741824 (1 GB): Klass
structures reservation. Three numbers, three planes, three graphs.

## Large pages reality

`UseLargePages=false` default. When enabled with OS support (Linux
hugetlbfs/THP pool, Windows lock-memory privilege), large pages cut TLB
misses for big heaps. Without OS support the flag does nothing observable
(or fails fast by version) — verify huge-page pools before attributing
any change to it.
