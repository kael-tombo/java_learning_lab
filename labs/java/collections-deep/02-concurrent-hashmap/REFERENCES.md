# References: ConcurrentHashMap

## Source of record
- OpenJDK source: `java.util.concurrent.ConcurrentHashMap` (JDK 17/21/23 — read the field/method level, not
  summaries). Companion: THEORY.md + CODE_DEEP_DIVE.md in this lab.

## Books
- Joshua Bloch, *Effective Java* (3rd ed.): items on equals/hashCode,
  comparators, and Map/List/Set selection — directly governs spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative.
- Doug Lea, *Concurrent Programming in Java* + Goetz et al., *Java
  Concurrency in Practice*: bucket locking, safe publication, and why
  volatile tabAt/casTabAt reads; Node.val/next volatile.
- Cormen et al., *Introduction to Algorithms (CLRS)*: hashing/amortized
  analysis and red-black trees behind sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer and TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.
- Bentley, *Programming Pearls*: back-of-envelope sizing for writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt).

## API docs
- `java.util` package docs + `java.util.concurrent.ConcurrentHashMap` class javadoc: complexity table and
  view/fail-fast contracts (weakly-consistent iterators (never throw CME)).

## Tools
- JMH for put/get/remove microbenchmarks; JOL for per-entry bytes
  (writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt)); async-profiler for growth-spike attribution.
- Lab note (02-concurrent-hashmap/REFERENCES.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFERENCES.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFERENCES.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFERENCES.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFERENCES.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFERENCES.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
- Lab note (02-concurrent-hashmap/REFERENCES.md): TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap
