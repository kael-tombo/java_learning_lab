# THEORY — Modern Java Deep Dive

## Overview

Comprehensive coverage of Java 17-21+ features: pattern matching, virtual threads, structured concurrency, records, sealed classes, and migration strategies.

---

## Records (Java 16)

### Definition

```java
public record Person(String name, int age, Address address) {
    // Compact constructor for validation
    public Person {
        if (name == null || name.isBlank()) throw new IllegalArgumentException("Name required");
        if (age < 0) throw new IllegalArgumentException("Age must be positive");
    }
    
    // Static factory
    public static Person of(String name, int age) {
        return new Person(name.trim(), age, null);
    }
}
```

### Generated Members

- `name()`, `age()`, `address()` - accessors
- `equals(Object)`, `hashCode()` - all components
- `toString()` - formatted
- Canonical constructor
- Serialization support

### Records with Generics

```java
public record Pair<T, U>(T first, U second) { }
public record Result<T>(T value, String error) { }
public record Page<T>(List<T> content, int page, int size, long total) { }
```

---

## Sealed Classes (Java 17)

### Hierarchy Control

```java
public sealed interface Shape permits Circle, Rectangle, Triangle { }

public final class Circle implements Shape {
    private final double radius;
    public Circle(double radius) { this.radius = radius; }
}

public non-sealed class Rectangle implements Shape { }
```

### Exhaustive Switch

```java
public double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t -> t.base() * t.height() / 2;
        // No default needed - compiler verifies exhaustiveness
    };
}
```

---

## Pattern Matching

### instanceof (Java 16)

```java
if (obj instanceof String s) {
    System.out.println(s.toUpperCase());
}
// s in scope only in true branch
```

### Switch Expressions (Java 14)

```java
String dayType = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "Weekday";
    case SATURDAY, SUNDAY -> "Weekend";
    default -> throw new IllegalStateException("Invalid: " + day);
};
```

### Pattern Switch (Java 21)

```java
static String format(Object obj) {
    return switch (obj) {
        case Integer i -> "int: " + i;
        case Long l -> "long: " + l;
        case Double d -> String.format("%.2f", d);
        case String s -> "string: " + s;
        case List<?> list -> "list[" + list.size() + "]";
        case null -> "null";
        default -> obj.getClass().getSimpleName();
    };
}
```

### Record Patterns (Java 21)

```java
record Point(int x, int y) { }
record Rectangle(Point tl, Point br) { }

static void print(Rectangle r) {
    if (r instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2))) {
        System.out.printf("Rect: (%d,%d)-(%d,%d)", x1, y1, x2, y2);
    }
}
```

### Guarded Patterns (Java 21)

```java
static String grade(int score) {
    return switch (score) {
        case int s when s >= 90 -> "A";
        case int s when s >= 80 -> "B";
        case int s when s >= 70 -> "C";
        case int s when s >= 60 -> "D";
        default -> "F";
    };
}
```

---

## Virtual Threads (Java 21)

### Lightweight Threads

```java
// Platform thread: ~1MB stack, ~1ms start
// Virtual thread: ~1KB stack, ~1μs start

// Per-task executor
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
executor.submit(() -> blockingIoCall());

// Structured
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var f1 = scope.fork(() -> serviceA.call());
    var f2 = scope.fork(() -> serviceB.call());
    scope.join();
    scope.throwIfFailed();
    return new Result(f1.get(), f2.get());
}
```

### Pinning

```java
// Causes pinning (blocks carrier thread)
synchronized(lock) { ... }        // Use ReentrantLock instead
nativeMethod();                    // FFI calls
ForeignFunction.allocate();        // Memory segments

// Fix
ReentrantLock lock = new ReentrantLock();
lock.lock();
try { ... } finally { lock.unlock(); }
```

---

## Structured Concurrency (Java 21)

### Task Scopes

```java
// Shutdown on first failure
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var f1 = scope.fork(() -> serviceA.call());
    var f2 = scope.fork(() -> serviceB.call());
    scope.join();
    scope.throwIfFailed();
    return combine(f1.get(), f2.get());
}

// Shutdown on success (race)
try (var scope = new StructuredTaskScope.ShutdownOnSuccess()) {
    var f1 = scope.fork(() -> primaryService.call());
    var f2 = scope.fork(() -> backupService.call());
    scope.join();
    return scope.getResult(); // First successful
}
```

### Benefits

- Automatic error propagation
- Automatic cancellation on failure
- No thread leaks
- Clear ownership hierarchy
- Observable in thread dumps

---

## Scoped Values (Java 21)

### Alternative to ThreadLocal

```java
ScopedValue<User> currentUser = ScopedValue.newInstance();

void handle(Request req) {
    User user = authenticate(req);
    ScopedValue.runWhere(currentUser, user, () -> {
        processRequest(req); // currentUser.get() available
    });
}

// Inherited by virtual threads automatically
```

---

## String Templates (Java 21 Preview)

```java
String name = "Alice";
int age = 30;

// STR - standard interpolation
String json = STR."""
    {"name": "\{name}", "age": \{age}}
    """;

// FMT - formatted
String formatted = FMT."""
    Name: \{name:%-10s}
    Age: \{age:%03d}
    """;

// RAW - template processor
String raw = RAW."""
    SELECT * FROM users WHERE name = '\{name}'
    """;
```

---

## Sequenced Collections (Java 21)

```java
interface SequencedCollection<E> extends Collection<E> {
    void addFirst(E);
    void addLast(E);
    E getFirst();
    E getLast();
    SequencedCollection<E> reversed();
}

interface SequencedSet<E> extends Set<E>, SequencedCollection<E> { }
interface SequencedMap<K, V> extends Map<K, V> {
    SequencedMap<K, V> reversed();
    V putFirst(K, V);
    V putLast(K, V);
}
```

---

## Generational ZGC (Java 21)

```bash
-XX:+UseZGC
-XX:+ZGenerational  # Enable generational mode

# Young + Old generations
# Separate collection cycles
# Better for allocation-heavy workloads
```

---

## Migration Guide

### Java 11 → 17

- [ ] Enable strong encapsulation (`--add-opens` if needed)
- [ ] Migrate `javax.*` → `jakarta.*`
- [ ] Use records for DTOs
- [ ] Use pattern matching `instanceof`

### Java 17 → 21

- [ ] Adopt virtual threads for blocking I/O
- [ ] Use structured concurrency
- [ ] Use pattern matching switch
- [ ] Use sequenced collections
- [ ] Consider generational ZGC
- [ ] Preview: String templates (`--enable-preview`)

---

## Build Configuration

```xml
<!-- Maven -->
<properties>
    <maven.compiler.release>21</maven.compiler.release>
</properties>
<plugin>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <compilerArgs>
            <arg>--enable-preview</arg>
        </compilerArgs>
    </configuration>
</plugin>
```

```kotlin
// Gradle
java { toolchain { languageVersion.set(JavaLanguageVersion.of(21)) } }
tasks.withType<JavaCompile> { options.compilerArgs.add("--enable-preview") }
```