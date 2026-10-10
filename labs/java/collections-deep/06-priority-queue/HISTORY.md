# History: Priority Queues and Heaps

## The heap (1964)

**J. W. J. Williams** published the binary heap in 1964 ("Algorithm 232 —
Heapsort", *Communications of the ACM*), giving both the array-embedded
tree and the sift operations PriorityQueue still uses. **R. W. Floyd**
(1964) added the O(n) bottom-up build — the `heapify()` starting at
`(n>>>1)-1` in the JDK source is Floyd's construction verbatim.

## Java's adoption (2004)

`java.util.PriorityQueue` arrived in **Java 5 (2004, JSR 176, Tiger
release)** as part of the Queue-framework push (`Queue`, `BlockingQueue`,
`ConcurrentLinkedQueue` all date to this release). **Josh Bloch** led the
collections work of the era; the class javadoc credits the queue-framework
design to **Doug Lea**'s concurrency package, which Sun folded into
`java.util.concurrent` in the same release.

## Sibling: PriorityBlockingQueue

The blocking variant shipped in the same Java 5 wave, wrapping the
identical heap algorithm in a `ReentrantLock` plus `notEmpty` condition —
same O(log n) sifts, plus blocking `take()`.

## Implementation notes

- `DEFAULT_INITIAL_CAPACITY = 11` and the `oldCap + 2 below 64` growth
  formula are JDK-specific tuning, shared with `ArraysSupport.newLength`
  (JDK 9+ replacement for the old inline `oldCapacity*2+2`-style code).
- The `initialCapacity < 1` rejection kept "for 1.5 compatibility" (source
  comment) is a fossil of the 2004 API contract, preserved across every
  release since.
