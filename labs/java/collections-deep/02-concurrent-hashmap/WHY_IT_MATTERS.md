# Why It Matters: ConcurrentHashMap

## Everyday impact
- Nearly every request path touches `java.util.concurrent.ConcurrentHashMap` (caches, indexes, params, models).
  putVal rejects null key/value with NullPointerException is why those lookups stay flat as data grows.

## Cost impact
- sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer; writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt). One presize decision at startup can remove the only
  latency spikes the structure ever produces.

## Correctness impact
- spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative; counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot. Getting either wrong silently corrupts lookups —
  entries that exist but never match.

## Concurrency impact
- volatile tabAt/casTabAt reads; Node.val/next volatile. Choosing the wrong variant turns a fast map into a race log.

## Interview signal
- Stating putVal rejects null key/value with NullPointerException + spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative + sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer with the numbers (8/6/64,
  0.75/16, 1.5x/2x, RED=false/BLACK=true as applicable) separates recall
  from understanding. Extra credit: TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/WHY_IT_MATTERS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
