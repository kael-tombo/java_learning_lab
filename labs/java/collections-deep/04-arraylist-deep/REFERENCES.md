# References: ArrayList Deep Dive

## Source of record
- OpenJDK source: `java.util.ArrayList` (JDK 17/21/23 — read the field/method level, not
  summaries). Companion: THEORY.md + CODE_DEEP_DIVE.md in this lab.

## Books
- Joshua Bloch, *Effective Java* (3rd ed.): items on equals/hashCode,
  comparators, and Map/List/Set selection — directly governs lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10.
- Doug Lea, *Concurrent Programming in Java* + Goetz et al., *Java
  Concurrency in Practice*: bucket locking, safe publication, and why
  unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.
- Cormen et al., *Introduction to Algorithms (CLRS)*: hashing/amortized
  analysis and red-black trees behind two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact) and MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves).
- Bentley, *Programming Pearls*: back-of-envelope sizing for set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it.

## API docs
- `java.util` package docs + `java.util.ArrayList` class javadoc: complexity table and
  view/fail-fast contracts (SubList view + fail-fast Itr/ListItr).

## Tools
- JMH for put/get/remove microbenchmarks; JOL for per-entry bytes
  (set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it); async-profiler for growth-spike attribution.
- Lab note (04-arraylist-deep/REFERENCES.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFERENCES.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFERENCES.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFERENCES.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFERENCES.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFERENCES.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
- Lab note (04-arraylist-deep/REFERENCES.md): MAX_ARRAY_SIZE Integer.MAX_VALUE-8; shifts via System.arraycopy (block moves)
