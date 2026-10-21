# Theory: Java 21 Features

## Virtual Threads - Theoretical Foundation

Virtual threads are an implementation of user-mode threads (also known as fibers or green threads) scheduled by the Java runtime rather than the operating system. The fundamental insight is that most concurrent tasks spend significant time waiting—for I/O, network responses, database queries, or lock acquisition. During these waiting periods, a platform thread is wasted if blocked.

The theoretical model is a many-to-many mapping between virtual threads and platform threads (carrier threads). The JVM's ForkJoinPool manages this mapping. When a virtual thread performs a blocking operation (e.g., `Socket.read()`), the JVM "mounts" the virtual thread onto a carrier thread. When the virtual thread blocks, the JVM unmounts it, parks its stack frame on the heap, and mounts another ready virtual thread onto the same carrier thread.

This model achieves three theoretical benefits:
1. **M:N threading**: M virtual threads run on N platform threads (where N is typically the number of CPU cores)
2. **Synchronous programming model**: Developers write sequential code without callbacks or reactive chains
3. **Resource efficiency**: A server can handle millions of concurrent connections with minimal memory overhead (a parked virtual thread consumes ~200 bytes vs ~1 MB for a platform thread stack)

## Pattern Matching for switch - Theoretical Foundation

Pattern matching extends the theoretical concept of algebraic data types and exhaustive pattern matching found in functional languages like Haskell, Scala, and ML. The switch construct evolves from a simple equality-based dispatch to a structural pattern-matching engine.

The theory decomposes into several pattern types:
- **Type patterns**: `case Integer i` — matches any Integer and binds it to variable `i`
- **Record patterns**: `case Point(int x, int y)` — deconstructs a record into its components
- **Guarded patterns**: `case Integer i when i > 0` — adds boolean conditions
- **Null handling**: `case null` — explicit null branch, improving null safety

The exhaustiveness principle ensures all possible inputs are covered either explicitly or through a `default`/`var` case. The compiler verifies exhaustiveness at compile time.

## Sequenced Collections - Theoretical Foundation

The theory addresses a long-standing deficiency in Java's collection hierarchy: there was no uniform interface for collections with a defined encounter order. `List`, `Deque`, `LinkedHashSet`, `TreeSet`, and `SortedSet` all have ordering guarantees but expose different APIs for accessing first/last elements.

The `SequencedCollection<E>` interface introduces `addFirst`, `addLast`, `getFirst`, `getLast`, `removeFirst`, `removeLast`, and `reversed()`. `SequencedSet<E>` extends this with reversed-order views, and `SequencedMap<K,V>` provides analogous methods for key-value pairs.

## String Templates - Theoretical Foundation

> **Status**: String Templates were previewed in JDK 21/22 (JEP 430/459) and withdrawn before JDK 23 — no current JDK accepts them. The theoretical model is kept here because it shaped Java's thinking on safe interpolation; the practical takeaway today is `String.formatted`, text blocks, and escaping by hand.

String templates addressed the security and readability issues of string concatenation and formatting. The theoretical model treats a template as a combination of literal text and embedded expressions. A `StringTemplate` processor receives the template, processes it, and produces a result.

The key insight is that template processing is pluggable: different processors (like `STR`, `FMT`, or custom processors) can interpret the same template differently, enabling safe SQL construction, JSON building, or internationalization without escaping vulnerabilities. Withdrawing the preview does not invalidate the problem — injection-safe interpolation remains an open need that `String.formatted` only partly answers.

## Structured Concurrency - Theoretical Foundation

Structured concurrency is based on the principle that concurrent tasks should have a clear structure with defined lifetimes. A parent task creates a scope, spawns child tasks within that scope, and the scope ensures all children complete (or are cancelled) before the parent continues.

This mirrors structured programming's approach to control flow: just as structured programming eliminated `goto` in favor of blocks, structured concurrency eliminates unstructured thread spawning in favor of hierarchical task scopes.
