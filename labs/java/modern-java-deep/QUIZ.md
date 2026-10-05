# QUIZ — Modern Java Deep Dive

## Multiple Choice

### 1. Record Compilation
What does the compiler generate for a record `record Point(int x, int y) { }`?

A) Only constructor and getters
B) Constructor, getters, equals, hashCode, toString
C) Constructor, getters, equals, hashCode, toString, and `writeReplace`/`readResolve` for serialization
D) All of the above plus `clone()`

**Answer: C)** Records get canonical constructor, accessors, equals/hashCode/toString, and serialization support via `writeReplace`/`readResolve`

---

### 2. Sealed Class Permits
Which statement about sealed classes is FALSE?

A) Permitted subclasses must be in the same module
B) Permitted subclasses can be `final`, `sealed`, or `non-sealed`
C) Sealed interface can permit classes in different packages
D) A sealed class can permit a class that doesn't extend it

**Answer: D)** Permitted subclasses MUST extend/implement the sealed class/interface

---

### 3. Pattern Matching Switch Exhaustiveness
```java
sealed interface Shape permits Circle, Square { }
record Circle(double r) implements Shape { }
record Square(double s) implements Shape { }

String describe(Shape s) {
    return switch (s) {
        case Circle c -> "circle";
        case Square sq -> "square";
    };
}
```
What happens if you add `record Triangle(double a) implements Shape { }` without updating the switch?

A) Compiles with warning
B) Compile error: switch not exhaustive
C) Runtime exception
D) Default case added implicitly

**Answer: B)** Compiler verifies exhaustiveness for sealed types

---

### 4. Virtual Thread Pinning
Which operation does NOT pin a virtual thread to its carrier thread?

A) `synchronized` block
B) `ReentrantLock.lock()`
C) Native method call (JNI)
D) `Thread.sleep()`

**Answer: B)** `ReentrantLock` does not pin; use it instead of `synchronized` in virtual thread code

---

### 5. StructuredTaskScope
What does `ShutdownOnFailure` do when one subtask fails?

A) Cancels all other subtasks immediately
B) Waits for all subtasks to complete, then throws
C) Shuts down the scope, cancels remaining subtasks, propagates exception
D) Retries the failed subtask 3 times

**Answer: C)** Shuts down scope, cancels remaining subtasks, propagates first exception

---

### 6. Record Patterns
```java
record Point(int x, int y) { }
record Rectangle(Point tl, Point br) { }

void print(Rectangle r) {
    if (r instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2))) {
        System.out.println(x1 + "," + y1 + " - " + x2 + "," + y2);
    }
}
```
What pattern matching feature is demonstrated?

A) Type pattern
B) Record pattern
C) Nested pattern
D) All of the above

**Answer: D)** Uses type pattern (`Rectangle`), record pattern (`Point(...)`), and nested patterns

---

### 7. Guarded Patterns
```java
String grade(int score) {
    return switch (score) {
        case int s when s >= 90 -> "A";
        case int s when s >= 80 -> "B";
        case int s when s >= 70 -> "C";
        default -> "F";
    };
}
```
What is the `when` clause called?

A) Filter pattern
B) Guarded pattern
C) Conditional pattern
D) Predicate pattern

**Answer: B)** Guarded pattern (Java 21+)

---

### 8. String Templates (Preview)
```java
String name = "Alice";
String query = STR."SELECT * FROM users WHERE name = \{name}";
```
What is the `STR` processor?

A) Standard interpolation processor
B) Formatted output processor
C) Raw template processor
D) SQL-safe processor

**Answer: A)** `STR` = standard interpolation; `FMT` = formatted; `RAW` = raw template

---

### 9. Sequenced Collections
Which interface was added in Java 21 for collections with defined order?

A) `OrderedCollection`
B) `SequencedCollection`
C) `IndexedCollection`
D) `PositionalCollection`

**Answer: B)** `SequencedCollection` with `reversed()`, `addFirst()`, `addLast()`, `getFirst()`, `getLast()`

---

### 10. Foreign Function Interface
What is the purpose of `Arena` in FFI?

A) Memory allocation for native code
B) Scoped lifecycle management for native memory
C) Thread pool for native calls
D) JNI replacement

**Answer: B)** `Arena` manages native memory lifecycle (confined, shared, global)

---

### 11. ScopedValue vs ThreadLocal
Which statement is TRUE about `ScopedValue`?

A) Inherited by child threads automatically
B) Only works with platform threads
C) Mutable like ThreadLocal
D) Requires manual cleanup

**Answer: A)** `ScopedValue` is automatically inherited by virtual threads and child threads

---

### 12. Compact Constructor Validation
```java
record User(String name, int age) {
    public User {
        if (name == null) throw new IllegalArgumentException();
        if (age < 0) age = 0; // normalize
    }
}
```
What happens when calling `new User("Alice", -5)`?

A) Compile error
B) Throws IllegalArgumentException
C) Creates User with age = 0
D) Creates User with age = -5

**Answer: C)** Compact constructor can normalize/validate before assignment

---

## True/False

### 13. Records can extend other classes.
**False** — Records implicitly extend `java.lang.Record` and cannot extend other classes

### 14. Sealed classes work with pattern matching for exhaustiveness checking.
**True** — This is the primary use case

### 15. Virtual threads share carrier threads via work-stealing.
**True** — Virtual threads are scheduled on carrier threads (ForkJoinPool) using work-stealing

### 16. `StructuredTaskScope` prevents thread leaks.
**True** — Automatic shutdown/cancellation on scope exit

### 17. Pattern matching switch requires `default` clause.
**False** — Exhaustive switches on sealed types don't need default

### 18. String templates are a standard feature in Java 21.
**False** — Preview feature, requires `--enable-preview`

### 18. `SequencedMap` extends `Map` and adds `reversed()`.
**True** — Also adds `putFirst`, `putLast`, `firstEntry`, `lastEntry`

### 19. FFI requires JNI headers and C compilation.
**False** — Pure Java, no C compilation needed (unlike JNI)

### 20. `ScopedValue` supports rebinding in nested scopes.
**True** — `ScopedValue.runWhere()` creates nested binding

---

## Code Completion

### 21. Complete the sealed hierarchy
```java
sealed interface Result permits _______, _______ { }
record Success<T>(T value) implements Result { }
record Failure(Throwable error) implements Result { }
```

**Answer:** `Success`, `Failure`

---

### 22. Complete the structured concurrency
```java
try (var scope = new StructuredTaskScope._________()) {
    var f1 = scope.fork(() -> serviceA.call());
    var f2 = scope.fork(() => serviceB.call());
    scope.join();
    scope.throwIfFailed();
    return combine(f1.get(), f2.get());
}
```

**Answer:** `ShutdownOnFailure` (or `ShutdownOnSuccess` for racing)

---

### 23. Complete the record pattern
```java
record Pair(String first, String second) { }
record Triple(Pair p, String third) { }

void process(Triple t) {
    if (t instanceof Triple(Pair(String a, String b), String c)) {
        System.out.println(a + " " + b + " " + c);
    }
}
```

---

## Scenario

### 24. Virtual Thread Migration
You're migrating a Spring Boot app from platform threads to virtual threads. The app uses:
- `synchronized` on service methods
- `ThreadLocal` for request context
- JDBC connection pool (HikariCP)

What changes are needed?

A) Replace `synchronized` with `ReentrantLock`, `ThreadLocal` with `ScopedValue`, use virtual-thread-aware pool
B) Just change `ExecutorService` to virtual thread executor
C) Only replace `ThreadLocal` with `InheritableThreadLocal`
D) No changes needed, fully compatible

**Answer: A)** All three need changes for proper virtual thread behavior

---

### 25. Record Serialization
```java
record User(String name, String password) implements Serializable {
    private static final long serialVersionUID = 1L;
}
```
When deserializing a `User` record:
A) Canonical constructor called with serialized values
B) Default constructor called, then fields set via reflection
C) `readObject` called automatically
D) Fails because records can't be serialized

**Answer: A)** Deserialization calls canonical constructor (like construction)