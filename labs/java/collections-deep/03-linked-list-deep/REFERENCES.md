# References: LinkedList Deep Dive

## Source of record
- OpenJDK source: `java.util.LinkedList` (JDK 17/21/23 — read the field/method level, not
  summaries). Companion: THEORY.md + CODE_DEEP_DIVE.md in this lab.

## Books
- Joshua Bloch, *Effective Java* (3rd ed.): items on equals/hashCode,
  comparators, and Map/List/Set selection — directly governs Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs).
- Doug Lea, *Concurrent Programming in Java* + Goetz et al., *Java
  Concurrency in Practice*: bucket locking, safe publication, and why
  unsynchronized; structural change must flow through link/unlink (size+modCount).
- Cormen et al., *Introduction to Algorithms (CLRS)*: hashing/amortized
  analysis and red-black trees behind no sentinel node: size==0 means first==last==null, every mutation branches on null and doubly-linked symmetry: node.next.prev == node.prev.next == node.
- Bentley, *Programming Pearls*: back-of-envelope sizing for implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst.

## API docs
- `java.util` package docs + `java.util.LinkedList` class javadoc: complexity table and
  view/fail-fast contracts (ListItr / DescendingIterator).

## Tools
- JMH for put/get/remove microbenchmarks; JOL for per-entry bytes
  (implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst); async-profiler for growth-spike attribution.
- Lab note (03-linked-list-deep/REFERENCES.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFERENCES.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFERENCES.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFERENCES.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFERENCES.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFERENCES.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFERENCES.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
