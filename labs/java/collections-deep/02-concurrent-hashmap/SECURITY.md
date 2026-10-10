# Security: ConcurrentHashMap

## Threat 1: Hash flooding (hash-based paths)
- Attack: adversary crafts keys colliding in low bits, forcing O(n) chains.
- Mitigation in JDK: spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative — treeify converts the bin to O(log n);
  putVal rejects null key/value with NullPointerException denies the trivial high-bit-only attack.
- Your duty: never accept untrusted keys into an un-treeified custom table.

## Threat 2: Ordering oracles (sorted paths)
- Attack: probing `ceiling/floor` or iteration timing to infer nearby keys.
- Mitigation: TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap; bound views so untrusted callers cannot escape
  their range.

## Threat 3: Concurrent mutation races
- Risk: volatile tabAt/casTabAt reads; Node.val/next volatile. Lost updates or torn reads become integrity bugs when
  the map guards auth state.
- Fix: confine or use the concurrent variant; never rely on fail-fast as
  a security gate (it is best-effort).

## Threat 4: Memory exhaustion via presizing
- Attack: untrusted `initialCapacity` triggers huge allocation (writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt)).
- Fix: clamp caller-supplied capacities; prefer lazy default + bounded growth.

## Threat 5: Null-confusion
- Risk: counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot. Code that treats "null value" as "absent" bypasses checks.
- Fix: use `containsKey` / `getOrDefault` explicitly, never null inference.
- Lab note (02-concurrent-hashmap/SECURITY.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/SECURITY.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/SECURITY.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/SECURITY.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
