# Security: HashMap Internals

## Threat 1: Hash flooding (hash-based paths)
- Attack: adversary crafts keys colliding in low bits, forcing O(n) chains.
- Mitigation in JDK: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64 — treeify converts the bin to O(log n);
  spreader `h ^ (h >>> 16)` folds high bits down denies the trivial high-bit-only attack.
- Your duty: never accept untrusted keys into an un-treeified custom table.

## Threat 2: Ordering oracles (sorted paths)
- Attack: probing `ceiling/floor` or iteration timing to infer nearby keys.
- Mitigation: TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties; bound views so untrusted callers cannot escape
  their range.

## Threat 3: Concurrent mutation races
- Risk: fail-fast via modCount, ConcurrentModificationException. Lost updates or torn reads become integrity bugs when
  the map guards auth state.
- Fix: confine or use the concurrent variant; never rely on fail-fast as
  a security gate (it is best-effort).

## Threat 4: Memory exhaustion via presizing
- Attack: untrusted `initialCapacity` triggers huge allocation (default capacity 16, load factor 0.75).
- Fix: clamp caller-supplied capacities; prefer lazy default + bounded growth.

## Threat 5: Null-confusion
- Risk: null key allowed once, hash 0, bucket 0. Code that treats "null value" as "absent" bypasses checks.
- Fix: use `containsKey` / `getOrDefault` explicitly, never null inference.
- Lab note (01-hashmap-internals/SECURITY.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/SECURITY.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/SECURITY.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/SECURITY.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
