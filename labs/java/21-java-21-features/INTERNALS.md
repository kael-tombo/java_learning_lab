# Internal Implementation of Java 21 Features

## Virtual Threads: JVM Internals

### Continuation Implementation
At the JVM level, virtual threads are built on **continuations** (`jdk.internal.vm.Continuation`). A continuation captures the execution state of a thread—its stack frames, local variables, and program counter—as a heap-allocated object.

The JVM modifies its native code to:
1. Detect blocking operations via `java.lang.VirtualThread.park()`
2. Call `Continuation.yield()` which saves the stack frames to a `ScopedValue`-managed buffer
3. Release the carrier thread
4. When resuming, `Continuation.run()` restores the stack and continues execution

### ForkJoinPool Integration
Virtual threads are executed by a dedicated `ForkJoinPool` (called the "virtual thread scheduler"). This pool:
- Has a parallelism level equal to the number of available processors
- Uses work-stealing to balance virtual threads across carrier threads
- Provides `ForkJoinPool.ManagedBlocker` for virtual threads to signal pending states

### Object Header Changes
Java 21 introduces changes to object headers to support virtual threads efficiently. The identity hash code and biased locking are affected.

### ThreadLocal Considerations
`ThreadLocal` variables work with virtual threads but should be used sparingly because:
- Each virtual thread gets its own ThreadLocal map (memory overhead)
- ThreadLocal is used extensively in pinning scenarios (synchronized blocks)
- `ScopedValue` (from Project Loom) is the preferred alternative for many use cases

## Pattern Matching: Compiler Internals

### Type Pattern Translation
```java
// Source
switch (obj) {
    case Integer i -> process(i);
    case String s -> process(s);
}

// Bytecode equivalent (simplified)
if (obj instanceof Integer) {
    Integer i = (Integer) obj;
    process(i);
} else if (obj instanceof String) {
    String s = (String) obj;
    process(s);
}
```

The compiler analyzes pattern dominance and exhaustiveness:
- A pattern is **dominant** if it always matches when a subsequent pattern would match
- Exhaustiveness checks that all possible types of the input (including null) are covered
- For sealed hierarchies, the compiler knows all permitted subtypes and can verify completeness

### Record Pattern Translation
Record patterns are translated to calls to the record's accessor methods:

```java
// Source: case Point(int x, int y) -> ...
// Translation: if (obj instanceof Point) {
//                 int x = ((Point)obj).x();
//                 int y = ((Point)obj).y();
//                 ...
//              }
```

## Sequenced Collections: Implementation Strategy

The new interfaces use **default methods** extensively. For example, `ArrayList.getFirst()` is implemented as:

```java
default E getFirst() {
    if (isEmpty()) throw new NoSuchElementException();
    return iterator().next();
}
```

Specialized implementations override these defaults for efficiency:
- `LinkedList` overrides `getFirst()` to call `getFirstNode().item` (O(1))
- `LinkedHashSet` overrides `reversed()` to return a descending iterator
- `TreeSet` and `TreeMap` override to leverage their internal tree structure

## String Templates: Compile-Time Processing

String template expressions (previewed in JDK 21/22, withdrawn before JDK 23 — no current JDK accepts them) were desugared by the compiler into:

```java
// Historical source (STR."..." preview syntax, withdrawn): STR."Hello \{name}, you are \{age} years old"
// What the compiler did under the hood:
StringTemplate.of(List.of("Hello ", ", you are ", " years old"), List.of(name, age))
    .process(STR);
```

The `StringTemplate` object captures both the literal fragments and the evaluated values. The `Processors.STR` processor simply interleaves them:

```java
public String process(StringTemplate st) {
    StringBuilder sb = new StringBuilder();
    List<String> fragments = st.fragments();
    List<Object> values = st.values();
    for (int i = 0; i < fragments.size(); i++) {
        sb.append(fragments.get(i));
        if (i < values.size()) {
            sb.append(values.get(i));
        }
    }
    return sb.toString();
}
```

## Structured Concurrency: Scope Implementation

`StructuredTaskScope` uses a `CopyOnWriteArrayList` internally to track forked subtasks. When `join()` is called, it awaits a countdown latch that is decremented when each subtask completes. If `ShutdownOnFailure` policy is active and a subtask throws, the scope's `shutdown()` method cancels all remaining subtasks.

The try-with-resources ensures `close()` is called, which throws if `join()` was not called, enforcing the structured lifecycle.
