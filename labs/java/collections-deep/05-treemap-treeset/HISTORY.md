# History: TreeMap / TreeSet

## Java 1.2 (1998) — Collections Framework
- **Josh Bloch** led the design of `java.util` collections (`HashMap`,
  `ArrayList`, `LinkedList`, `TreeMap`); `Collections` utility and the
  fail-fast iterator convention date from this release.

## Java 5 (2004) — Generics + Concurrency
- Generics (JSR 14) made `java.util.TreeMap / java.util.TreeSet` type-safe: `Map<K,V>`, `List<E>`.
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
  replacement for `java.util.TreeMap / java.util.TreeSet`, but the default choice for fixed data.

## Java 21 (2023) — Sequenced collections
- JEP 431 added `SequencedCollection/Map` (`addFirst/addLast/reversed`),
  making `java.util.TreeMap / java.util.TreeSet`'s head/tail behavior part of the interface vocabulary.

## Why this timeline matters for TreeMap / TreeSet
- identity is compareTo==0 (or comparator.compare==0), NOT equals(); compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first.
- iteration ascending via on-the-fly successor links; fail-fast via modCount.
- Source of record remains `java.util.TreeMap`; books below agree on these dates.
