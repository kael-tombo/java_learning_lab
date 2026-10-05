# THEORY — Java Version Evolution

## Overview

Java's 6-month release cadence (since Java 10) brings predictable feature delivery. LTS releases every 3 years.

---

## Release Timeline

| Version | Date | Type | Key Features |
|---------|------|------|--------------|
| Java 8 | Mar 2014 | LTS | Lambdas, Streams, Optional, Date/Time, Nashorn |
| Java 9 | Sep 2017 | — | Modules (JPMS), JShell, Reactive Streams |
| Java 10 | Mar 2018 | — | `var`, GC improvements, Docker awareness |
| Java 11 | Sep 2018 | LTS | HTTP Client, `var` in lambda, String methods, Epsilon GC |
| Java 12 | Mar 2019 | — | Switch expressions (preview), Shenandoah GC |
| Java 13 | Sep 2019 | — | Text blocks (preview), CDS improvements |
| Java 14 | Mar 2020 | — | Records (preview), Pattern matching instanceof, NVM |
| Java 15 | Sep 2020 | — | Sealed classes (preview), Text blocks, ZGC |
| Java 16 | Mar 2021 | — | Records, Pattern matching, Vector API (incubator) |
| Java 17 | Sep 2021 | LTS | Sealed classes, Pattern matching, Strong encapsulation |
| Java 18 | Mar 2022 | — | Simple web server, UTF-8 default, Vector API |
| Java 19 | Sep 2022 | — | Virtual threads (preview), Structured concurrency (preview) |
| Java 20 | Mar 2023 | — | Pattern matching switch, Virtual threads (2nd preview) |
| Java 21 | Sep 2023 | LTS | **Virtual threads, Structured concurrency, Pattern matching switch, String templates (preview), Sequenced collections, Generational ZGC** |
| Java 22 | Mar 2024 | — | FFI (final), Stream gatherers (preview), JEP 447 |
| Java 23 | Sep 2024 | — | Stream gatherers (2nd preview), Module import decl. (preview) |
| Java 24 | Mar 2025 | — | — |
| Java 25 | Sep 2025 | LTS | — |

---

## Key Feature Evolution

### Language Syntax

```java
// Java 8: Anonymous classes
Runnable r = new Runnable() { public void run() { System.out.println("Hi"); } };

// Java 8: Lambdas
Runnable r = () -> System.out.println("Hi");

// Java 10: var
var list = new ArrayList<String>();
var stream = list.stream();

// Java 14: Switch expressions
String result = switch (day) {
    case MONDAY, FRIDAY -> "Work";
    case SATURDAY, SUNDAY -> "Weekend";
    default -> "Midweek";
};

// Java 16: Records
record Point(int x, int y) { }

// Java 17: Sealed classes
sealed interface Shape permits Circle, Square { }

// Java 21: Pattern matching switch
return switch (obj) {
    case String s -> s.length();
    case Integer i -> i;
    case null -> 0;
    default -> -1;
};

// Java 21: String templates (preview)
String json = STR."""
    {"name": "\{name}", "age": \{age}}
    """;
```

### Collections & Streams

```java
// Java 9: Factory methods
List.of(1, 2, 3)
Set.of("a", "b")
Map.of("k1", "v1", "k2", "v2")

// Java 10: Unmodifiable collectors
list.stream().collect(toUnmodifiableList())

// Java 12: Collectors.teeing
stream.collect(teeing(
    mapping(e -> e.getName(), toList()),
    counting(),
    (names, count) -> new Summary(names, count)
))

// Java 16: Stream.toList()
list.stream().filter(...).toList()

// Java 21: Sequenced collections
interface SequencedCollection<E> {
    void addFirst(E); void addLast(E);
    E getFirst(); E getLast();
    SequencedCollection<E> reversed();
}
```

### Concurrency

```java
// Java 8: CompletableFuture
CompletableFuture.supplyAsync(() -> fetch())
    .thenApply(this::process)
    .thenAccept(this::save);

// Java 19-21: Virtual threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> blockingCall());
}

// Java 21: Structured concurrency
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var f1 = scope.fork(() -> serviceA.call());
    var f2 = scope.fork(() -> serviceB.call());
    scope.join();
    scope.throwIfFailed();
    return new Result(f1.get(), f2.get());
}

// Java 21: Scoped values (alternative to ThreadLocal)
ScopedValue<User> currentUser = ScopedValue.newInstance();
ScopedValue.runWhere(currentUser, user, () -> handler.handle(request));
```

### GC Evolution

| GC | Introduced | Target |
|----|------------|--------|
| Parallel | Java 8 | Throughput |
| G1 | Java 9 (default) | Balanced |
| ZGC | Java 11 (exp) → 15 | Low latency, large heaps |
| Shenandoah | Java 12 | Low latency |
| Generational ZGC | Java 21 | Low latency + generational |

---

## Migration Checklist

### Java 8 → 11 (LTS to LTS)

- [ ] Replace `java.xml.bind` (JAXB) - removed
- [ ] Replace `java.xml.ws` (JAX-WS) - removed
- [ ] Update `java.se.ee` modules
- [ ] Migrate to `java.net.http.HttpClient`
- [ ] Use `var` for local variables
- [ ] Replace `Collection.removeIf` with `Predicate`

### Java 11 → 17 (LTS to LTS)

- [ ] Enable strong encapsulation (`--add-opens` if needed)
- [ ] Migrate from `javax.*` to `jakarta.*` (EE 9+)
- [ ] Update GC tuning (G1 default)
- [ ] Use sealed classes for domain modeling
- [ ] Use pattern matching `instanceof`
- [ ] Use records for DTOs

### Java 17 → 21 (LTS to LTS)

- [ ] Adopt virtual threads for blocking I/O
- [ ] Use structured concurrency
- [ ] Use pattern matching switch
- [ ] Use sequenced collections
- [ ] Consider generational ZGC for large heaps
- [ ] Preview: String templates (`--enable-preview`)

---

## Deprecation & Removal

```java
// Java 9: Deprecated
@Deprecated(since = "9", forRemoval = true)
public final void stop() { }

// Java 11: Removed
// sun.misc.Unsafe (use VarHandles)
// com.sun.* internal APIs

// Java 17: Strong encapsulation
// Illegal reflective access warnings → errors
// Need: --add-opens java.base/java.lang=ALL-UNNAMED

// Java 21: Finalization deprecated
// Override finalize() → Cleaner API
Cleaner cleaner = Cleaner.create();
cleaner.register(this, () -> cleanup());
```

---

## Build Tool Configuration

### Maven

```xml
<properties>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
    <maven.compiler.release>21</maven.compiler.release>
</properties>

<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.13.0</version>
    <configuration>
        <release>21</release>
        <compilerArgs>
            <arg>--enable-preview</arg>
        </compilerArgs>
    </configuration>
</plugin>
```

### Gradle

```kotlin
java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

tasks.withType<JavaCompile> {
    options.compilerArgs.add("--enable-preview")
}
```

---

## Compatibility

| From → To | Binary | Source | Behavioral |
|-----------|--------|--------|------------|
| 8 → 11 | ✅ | ⚠️ modules | ⚠️ GC, TLS |
| 11 → 17 | ✅ | ⚠️ encapsulation | ⚠️ defaults |
| 17 → 21 | ✅ | ✅ | ⚠️ virtual threads |

**Rule**: Compile with `--release N` for target version N compatibility.