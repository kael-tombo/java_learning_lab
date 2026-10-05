# CODE_DEEP_DIVE — Modern Java Deep Dive

## 1. Record Compilation

### Decompiled Record
```java
// Source
public record Point(int x, int y) { }

// Compiled (javap -c)
public final class Point extends java.lang.Record {
    private final int x;
    private final int y;
    
    public Point(int x, int y) { this.x = x; this.y = y; }
    
    public int x() { return x; }
    public int y() { return y; }
    
    public final int hashCode() { ... }
    public final boolean equals(Object o) { ... }
    public final String toString() { ... }
    
    // Serialization support
    protected final Object writeReplace() throws ObjectStreamException { ... }
    protected final Object readResolve() throws ObjectStreamException { ... }
}
```

### Compact Constructor Bytecode
```java
// Source
record User(String name, int age) {
    public User {
        if (name == null) throw new IllegalArgumentException();
        if (age < 0) age = 0;
    }
}

// Bytecode (constructor)
public User(java.lang.String, int);
  Code:
   0: aload_0
   1: aload_1
   2: ifnonnull 11
   5: new java/lang/IllegalArgumentException
   8: dup
   9: invokespecial java/lang/IllegalArgumentException."<init>":()V
  11: aload_0
  12: iload_2
  13: ifge 20
  16: iconst_0
  17: istore_2
  20: aload_0
  21: aload_1
  22: putfield #2  // Field name:Ljava/lang/String;
  25: aload_0
  26: iload_2
  27: putfield #3  // Field age:I
  30: return
```

---

## 2. Sealed Class Implementation

### Class Hierarchy
```java
// Source
sealed interface Shape permits Circle, Square { }
final class Circle implements Shape { ... }
non-sealed class Square implements Shape { }

// Compiled: Shape has PermittedSubclasses attribute
// Circle has SealedKind=FINAL, Square has SealedKind=NON_SEALED
```

### Exhaustiveness Checking
```java
// Switch on sealed type
String describe(Shape s) {
    return switch (s) {
        case Circle c -> "circle";
        case Square sq -> "square";
    };
}

// Compiled: tableswitch on ordinal (no default needed)
// Compiler verifies all permitted subtypes covered
```

### Pattern Matching Bytecode
```java
// Source
if (obj instanceof Point(int x, int y)) { ... }

// Bytecode
ALOAD 1          // obj
INSTANCEOF Point
IFFALSE L1
ALOAD 1
CHECKCAST Point
INVOKEVIRTUAL Point.x()I
ISTORE 2         // x
ALOAD 1
CHECKCAST Point
INVOKEVIRTUAL Point.y()I
ISTORE 3         // y
// ... body
L1:
```

---

## 3. Virtual Threads Implementation

### Virtual Thread Creation
```java
// Source
Thread.startVirtualThread(() -> System.out.println("Hello"));

// Internal: Continuation-based
// java.lang.VirtualThread extends Thread
// Uses Continuation.yield() for park/unpark
```

### Carrier Thread Pool
```java
// Default scheduler: ForkJoinPool.commonPool()
// Work-stealing queue per carrier thread
// Virtual threads yield at: I/O, sleep, lock, yield()

// Scheduler implementation:
class VirtualThreadScheduler {
    private final ForkJoinPool pool;
    
    void schedule(VirtualThread vt) {
        pool.execute(() -> {
            while (!vt.isDone()) {
                vt.runContinuation();  // Run until yield
            }
        });
    }
}
```

### Pinning Detection
```java
// JFR Event: jdk.VirtualThreadPinned
// Triggered when:
/*
1. synchronized block entered
2. Native method called (JNI)
3. Foreign function call (FFI)
*/

// Stack trace shows:
// java.base/java.lang.VirtualThread.pin(VirtualThread.java:XXX)
// java.base/java.lang.VirtualThread.run(VirtualThread.java:XXX)
```

---

## 4. Structured Concurrency Internals

### StructuredTaskScope
```java
// Source
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var f1 = scope.fork(() -> service.call());
    scope.join();
    scope.throwIfFailed();
}

// Implementation:
class StructuredTaskScope<T> implements AutoCloseable {
    private final List<Subtask<?>> subtasks = new ArrayList<>();
    private final AtomicReference<Throwable> failure = new AtomicReference<>();
    
    <U> Subtask<U> fork(Callable<U> task) {
        Subtask<U> st = new Subtask<>(task);
        subtasks.add(st);
        // Submit to scheduler (virtual thread per task)
        scheduler.execute(st);
        return st;
    }
    
    void join() {
        // Wait for all subtasks
        for (Subtask<?> st : subtasks) st.join();
    }
    
    void throwIfFailed() {
        Throwable t = failure.get();
        if (t != null) throw new FailedException(t);
    }
    
    void close() {
        // Shutdown policy: cancel all on failure
        if (failure.get() != null) subtasks.forEach(Subtask::cancel);
    }
}
```

### Subtask State Machine
```
UNAVAILABLE -> SUCCESS (completed normally)
UNAVAILABLE -> FAILED (exception thrown)
SUCCESS/FAILED -> (terminal)
```

---

## 5. Pattern Matching Switch Compilation

### Switch Expression
```java
// Source
String result = switch (obj) {
    case String s -> s.toUpperCase();
    case Integer i -> String.valueOf(i);
    case null -> "null";
    default -> "unknown";
};

// Compiled: tableswitch/lookupswitch on type ordinal
// Null case handled first
// Default case for non-exhaustive
```

### Guarded Pattern
```java
// Source
switch (score) {
    case int s when s >= 90 -> "A";
    case int s when s >= 80 -> "B";
    default -> "F";
}

// Compiled: 
// 1. Type check (int)
// 2. Conditional branch for guard
// 3. Fallthrough to next case if guard fails
```

### Record Pattern
```java
// Source
if (r instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2))) { ... }

// Compiled:
// 1. instanceof Rectangle
// 2. Invoke getTopLeft() -> Point
// 3. Deconstruct Point -> x1, y1
// 4. Invoke getBottomRight() -> Point  
// 5. Deconstruct Point -> x2, y2
```

---

## 6. String Templates (Preview)

### Processor Interface
```java
// java.lang.StringTemplate.Processor
@FunctionalInterface
interface Processor<R> {
    R process(StringTemplate template);
}

// STR Processor (simplified)
static final Processor<String> STR = template -> {
    StringBuilder sb = new StringBuilder();
    List<String> fragments = template.fragments();
    List<Object> values = template.values();
    
    for (int i = 0; i < values.size(); i++) {
        sb.append(fragments.get(i));
        sb.append(values.get(i));
    }
    sb.append(fragments.get(fragments.size() - 1));
    return sb.toString();
};
```

### Template Representation
```java
// STR."Hello \{name}"
// Fragments: ["Hello ", ""]
// Values: [name]

// FMT."Name: \{name:%-10s}"
// Fragments: ["Name: ", ""]
// Values: [name]
// Format specifiers stored in template
```

---

## 7. Foreign Function & Memory API

### MemorySegment Allocation
```java
// Source
try (Arena arena = Arena.ofConfined()) {
    MemorySegment segment = arena.allocate(1024);
    segment.setAtIndex(ValueLayout.JAVA_INT, 0, 42);
}

// Implementation:
// Arena.ofConfined() -> ConfinedArena (thread-local)
// allocate() -> NativeMemorySegment.allocateNative()
// setAtIndex() -> UNSAFE.putInt(address + offset, value)
```

### Layout Definition
```java
// Source
MemoryLayout playerLayout = MemoryLayout.structLayout(
    ValueLayout.JAVA_INT.withName("id"),
    MemoryLayout.sequenceLayout(32, ValueLayout.JAVA_BYTE).withName("name"),
    ValueLayout.JAVA_DOUBLE.withName("score")
);

// Compiled: Layout trees with byte offsets
// playerLayout.byteOffset("id") = 0
// playerLayout.byteOffset("name") = 4
// playerLayout.byteOffset("score") = 36 (aligned)
```

### Downcall Handle
```java
// Source
MethodHandle save = LINKER.downcallHandle(
    LOOKUP.find("save_player").orElseThrow(),
    FunctionDescriptor.ofVoid(ValueLayout.ADDRESS)
);

// Implementation:
// 1. Resolve symbol address
// 2. Generate JNI-like stub (assembly)
// 3. Create MethodHandle with exact signature
// 4. invokeExact -> stub -> native call
```

---

## 8. ScopedValue Implementation

### Binding Mechanism
```java
// Source
ScopedValue<User> CURRENT = ScopedValue.newInstance();
ScopedValue.runWhere(CURRENT, user, () -> handler.handle(request));

// Implementation:
class ScopedValue<T> {
    // InheritableThreadLocal-like but immutable
    private static final ThreadLocal<Map<ScopedValue<?>, Object>> SCOPED_VALUES = 
        ThreadLocal.withInitial(HashMap::new);
    
    static <T> T runWhere(ScopedValue<T> key, T value, Callable<R> op) {
        Map<ScopedValue<?>, Object> map = SCOPED_VALUES.get();
        Object prev = map.put(key, value);
        try { return op.call(); }
        finally { 
            if (prev == null) map.remove(key); 
            else map.put(key, prev);
        }
    }
    
    T get() {
        return (T) SCOPED_VALUES.get().get(this);
    }
}
```

### Virtual Thread Inheritance
```java
// When virtual thread starts:
class VirtualThread extends Thread {
    void run() {
        // Inherit scoped values from creator
        Map<ScopedValue<?>, Object> parentMap = 
            Thread.currentThread().getScopedValues();
        this.scopedValues = new HashMap<>(parentMap);
        // ...
    }
}
```

---

## 9. Sequenced Collections

### Interface Hierarchy
```java
// New interfaces (Java 21)
interface SequencedCollection<E> extends Collection<E> {
    void addFirst(E e);
    void addLast(E e);
    E getFirst();
    E getLast();
    SequencedCollection<E> reversed();
}

interface SequencedSet<E> extends Set<E>, SequencedCollection<E> { }

interface SequencedMap<K,V> extends Map<K,V> {
    SequencedMap<K,V> reversed();
    V putFirst(K k, V v);
    V putLast(K k, V v);
    Map.Entry<K,V> firstEntry();
    Map.Entry<K,V> lastEntry();
}
```

### Implementation (LinkedHashMap)
```java
// LinkedHashMap already maintains insertion order
// Java 21: implements SequencedMap
// reversed() returns lightweight view
public SequencedMap<K,V> reversed() {
    return new ReverseView<>(this);
}

class ReverseView<K,V> implements SequencedMap<K,V> {
    private final SequencedMap<K,V> forward;
    
    public V putFirst(K k, V v) { return forward.putLast(k, v); }
    public V putLast(K k, V v) { return forward.putFirst(k, v); }
    // ... delegates reversed
}
```

---

## 10. JIT Optimization for Modern Features

### Record Inlining
```java
// C2 inlines record accessors aggressively
// x() -> direct field load
// equals/hashCode -> optimized field comparison
// Escape analysis: records often scalar replaced
```

### Virtual Thread Optimization
```java
// C2 knows about virtual thread semantics
// Continuation yield points are safepoints
// Lock elision works with ReentrantLock (not synchronized)
```

### Pattern Matching Optimization
```java
// Switch on sealed type -> tableswitch on ordinal
// Type checks folded into switch
// Guarded patterns -> conditional branches
```

---

## Key Source Files (OpenJDK)

| Feature | Source Files |
|---------|--------------|
| Records | `java/lang/Record.java`, `Record*` in compiler |
| Sealed | `SealedClassAttribute`, `PermittedSubclasses` |
| Pattern Matching | `PatternMatching.java`, `SwitchExpr.java` |
| Virtual Threads | `java/lang/VirtualThread.java`, `Continuation.java` |
| Structured Concurrency | `StructuredTaskScope.java`, `Subtask.java` |
| String Templates | `StringTemplate.java`, `Processor.java` |
| FFI | `jdk/internal/foreign/`, `Linker.java`, `Arena.java` |
| ScopedValue | `ScopedValue.java` |
| Sequenced Collections | `SequencedCollection.java`, `LinkedHashMap.java` |