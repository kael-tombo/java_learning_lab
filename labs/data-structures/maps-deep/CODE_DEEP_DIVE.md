# CODE_DEEP_DIVE — Maps Deep

## HashMap internals
- `Node<K,V>` fields: hash, key, value, next.
- `putVal`: find bucket, walk chain; if key matches, replace; if tree bin, insert in tree.
- Treeify converts a chain to a red-black bin when bucket length ≥ 8 and cap ≥ 64; if cap < 64 it doubles cap instead.
- Hash spreading: `(h = key.hashCode()) ^ (h >>> 16)` to mix high bits into low.
- `resize()`: allocate new array, walk old, split each node into lo/hi lists by `hash & (oldCap)`.

Pitfall: mutating keys in place breaks invariants; use HashMap with immutable key semantics (prefer Objects.equals/hashCode stable).

## TreeMap internals
- `Entry<K,V>` extends LinkedList? No — entry stores key/value/left/right/parent/color.
- `fixAfterInsertion` = recolor + rotations (like RB insert).
- `keyOrNull`, `Objects.compare` virtual calls for comparator.

Pitfall: a comparator that returns 0 for distinct keys silently drops data.

## LinkedHashMap
- `LinkedHashMap.Entry` extends HashMap.Node with prev/next.
- `afterNodeInsertion` maintains tail; with accessOrder=true, `afterNodeAccess` moves node to tail.

## ConcurrentHashMap
- No global lock; `Node` array with CAS on bin head.
- Tree bins use `TreeBin` wrapper with `find` walking a red-black structure.
- During resize a `ForwardingNode` (hash = −1) marks transferred bins; helpers assist.
- No null keys/values; `putIfAbsent`/`computeIfAbsent` are atomic for the bin.

Pitfall: `size()` is not transactional; use `mappingCount()` for a long count and accept eventual consistency.

## Bloom filter sizing
- guava: `BloomFilter.create(Funnel, expectedInsertions, fpp)`.
- Monitor: after N > expected, FPR rises.

## Iterators
- HashMap/TreeMap/LinkedHashMap: fail-fast.
- ConcurrentHashMap: weakly consistent — they may reflect concurrent updates.

## Debug tips
- Print `getNode` chain length on suspicious latency; a too-small capacity can make bins long.
- Watch `modCount` for CME vs concurrent iteration.
