# How Java 21 Features Work

## Virtual Threads: Mechanics

Virtual threads are instances of `java.lang.Thread` that are scheduled by the JVM rather than the OS. Here's the mechanical flow:

### Creation
```java
Thread vThread = Thread.startVirtualThread(() -> {
    System.out.println("Running in virtual thread: " + Thread.currentThread());
});
```

Or with `Thread.Builder`:
```java
Thread vThread = Thread.ofVirtual()
    .name("my-virtual")
    .unstarted(() -> { /* task */ });
vThread.start();
```

### Execution Flow
1. JVM creates a virtual thread with a lightweight continuation (the stack stored on heap)
2. The virtual thread is submitted to a `ForkJoinPool` of carrier threads (size = number of CPU cores)
3. A carrier thread picks up the virtual thread and executes it
4. When the virtual thread performs a blocking operation (I/O, `park()`, `sleep()`):
   - The JVM intercepts the blocking call
   - The virtual thread's stack is copied to the heap as a continuation
   - The carrier thread is released to execute another virtual thread
5. When the blocking operation completes, the virtual thread is resubmitted to the pool
6. A carrier thread (possibly a different one) picks it up and restores the continuation

### Pinning
Some operations "pin" a virtual thread to its carrier thread, preventing unmounting:
- `synchronized` blocks/methods
- Native method calls (JNI)
- `wait()`/`notify()`

In these cases, the virtual thread blocks the carrier thread, reducing scalability. Use `ReentrantLock` instead of `synchronized` when possible.

## Pattern Matching for switch: Mechanics

### Type Patterns
```java
Object obj = "hello";
switch (obj) {
    case Integer i -> System.out.println("Integer: " + i);
    case String s -> System.out.println("String: " + s);
    case null     -> System.out.println("null");
    default       -> System.out.println("Other: " + obj);
}
```

The compiler generates a type-check-and-cast sequence, similar to `if-else if` chains but with exhaustiveness verification.

### Guarded Patterns
```java
switch (obj) {
    case Integer i when i > 0 -> System.out.println("Positive integer: " + i);
    case Integer i            -> System.out.println("Non-positive integer: " + i);
    case String s when s.length() > 5 -> System.out.println("Long string");
    default -> System.out.println("Other");
}
```

Guards are boolean expressions evaluated after the pattern matches but before the body executes.

### Record Patterns (Nested Deconstruction)
```java
record Point(int x, int y) {}
record Line(Point start, Point end) {}

Line line = new Line(new Point(1, 2), new Point(3, 4));
if (line instanceof Line(Point(int x1, int y1), Point(int x2, int y2))) {
    System.out.println("Line from (" + x1 + "," + y1 + ") to (" + x2 + "," + y2 + ")");
}
```

The compiler generates accessor calls to the record components, then recursively matches.

## Sequenced Collections: Mechanics

### Interface Hierarchy
```
Collection
  ├── List (SequencedCollection)    ← get/set by index, ordered
  ├── Deque (SequencedCollection)   ← double-ended access
  ├── SequencedCollection           ← addFirst/Last, getFirst/Last, reversed()
  └── SequencedSet extends SequencedCollection
      └── SequencedMap extends SequencedCollection-like

SequencedMap: firstEntry(), lastEntry(), pollFirstEntry(), pollLastEntry(), reversed()
```

### Default Methods
The methods are added as default methods on existing classes where possible. For example, `ArrayList` inherits `getFirst()` which calls `get(0)`. `LinkedHashSet` implements these methods natively.

## String Templates: Mechanics

> **Status**: String Templates (JEP 430/459) were previewed in JDK 21/22 and withdrawn before JDK 23 — no current JDK accepts this syntax, even with `--enable-preview`. The model below is kept for historical understanding.

### Template Expression Structure
```java
// The withdrawn preview spelled this STR."Hello \{name}, you are \{age} years old".
// The equivalent that compiles today:
String name = "João";
int age = 30;
String msg = "Hello %s, you are %d years old".formatted(name, age);
```

The historical template expression consisted of:
1. A **template processor** (`STR`, `FMT`, or custom)
2. A dot (`.`)
3. A **template** with embedded expressions `\{expr}`

At compile time, the template was processed into a `StringTemplate` object containing:
- `fragments()`: List of string literal pieces between expressions
- `values()`: List of evaluated expression results

The template processor then combined these as appropriate. `STR` simply interleaved fragments and values; `FMT` applied format specifiers from the fragments. The model lives on conceptually in `String.formatted`, where the format string is the fragment and the arguments are the values.

## Structured Concurrency: Mechanics

```java
Response handle() throws ExecutionException, InterruptedException {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Subtask<String> user  = scope.fork(() -> findUser());
        Subtask<Address> addr = scope.fork(() -> findAddress());
        
        scope.join();                 // Wait for all subtasks
        scope.throwIfFailed();        // Propagate exceptions
        
        return new Response(user.get(), addr.get());
    }
}
```

The `StructuredTaskScope`:
- Maintains a list of forked subtasks
- On `join()`, blocks until all subtasks complete or one fails
- On shutdown, cancels remaining subtasks
- On `close()`, waits for completion (enforced by try-with-resources)

The key mechanical detail: the scope's lifetime is tied to the try-with-resources block, ensuring deterministic cleanup.
