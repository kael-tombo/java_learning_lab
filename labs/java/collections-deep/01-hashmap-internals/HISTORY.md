# History: HashMap Internals

## Java 1.2 (1998) — Collections Framework
- **Josh Bloch** led the design of `java.util` collections (`HashMap`,
  `ArrayList`, `LinkedList`, `TreeMap`); `Collections` utility and the
  fail-fast iterator convention date from this release.

## Java 5 (2004) — Generics + Concurrency
- Generics (JSR 14) made `java.util.HashMap` type-safe: `Map<K,V>`, `List<E>`.
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
  replacement for `java.util.HashMap`, but the default choice for fixed data.

## Java 21 (2023) — Sequenced collections
- JEP 431 added `SequencedCollection/Map` (`addFirst/addLast/reversed`),
  making `java.util.HashMap`'s head/tail behavior part of the interface vocabulary.

## Why this timeline matters for HashMap Internals
- TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64; resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0.
- default capacity 16, load factor 0.75.
- Source of record remains `java.util.HashMap`; books below agree on these dates.
