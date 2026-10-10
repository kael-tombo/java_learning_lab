# Security: LinkedList Deep Dive

## Threat 1: Hash flooding (hash-based paths)
- Attack: adversary crafts keys colliding in low bits, forcing O(n) chains.
- Mitigation in JDK: Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs) — treeify converts the bin to O(log n);
  node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last denies the trivial high-bit-only attack.
- Your duty: never accept untrusted keys into an un-treeified custom table.

## Threat 2: Ordering oracles (sorted paths)
- Attack: probing `ceiling/floor` or iteration timing to infer nearby keys.
- Mitigation: doubly-linked symmetry: node.next.prev == node.prev.next == node; bound views so untrusted callers cannot escape
  their range.

## Threat 3: Concurrent mutation races
- Risk: unsynchronized; structural change must flow through link/unlink (size+modCount). Lost updates or torn reads become integrity bugs when
  the map guards auth state.
- Fix: confine or use the concurrent variant; never rely on fail-fast as
  a security gate (it is best-effort).

## Threat 4: Memory exhaustion via presizing
- Attack: untrusted `initialCapacity` triggers huge allocation (implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst).
- Fix: clamp caller-supplied capacities; prefer lazy default + bounded growth.

## Threat 5: Null-confusion
- Risk: fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal. Code that treats "null value" as "absent" bypasses checks.
- Fix: use `containsKey` / `getOrDefault` explicitly, never null inference.
- Lab note (03-linked-list-deep/SECURITY.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/SECURITY.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/SECURITY.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/SECURITY.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
