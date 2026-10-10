# Performance: ArrayList Deep Dive

## Hot-path costs (`java.util.ArrayList`)
| Op | Cost | Notes |
|----|------|-------|
| lookup | O(1) hash / O(n/2) linked walk / O(log n) tree | per growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf |
| insert | O(1) amortized / O(log n) tree | plus two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact) |
| remove | same as insert | slot hygiene: MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves) |
| iteration | O(n) | SubList view + fail-fast Itr/ListItr |

## Constants that dominate
- set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it: first-touch allocation or default sizing decides L1/cache behavior.
- lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10: threshold crossings are the latency spikes in profiles.
- Pointer chasing (linked/tree) vs contiguous scan (array): contiguous wins
  per element by ~4-16x in cache misses even at equal big-O.

## Sizing guidance
- Known n up front: presize once (initialCapacity / ensureCapacity / sizeCtl
  equivalent) to skip the geometric copy series (two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact)).
- Unknown n: accept amortized growth; call trimToSize/compact only after load.

## Concurrency cost
- unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList. Contended bucket/cell updates serialize; uncontended paths
  stay CAS-only or lock-free — see THEORY.md for the exact split.

## What to measure
- JMH put/get/remove at n = 10 / 10K / 1M; report p99, not just mean.
- GC logs during bulk load separate copy cost from collection pauses.
- Lab note (04-arraylist-deep/PERFORMANCE.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/PERFORMANCE.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
