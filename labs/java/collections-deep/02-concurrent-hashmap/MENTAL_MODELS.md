# Mental Models: ConcurrentHashMap

## 1. Slots plus overflow
Think of `java.util.concurrent.ConcurrentHashMap` as numbered slots plus an overflow strategy: lock-striped hash table: buckets (not the map) are the locking unit.
Position first (putVal rejects null key/value with NullPointerException), then resolve the few items that share it.

## 2. Thresholds as tripwires
spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative — each is a tripwire that converts a cheap shape into a
scalable one (sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer). Below the wire, linear scan is fine; above it,
you pay for structure once and save on every later op.

## 3. Views as windows, not photos
`weakly-consistent iterators (never throw CME)` is a window into the live store. Writing through the
window writes the room. Copy when you need a photo.

## 4. Nulls as contract, not accident
counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot. The rule exists so "absent" stays distinguishable from
"present" under the class's concurrency/ordering guarantees.

## 5. Growth cost as rent
writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt); sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer. You pay rent (copies/rotations) rarely and in bulk;
steady-state ops stay cheap. Presizing is paying a year up front.

## 6. The extra gear
TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap. That detail is what separates a passing interview answer
from one that matches `java.util.concurrent.ConcurrentHashMap`.
- Lab note (02-concurrent-hashmap/MENTAL_MODELS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/MENTAL_MODELS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/MENTAL_MODELS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/MENTAL_MODELS.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
