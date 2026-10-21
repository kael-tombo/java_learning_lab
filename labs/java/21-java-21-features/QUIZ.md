# Quiz: Java 21 Features

## Question 1
What is the primary advantage of virtual threads over platform threads?

A) They are faster for CPU-bound tasks
B) They eliminate all concurrency bugs
C) They enable millions of concurrent I/O-bound tasks with low memory overhead
D) They replace the need for thread synchronization

## Question 2
Which operation causes a virtual thread to be "pinned" to its carrier thread?

A) `Thread.sleep()`
B) `synchronized` block
C) `java.nio.channels.SocketChannel.read()`
D) `LockSupport.park()`

## Question 3
What is the correct syntax for a guarded pattern in a switch expression?

A) `case Integer i > 0 -> ...`
B) `case Integer i when i > 0 -> ...`
C) `case Integer i if i > 0 -> ...`
D) `case (Integer i) && (i > 0) -> ...`

## Question 4
Which interfaces were added in Java 21 for sequenced collections?

A) `OrderedCollection`, `OrderedSet`, `OrderedMap`
B) `SequencedCollection`, `SequencedSet`, `SequencedMap`
C) `IndexedCollection`, `IndexedSet`, `IndexedMap`
D) `SortedCollection`, `SortedSet`, `SortedMap`

## Question 5
What does the `reversed()` method on a SequencedCollection return?

A) A new reversed copy of the collection
B) A view of the collection in reverse order
C) The last element of the collection
D) A new collection sorted in descending order

## Question 6
What did the template processor do in the String Templates feature (previewed in JDK 21/22 and withdrawn before JDK 23)?

A) It validated that all expressions are compile-time constants
B) It combined template fragments with evaluated values according to processor-specific rules — the model lives on in `String.formatted`
C) It optimized the string concatenation for performance
D) It checked for SQL injection vulnerabilities

## Question 7
What is the purpose of `StructuredTaskScope`?

A) To replace all ExecutorService implementations
B) To enforce a structured lifecycle for concurrent tasks with automatic cancellation
C) To provide a thread pool for virtual threads
D) To improve garbage collection for thread-local variables

## Question 8
Which pattern is valid for nested deconstruction?

A) `case Circle(Point p, double r) -> ...`
B) `case Circle(Point(int x, int y), double r) -> ...`
C) `case Circle(Point(var x, var y), var r) -> ...`
D) All of the above

## Question 9
What happens in a switch expression if null is not explicitly handled?

A) The switch expression returns null
B) A NullPointerException is thrown at runtime
C) The switch falls through to the default case
D) The compiler generates a warning but it's handled automatically

## Question 10
How do you create a virtual thread using the ExecutorService API?

A) `Executors.newFixedThreadPool(0)` with virtual threads
B) `Executors.newVirtualThreadPerTaskExecutor()`
C) `Executors.newCachedThreadPool()` with virtual threads
D) `Executors.newSingleThreadExecutor()` with virtual threads

## Answer Key
1. C, 2. B, 3. B, 4. B, 5. B, 6. B, 7. B, 8. D, 9. B, 10. B
