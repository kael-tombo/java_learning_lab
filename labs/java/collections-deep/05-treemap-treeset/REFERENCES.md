# References: TreeMap / TreeSet

## Source of record
- OpenJDK source: `java.util.TreeMap` (JDK 17/21/23 — read the field/method level, not
  summaries). Companion: THEORY.md + CODE_DEEP_DIVE.md in this lab.

## Books
- Joshua Bloch, *Effective Java* (3rd ed.): items on equals/hashCode,
  comparators, and Map/List/Set selection — directly governs identity is compareTo==0 (or comparator.compare==0), NOT equals().
- Doug Lea, *Concurrent Programming in Java* + Goetz et al., *Java
  Concurrency in Practice*: bucket locking, safe publication, and why
  unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.
- Cormen et al., *Introduction to Algorithms (CLRS)*: hashing/amortized
  analysis and red-black trees behind compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first and floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).
- Bentley, *Programming Pearls*: back-of-envelope sizing for iteration ascending via on-the-fly successor links; fail-fast via modCount.

## API docs
- `java.util` package docs + `java.util.TreeMap / java.util.TreeSet` class javadoc: complexity table and
  view/fail-fast contracts (NavigableSubMap view classes).

## Tools
- JMH for put/get/remove microbenchmarks; JOL for per-entry bytes
  (iteration ascending via on-the-fly successor links; fail-fast via modCount); async-profiler for growth-spike attribution.
- Lab note (05-treemap-treeset/REFERENCES.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFERENCES.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFERENCES.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFERENCES.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFERENCES.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFERENCES.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
- Lab note (05-treemap-treeset/REFERENCES.md): floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n)
