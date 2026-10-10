# Mental Models: HashMap Internals

## 1. Slots plus overflow
Think of `java.util.HashMap` as numbered slots plus an overflow strategy: hash table with separate chaining over a Node[] table.
Position first (spreader `h ^ (h >>> 16)` folds high bits down), then resolve the few items that share it.

## 2. Thresholds as tripwires
TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64 — each is a tripwire that converts a cheap shape into a
scalable one (resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0). Below the wire, linear scan is fine; above it,
you pay for structure once and save on every later op.

## 3. Views as windows, not photos
`entrySet().iterator() EntryIterator` is a window into the live store. Writing through the
window writes the room. Copy when you need a photo.

## 4. Nulls as contract, not accident
null key allowed once, hash 0, bucket 0. The rule exists so "absent" stays distinguishable from
"present" under the class's concurrency/ordering guarantees.

## 5. Growth cost as rent
default capacity 16, load factor 0.75; resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0. You pay rent (copies/rotations) rarely and in bulk;
steady-state ops stay cheap. Presizing is paying a year up front.

## 6. The extra gear
TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties. That detail is what separates a passing interview answer
from one that matches `java.util.HashMap`.
- Lab note (01-hashmap-internals/MENTAL_MODELS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/MENTAL_MODELS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/MENTAL_MODELS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/MENTAL_MODELS.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
