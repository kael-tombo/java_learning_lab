# References: HashMap Internals

## Source of record
- OpenJDK source: `java.util.HashMap` (JDK 17/21/23 — read the field/method level, not
  summaries). Companion: THEORY.md + CODE_DEEP_DIVE.md in this lab.

## Books
- Joshua Bloch, *Effective Java* (3rd ed.): items on equals/hashCode,
  comparators, and Map/List/Set selection — directly governs TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64.
- Doug Lea, *Concurrent Programming in Java* + Goetz et al., *Java
  Concurrency in Practice*: bucket locking, safe publication, and why
  fail-fast via modCount, ConcurrentModificationException.
- Cormen et al., *Introduction to Algorithms (CLRS)*: hashing/amortized
  analysis and red-black trees behind resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0 and TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.
- Bentley, *Programming Pearls*: back-of-envelope sizing for default capacity 16, load factor 0.75.

## API docs
- `java.util` package docs + `java.util.HashMap` class javadoc: complexity table and
  view/fail-fast contracts (entrySet().iterator() EntryIterator).

## Tools
- JMH for put/get/remove microbenchmarks; JOL for per-entry bytes
  (default capacity 16, load factor 0.75); async-profiler for growth-spike attribution.
- Lab note (01-hashmap-internals/REFERENCES.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFERENCES.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFERENCES.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFERENCES.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFERENCES.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFERENCES.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/REFERENCES.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
