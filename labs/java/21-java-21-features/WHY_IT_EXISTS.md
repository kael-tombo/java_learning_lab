# Why Java 21 Features Exist

## The Problem Landscape

### The Threading Crisis (Virtual Threads)

Before Java 21, Java's concurrency model was tied to OS platform threads. Each `java.lang.Thread` corresponds to an OS thread with a 1 MB default stack. This limits a server to handling roughly 4,000-5,000 concurrent threads—far below what modern microservices need. Workarounds like asynchronous frameworks (CompletableFuture, reactive streams) introduced steep learning curves and debugging nightmares. **Virtual threads exist** to let developers write straightforward synchronous code that scales to millions of concurrent tasks.

### Verbose Conditional Logic (Pattern Matching)

For decades, Java developers wrote tedious `instanceof`-check-cast patterns:

```java
if (obj instanceof String) {
    String s = (String) obj;
    // use s
}
```

This boilerplate invited errors from mismatched types. Switch statements only worked with numeric types, enums, and strings—not with arbitrary object types. **Pattern matching exists** to eliminate this ceremony, reduce errors, and enable declarative type-based dispatch.

### Missing Sequence Operations (Sequenced Collections)

Accessing the last element of a `LinkedHashSet` required iterating through the entire set. Reversing a `Deque` required manual collection manipulation. There was no consistent API for ordered collections to say "give me the first," "give me the last," or "iterate in reverse." **Sequenced Collections exist** to provide a standard, type-safe interface for ordered collections.

### Dangerous String Composition (String Templates)

Building strings with concatenation (`+`) or `String.format()` is error-prone, especially with user-provided data. SQL injection, XSS attacks, and formatting errors are direct consequences. **String Templates were designed** to provide safe, composable, processor-aware string interpolation where the template processor can apply escaping or validation automatically — but they were previewed in JDK 21/22 and withdrawn before JDK 23, so the problem still needs manual answers (`String.formatted`, PreparedStatement, escaping) today.

### Unstructured Concurrency (Structured Concurrency)

Spawning threads with `new Thread(() -> {...}).start()` creates tasks with no clear parent-child relationship. If a parent task completes, its children continue running unseen—leading to resource leaks, orphaned threads, and cascading failures. **Structured Concurrency exists** to enforce task lifecycle boundaries, ensuring all subtasks complete before their parent scope exits.

## Design Goals

Each feature was designed with specific goals:
- **Virtual Threads**: Maintain backward compatibility, preserve the `Thread` API, eliminate blocking penalties
- **Pattern Matching**: Gradual introduction (preview phases), exhaustiveness verification, composability
- **Sequenced Collections**: Backward compatible via default methods, uniform across list/set/map
- **String Templates**: Safety by default, pluggable processing, compile-time verification (withdrawn before JDK 23 after two preview rounds)
- **Structured Concurrency**: Task isolation, error propagation, deadline management

In short, these features exist because the Java platform must evolve to meet modern application demands while preserving its core values of backward compatibility, readability, and robustness.
