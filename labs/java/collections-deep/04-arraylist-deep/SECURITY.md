# Security: ArrayList Deep Dive

## Threat 1: Hash flooding (hash-based paths)
- Attack: adversary crafts keys colliding in low bits, forcing O(n) chains.
- Mitigation in JDK: lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10 — treeify converts the bin to O(log n);
  growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf denies the trivial high-bit-only attack.
- Your duty: never accept untrusted keys into an un-treeified custom table.

## Threat 2: Ordering oracles (sorted paths)
- Attack: probing `ceiling/floor` or iteration timing to infer nearby keys.
- Mitigation: MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves); bound views so untrusted callers cannot escape
  their range.

## Threat 3: Concurrent mutation races
- Risk: unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList. Lost updates or torn reads become integrity bugs when
  the map guards auth state.
- Fix: confine or use the concurrent variant; never rely on fail-fast as
  a security gate (it is best-effort).

## Threat 4: Memory exhaustion via presizing
- Attack: untrusted `initialCapacity` triggers huge allocation (set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it).
- Fix: clamp caller-supplied capacities; prefer lazy default + bounded growth.

## Threat 5: Null-confusion
- Risk: fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks. Code that treats "null value" as "absent" bypasses checks.
- Fix: use `containsKey` / `getOrDefault` explicitly, never null inference.
- Lab note (04-arraylist-deep/SECURITY.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/SECURITY.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/SECURITY.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/SECURITY.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
