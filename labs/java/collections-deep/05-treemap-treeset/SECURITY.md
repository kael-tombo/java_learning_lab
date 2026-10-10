# Security: TreeMap / TreeSet

## Threat 1: Hash flooding (hash-based paths)
- Attack: adversary crafts keys colliding in low bits, forcing O(n) chains.
- Mitigation in JDK: identity is compareTo==0 (or comparator.compare==0), NOT equals() — treeify converts the bin to O(log n);
  color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1) denies the trivial high-bit-only attack.
- Your duty: never accept untrusted keys into an un-treeified custom table.

## Threat 2: Ordering oracles (sorted paths)
- Attack: probing `ceiling/floor` or iteration timing to infer nearby keys.
- Mitigation: floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n); bound views so untrusted callers cannot escape
  their range.

## Threat 3: Concurrent mutation races
- Risk: unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them. Lost updates or torn reads become integrity bugs when
  the map guards auth state.
- Fix: confine or use the concurrent variant; never rely on fail-fast as
  a security gate (it is best-effort).

## Threat 4: Memory exhaustion via presizing
- Attack: untrusted `initialCapacity` triggers huge allocation (iteration ascending via on-the-fly successor links; fail-fast via modCount).
- Fix: clamp caller-supplied capacities; prefer lazy default + bounded growth.

## Threat 5: Null-confusion
- Risk: live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view. Code that treats "null value" as "absent" bypasses checks.
- Fix: use `containsKey` / `getOrDefault` explicitly, never null inference.
- Lab note (05-treemap-treeset/SECURITY.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/SECURITY.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/SECURITY.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/SECURITY.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
