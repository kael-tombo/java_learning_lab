# Performance: ConcurrentHashMap

## Hot-path costs (`java.util.concurrent.ConcurrentHashMap`)
| Op | Cost | Notes |
|----|------|-------|
| lookup | O(1) hash / O(n/2) linked walk / O(log n) tree | per putVal rejects null key/value with NullPointerException |
| insert | O(1) amortized / O(log n) tree | plus sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer |
| remove | same as insert | slot hygiene: TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap |
| iteration | O(n) | weakly-consistent iterators (never throw CME) |

## Constants that dominate
- writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt): first-touch allocation or default sizing decides L1/cache behavior.
- spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative: threshold crossings are the latency spikes in profiles.
- Pointer chasing (linked/tree) vs contiguous scan (array): contiguous wins
  per element by ~4-16x in cache misses even at equal big-O.

## Sizing guidance
- Known n up front: presize once (initialCapacity / ensureCapacity / sizeCtl
  equivalent) to skip the geometric copy series (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer).
- Unknown n: accept amortized growth; call trimToSize/compact only after load.

## Concurrency cost
- volatile tabAt/casTabAt reads; Node.val/next volatile. Contended bucket/cell updates serialize; uncontended paths
  stay CAS-only or lock-free — see THEORY.md for the exact split.

## What to measure
- JMH put/get/remove at n = 10 / 10K / 1M; report p99, not just mean.
- GC logs during bulk load separate copy cost from collection pauses.
- Lab note (02-concurrent-hashmap/PERFORMANCE.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/PERFORMANCE.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
