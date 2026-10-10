# History: LinkedList Deep Dive

## Java 1.2 (1998) — Collections Framework
- **Josh Bloch** led the design of `java.util` collections (`HashMap`,
  `ArrayList`, `LinkedList`, `TreeMap`); `Collections` utility and the
  fail-fast iterator convention date from this release.

## Java 5 (2004) — Generics + Concurrency
- Generics (JSR 14) made `java.util.LinkedList` type-safe: `Map<K,V>`, `List<E>`.
- **Doug Lea**'s `java.util.concurrent` (JSR 166) added `ConcurrentHashMap`
  and `CopyOnWriteArrayList`; segment-locked CHM is the ancestor of the
  modern bucket-locked design.

## Java 8 (2014) — Collision defense + CHM rewrite
- Hash bins gained red-black treeification (threshold 8 / untreeify 6 /
  minimum table 64) against hash-flooding denial of service.
- `ConcurrentHashMap` was rewritten onto `Node[]` + CAS + `synchronized`
  bucket heads with `CounterCell` counting; `Segment` removed.

## Java 9 (2017) — Immutable factories
- `List.of / Set.of / Map.of` gave compact immutable collections; not a
  replacement for `java.util.LinkedList`, but the default choice for fixed data.

## Java 21 (2023) — Sequenced collections
- JEP 431 added `SequencedCollection/Map` (`addFirst/addLast/reversed`),
  making `java.util.LinkedList`'s head/tail behavior part of the interface vocabulary.

## Why this timeline matters for LinkedList Deep Dive
- Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs); no sentinel node: size==0 means first==last==null, every mutation branches on null.
- implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst.
- Source of record remains `java.util.LinkedList`; books below agree on these dates.
