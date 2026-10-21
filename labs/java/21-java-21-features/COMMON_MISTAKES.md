# Common Mistakes with Java 21 Features

## Virtual Threads

### Mistake 1: Using synchronized Blocks Excessively
```java
// BAD: Synchronized pinning causes carrier thread blocking
public synchronized void process() {
    // Virtual thread gets pinned to carrier
}

// GOOD: Use ReentrantLock instead
private final Lock lock = new ReentrantLock();
public void process() {
    lock.lock();
    try {
        // Virtual thread can unmount properly
    } finally {
        lock.unlock();
    }
}
```

### Mistake 2: ThreadLocal Abuse in Virtual Threads
```java
// BAD: Each virtual thread creates a ThreadLocal (memory overhead)
private static final ThreadLocal<Map<String, Object>> context = new ThreadLocal<>();

// GOOD: Use ScopedValue for request-scoped data
private static final ScopedValue<Map<String, Object>> CONTEXT = ScopedValue.newInstance();
ScopedValue.where(CONTEXT, requestData).run(() -> {
    // ScopedValue is inherited by child virtual threads efficiently
});
```

### Mistake 3: Thread Pools with Virtual Threads
```java
// BAD: Pooling virtual threads defeats their purpose
ExecutorService pool = Executors.newFixedThreadPool(100, Thread.ofVirtual().factory());

// GOOD: Use the unbounded virtual thread executor
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
```

## Pattern Matching

### Mistake 4: Pattern Ordering and Dominance
```java
// BAD: Integer pattern dominates, second branch is unreachable
switch (obj) {
    case Integer i -> handleInt(i);
    case Integer i when i > 0 -> handlePositiveInt(i);  // COMPILER ERROR: unreachable
    default -> handleOther(obj);
}

// GOOD: Put more specific (guarded) patterns first
switch (obj) {
    case Integer i when i > 0 -> handlePositiveInt(i);
    case Integer i -> handleInt(i);
    default -> handleOther(obj);
}
```

### Mistake 5: Forgetting null Handling
```java
// BAD: No null case in switch
switch (obj) {
    case String s -> processString(s);
    case Integer i -> processInt(i);
    // What if obj is null? NullPointerException!
}

// GOOD: Handle null explicitly
switch (obj) {
    case null -> handleNull();
    case String s -> processString(s);
    case Integer i -> processInt(i);
}
```

## Sequenced Collections

### Mistake 6: Assuming All Collections Support Sequenced Operations
```java
// BAD: HashSet might not preserve order
Set<String> set = new HashSet<>(Set.of("A", "B", "C"));
set.getFirst(); // Works but result is non-deterministic

// GOOD: Use explicitly ordered collections
SequencedCollection<String> seq = new LinkedHashSet<>(List.of("A", "B", "C"));
```

## String Templates

> **Status**: String Templates were previewed in JDK 21/22 and withdrawn before JDK 23. No current JDK accepts `STR."..."` syntax — not even with `--enable-preview`. Do not enable previews expecting this feature.

### Mistake 7: Expecting String Templates to Compile on Current JDKs
```java
// BAD: The withdrawn preview syntax — fails to compile on any JDK today
String msg = "Hello \{name}";  // Also wrong: literal string with backslash-brace

// GOOD: Use the APIs that actually exist
String msg = "Hello %s".formatted(name);  // or "Hello " + name
```

**Takeaway**: The feature was withdrawn wholesale — there is no preview flag that brings it back. On current JDKs build interpolated strings with `String.formatted`, concatenation, or text blocks. (`--enable-preview` still matters for other live preview features, but not this one.)

## Structured Concurrency

### Mistake 8: Not Calling join() Before Scope Close
```java
// BAD: Scope closes without joining tasks
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    scope.fork(() -> fetchData());
    // Missing scope.join()!
}  // close() throws IllegalStateException

// GOOD: Always join within the scope
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> f = scope.fork(() -> fetchData());
    scope.join();
    return f.resultNow();
}
```

### Mistake 9: Forgetting to Handle InterruptedException
```java
// BAD: Swallowing interrupt
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    scope.fork(() -> task());
    scope.join();  // Can throw InterruptedException
}

// GOOD: Propagate or restore interrupt status
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    scope.fork(() -> task());
    scope.join();  // Let it propagate
}
```

## General Mistakes

### Mistake 10: Misusing --enable-preview for Preview Features
Preview features need `--enable-preview --release 21` at compile time and `--enable-preview` at runtime. This applies to live previews such as Structured Concurrency — but not to String Templates: that feature was withdrawn wholesale before JDK 23, so no `--enable-preview` flag brings it back on any current JDK.
