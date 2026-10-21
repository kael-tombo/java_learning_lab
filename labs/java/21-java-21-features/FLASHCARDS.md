# Flashcards: Java 21 Features

## Card 1
**Q**: What is a virtual thread?
**A**: A lightweight thread managed by the JVM (not the OS) that can be parked and unmounted from its carrier thread during blocking operations, enabling millions of concurrent threads with low memory overhead.

## Card 2
**Q**: What is a carrier thread?
**A**: A platform thread that executes virtual threads. The JVM uses a ForkJoinPool of carrier threads (typically equal to the number of CPU cores) to schedule and run virtual threads.

## Card 3
**Q**: What does "pinning" mean in the context of virtual threads?
**A**: When a virtual thread cannot be unmounted from its carrier thread (e.g., inside a synchronized block), it is "pinned." The carrier thread is blocked during this time, reducing scalability.

## Card 4
**Q**: How do you create a virtual thread?
**A**: `Thread.startVirtualThread(runnable)`, `Thread.ofVirtual().start(runnable)`, or `Executors.newVirtualThreadPerTaskExecutor()`.

## Card 5
**Q**: What is the syntax for a type pattern in switch?
**A**: `case Type variableName -> expression` — e.g., `case Integer i -> process(i)`.

## Card 6
**Q**: What is a guarded pattern?
**A**: A pattern combined with a boolean condition: `case Type var when condition -> expression`. The condition is evaluated only after the pattern matches.

## Card 7
**Q**: What is a record pattern?
**A**: A pattern that deconstructs a record into its components: `case RecordType(component1, component2) -> expression`. Supports nested deconstruction.

## Card 8
**Q**: What is the `reversed()` method?
**A**: A method on SequencedCollection/SequencedSet/SequencedMap that returns a reverse-ordered view of the collection (not a copy).

## Card 9
**Q**: What methods does SequencedCollection add?
**A**: `addFirst()`, `addLast()`, `getFirst()`, `getLast()`, `removeFirst()`, `removeLast()`, `reversed()`.

## Card 10
**Q**: What is a string template expression?
**A**: A form like `STR."Hello \{name}"` that combined a template processor (STR/FMT) with a template containing embedded expressions `\{...}`. Status: it was previewed in JDK 21/22 and withdrawn before JDK 23 — today use `String.formatted` or concatenation instead.

## Card 11
**Q**: What is StructuredTaskScope?
**A**: A structured concurrency API that groups related tasks into a scope. When the scope closes, all tasks must complete (or be cancelled). It ensures no orphaned threads.

## Card 12
**Q**: What are the two ShutdownPolicies for StructuredTaskScope?
**A**: `ShutdownOnFailure` (cancel all if any task fails) and `ShutdownOnSuccess` (cancel all if any task succeeds).

## Card 13
**Q**: How does `scope.join()` differ from `ExecutorService.invokeAll()`?
**A**: `scope.join()` waits for all tasks in the scope and respects the shutdown policy. If any task fails with `ShutdownOnFailure`, remaining tasks are cancelled.

## Card 14
**Q**: What is the advantage of pattern matching over instanceof-cast?
**A**: Pattern matching eliminates the need for explicit casting, combines type checking and variable binding in one step, and enables exhaustive switch expressions.

## Card 15
**Q**: What was the difference between `STR."..."` and `FMT."..."`, and do either work today?
**A**: Historically, `STR` performed simple string interpolation and `FMT` (FormatProcessor) applied format specifiers from the template fragments, similar to `String.format()`. Neither works today: the feature was previewed in JDK 21/22 and then withdrawn before JDK 23, so `String.formatted` fills the `FMT` role on current JDKs.

## Card 16
**Q**: Can virtual threads use ThreadLocal?
**A**: Yes, but it's discouraged. Each virtual thread creates its own ThreadLocal map, adding memory overhead. `ScopedValue` is the recommended alternative.

## Card 17
**Q**: What is the exhaustiveness requirement in pattern matching?
**A**: A switch expression over a sealed type must cover all permitted subtypes. The compiler verifies this, making the code safer.

## Card 18
**Q**: How does `StructuredTaskScope` enforce lifecycle?
**A**: Through `AutoCloseable`. The try-with-resources block ensures `close()` is called. If tasks are still running, `close()` waits for them.

## Card 19
**Q**: Which collection types implement SequencedCollection?
**A**: All List implementations, Deque implementations, LinkedHashSet, TreeSet (via NavigableSet), and their subclasses.

## Card 20
**Q**: What is the memory cost of a parked virtual thread?
**A**: Approximately 200 bytes (versus ~1 MB for a platform thread stack). This allows millions of virtual threads in a few hundred MB of heap.
