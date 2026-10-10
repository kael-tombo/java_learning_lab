# Internals: Your Table vs the JDK's

## Your table (this lab)

- Single `Entry[]` with inline state flags; linear probe `(i+1) & (n-1)`
  (mask works because n is a power of two — no `%` needed).
- `hash(k) = h ^ (h >>> 16)`, copied from `HashMap.hash` — same spread,
  different use (index mask instead of bucket select + tree compare).
- Tombstone deletion; `(size + tombstones)` load accounting; doubling
  resize that recounts `size`.

## java.util.HashMap (separate chaining + trees)

File: `src/java.base/share/classes/java/util/HashMap.java`.

- Buckets are `Node` chains; bin length ≥ 8 with table ≥ 64 treeifies to
  `TreeNode` (red-black), degrading collide-all-cases to O(log n).
- Same `hash()` spread and `h & (n-1)` index — then chains instead of
  probing. Deletion unlinks locally: no tombstones, no probe chains to
  protect.
- Load 0.75, growth ×2, `threshold = (int)(cap * load)`. Null key allowed
  (hash 0, bucket 0).

## java.util.IdentityHashMap (closest JDK cousin)

File: `src/java.base/share/classes/java/util/IdentityHashMap.java`.

- Open addressing with linear probing — the JDK's proof this lab's design
  ships: `nextKeyIndex` probes `(i+1) & (len-1)`, deletion does
  **backward-shift** (walks subsequent entries back into the hole) instead
  of tombstones, and `==` replaces `equals`.
- Study its `closeDeletion` method as the tombstone-free alternative your
  lab chose not to implement.

## Probe arithmetic

With mask indexing, `(i + 1) & (n - 1)` wraps without division. Quadratic
(`i + i²/2`) and double-hashing variants change only the step function —
the tombstone and resize machinery is identical.
