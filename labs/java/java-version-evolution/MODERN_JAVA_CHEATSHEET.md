# Modern Java Cheatsheet (Java 8-27)

> Quick reference for modern Java features with code snippets and interview context.

---

## Records (Java 14 preview, Java 16 stable)

**What**: Compact data carrier with auto-generated constructor, accessors, equals, hashCode, toString.

`java
public record Point(int x, int y) {}
Point p = new Point(3, 4);
int x = p.x(); // accessor, not getX()
`

**When to use**: DTOs, value objects, multi-value returns, immutable data carriers.
**When NOT to use**: JPA entities, classes needing mutation, classes needing inheritance.
**Interview context**: "Records eliminated 50 lines of boilerplate from our DTOs."

---

## Sealed Classes (Java 15 preview, Java 17 stable)

**What**: Restricts which classes can extend/implement a type using permits clause.

`java
public sealed interface Shape permits Circle, Rectangle, Triangle {}
public final class Circle implements Shape {}
public final class Rectangle implements Shape {}
public final class Triangle implements Shape {}
`

**When to use**: Domain modeling, algebraic data types, exhaustive pattern matching.
**Interview context**: "Sealed classes make domain invariants compiler-checked. No more runtime errors from unexpected subtypes."

---

## Pattern Matching for instanceof (Java 14 preview, Java 16 stable)

**What**: Combines type check, cast, and variable binding into one expression.

`java
if (obj instanceof String s) {
    System.out.println(s.length());
}
`

**When to use**: Any instanceof check followed by a cast.
**Interview context**: "This eliminated hundreds of redundant casts in our codebase."

---

## Pattern Matching for switch (Java 17 preview, Java 21 stable)

**What**: Switch on type patterns with guards, exhaustiveness checking with sealed types.

`java
String formatted = switch (obj) {
    case Integer i when i > 0 -> "Positive: " + i;
    case Integer i -> "Non-positive: " + i;
    case String s -> "String: " + s;
    case null -> "null";
    default -> "Other: " + obj;
};
`

**When to use**: Type-based dispatch, visitor pattern replacement.
**Interview context**: "Pattern matching for switch replaces the visitor pattern with compiler-verified exhaustiveness."

---

## Record Patterns (Java 19 preview, Java 21 stable)

**What**: Deconstruct records directly in pattern matching.

`java
if (obj instanceof Point(int x, int y)) {
    System.out.println("Point at " + x + "," + y);
}

// Nested deconstruction
if (obj instanceof Line(Point(int x1, int y1), Point(int x2, int y2))) {
    // use coordinates directly
}
`

**When to use**: Processing nested data structures, functional-style data transformation.
**Interview context**: "Record patterns make data extraction type-safe and concise, especially with pattern matching for switch."

---

## Virtual Threads (Java 19 preview, Java 21 stable)

**What**: Lightweight JVM-managed threads (Project Loom) that multiplex on OS threads.

`java
// Virtual thread per task executor
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> executor.submit(() -> {
        Thread.sleep(1000);  // yields carrier thread
        return process();
    }));
}

// Direct creation
Thread vThread = Thread.ofVirtual().name("handler").start(() -> handle());
`

**When to use**: I/O-heavy workloads, web servers, microservices, API gateways.
**When NOT to use**: CPU-bound computation (use platform threads = core count).
**Interview context**: "Virtual threads let us handle 1M concurrent connections without rewriting our thread pool code."

---

## Sequenced Collections (Java 21)

**What**: Common interface for collections with a defined encounter order.

`java
SequencedCollection<String> seq = new LinkedHashSet<>();
seq.addFirst("a");
seq.addLast("z");
String first = seq.getFirst(); // "a"
SequencedCollection<String> reversed = seq.reversed();
`

**When to use**: When order matters and you need first/last element operations.
**Interview context**: "Sequenced Collections standardized getFirst/getLast across all ordered collection types."

---

## String Templates (JDK 21–22 preview, withdrawn before JDK 23)

**What**: String interpolation with template processors is NOT available in any shipping JDK. String Templates were previewed in JDK 21/22 and then withdrawn before JDK 23 — no current JDK accepts them, even with `--enable-preview`. Do not use `STR."..."` syntax.

**The safe interpolation you get today — `String.formatted` and concatenation**:

`java
String name = "Alice";
int age = 30;
String message = "Hello %s, you are %d years old".formatted(name, age);

// With format specifiers
String price = "Price: %-10.2f".formatted(total);
`

**Interview context**: "String Templates aimed to eliminate string concatenation bugs in SQL/HTML generation, but the experts group declined to continue the preview after JDK 22, so Java still relies on `String.formatted` and text blocks for readable string construction."

---

## Text Blocks (Java 13 preview, Java 15 stable)

**What**: Multiline string literals with triple quotes.

`java
String json = """
    {
        "name": "John",
        "age": 30,
        "address": {
            "city": "New York"
        }
    }
    """;
`

**When to use**: Embedding SQL, JSON, XML, HTML, or any multiline text in Java.
**Interview context**: "Text blocks made our embedded SQL readable without concatenation pollution."

---

## Switch Expressions (Java 12 preview, Java 14 stable)

**What**: Arrow-syntax switch that can be used as an expression with yield.

`java
String type = switch (day) {
    case "MONDAY", "TUESDAY" -> "Work day";
    case "SATURDAY", "SUNDAY" -> "Weekend";
    default -> {
        int len = day.length();
        yield "Other (" + len + " chars)";
    }
};
`

**When to use**: Replacing if-else chains, assigning values based on conditions.
**Interview context**: "Switch expressions eliminated fall-through bugs and made our branching logic declarative."

---

## Helpful NullPointerExceptions (Java 14)

**What**: JVM pinpoints exactly which variable was null in an NPE message.

`java
// Before: "Cannot read field 'name' because 'order.customer' is null"
// After: "Cannot read field 'name' because 'order.customer' is null (reason: order is null)"
order.customer.getName();  // tells you order was null, not customer
`

**When to use**: Not a feature to enable — it's automatic in Java 14+.
**Interview context**: "Helpful NPE messages saved hours of debugging by telling us exactly which reference was null."

---

## var (Java 10)

**What**: Local variable type inference.

`java
var list = new ArrayList<String>();  // inferred ArrayList<String>
var entry = Map.entry("key", "value");  // inferred Map.Entry<String, String>

// Valid in: local variables, for-each, for-loop indices
// Invalid: fields, method params, return types, without initializer
`

**When to use**: When the right-hand side makes the type obvious. Avoid when type is unclear.
**Interview context**: "Var improves readability when the type is obvious from context, but we restrict it in our style guide to avoid obscuring intent."

---

## Stream API refinements

`java
// Java 9: takeWhile, dropWhile, ofNullable, iterate with predicate
stream.takeWhile(x -> x > 0);
stream.dropWhile(x -> x > 0);
Stream.ofNullable(someObject);

// Java 11: toArray with method reference
String[] arr = list.stream().toArray(String[]::new);

// Java 16: toList() (immutable list)
List<String> result = stream.toList();

// Java 22 preview: Stream Gatherers
stream.gather(Gatherers.windowFixed(3));
`

---

## Immutable Collection Factories (Java 9)

`java
List<String> list = List.of("a", "b", "c");
Set<Integer> set = Set.of(1, 2, 3);
Map<String, Integer> map = Map.of("a", 1, "b", 2);
Map<String, Integer> multi = Map.ofEntries(
    Map.entry("a", 1),
    Map.entry("b", 2)
);
`

**When to use**: Defensive copies, constant collections, configuration.
**Interview context**: "List.of replaced Arrays.asList and Collections.unmodifiableList for most use cases."

---

## Optional refinements

`java
// Java 8: Optional creation
Optional<String> opt = Optional.of("value");
Optional<String> empty = Optional.empty();
Optional<String> nullable = Optional.ofNullable(maybeNull);

// Java 9: ifPresentOrElse, or, stream
opt.ifPresentOrElse(
    v -> System.out.println(v),
    () -> System.out.println("empty")
);

// Java 10: orElseThrow (no-arg version)
String v = opt.orElseThrow();

// Java 11: isEmpty
boolean empty = opt.isEmpty();
`

---

## HttpClient (Java 9 incubator, Java 11 stable)

`java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .header("Accept", "application/json")
    .timeout(Duration.ofSeconds(30))
    .GET()
    .build();

HttpResponse<String> response = client.send(request, 
    HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());

// Async
client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
    .thenApply(HttpResponse::body)
    .thenAccept(System.out::println);
`

**When to use**: HTTP clients, REST API calls, web service communication.
**Interview context**: "HttpClient is reactive, supports HTTP/2, WebSockets, and doesn't need third-party libraries for basic HTTP."

---

## Compact Strings (Java 9)

**What**: String uses byte[] instead of char[]. Latin-1 characters stored as single byte, UTF-16 only when needed.

`java
// Before: char[20] = 40 bytes per String
// After: byte[20] = 20 bytes (Latin-1) or 40 bytes (UTF-16)
`

**Interview context**: "Compact strings reduced heap usage by 10-15% in our application with zero code changes."

---

## GC Evolution

`java
// Java 8 default: G1 (replaced Parallel in some configs)
// Java 9 default: G1 (replaced CMS)
// Java 11: ZGC (experimental), Epsilon (no-op GC)
// Java 12: Shenandoah (experimental)
// Java 15: ZGC + Shenandoah production-ready
// Java 21: Generational ZGC (preview)
// Java 24+: Generational ZGC default

// Common flags:
// -XX:+UseZGC
// -XX:+UseShenandoahGC
// -XX:+UseG1GC
// -XX:+UseParallelGC
`

**Interview context**: "ZGC sub-millisecond pauses transformed our user-facing latency profile without code changes."

---

## Module System (Java 9)

`java
// module-info.java
module com.myapp {
    requires java.sql;
    requires org.slf4j;
    exports com.myapp.api;
    exports com.myapp.dto;
    opens com.myapp.internal to com.fasterxml.jackson.databind;
}
`

**When to use**: New applications, library authors, large monorepos needing encapsulation.
**Interview context**: "Modules prevent accidental internal API usage and make dependency graphs explicit."

---

## Structured Concurrency (Java 19 incubator, Java 25 stable)

`java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> user = scope.fork(() -> fetchUser(id));
    Future<Order> order = scope.fork(() -> fetchOrder(id));
    
    scope.join();          // wait for all
    scope.throwIfFailed(); // propagate failures
    
    return new Response(user.resultNow(), order.resultNow());
}
`

**When to use**: Managing multiple concurrent tasks with clear lifecycle and error propagation.
**Interview context**: "Structured concurrency ensures no task is leaked and errors are propagated deterministically."

---

## Scoped Values (Java 20 incubator, Java 25 stable)

**What**: Immutable thread-local values that don't leak across virtual threads.

`java
final static ScopedValue<String> USER_ID = ScopedValue.newInstance();

ScopedValue.where(USER_ID, "user123", () -> {
    // Inside this scope, USER_ID.get() returns "user123"
    processRequest();
});
`

**When to use**: Context propagation (user ID, request ID, tenant ID) in virtual thread environments.
**Interview context**: "Scoped values solve the ThreadLocal memory leak problem with virtual threads."

---

## Value Objects / Inline Classes (Java 25 preview, Java 27 stable)

**What**: Classes without identity — value-based equality, flattened in memory.

`java
inline class Money {
    private final long cents;
    
    public Money(long cents) {
        this.cents = cents;
    }
    
    public Money add(Money other) {
        return new Money(this.cents + other.cents);
    }
}

// No identity: == compares by value
Money a = new Money(100);
Money b = new Money(100);
boolean eq = (a == b);  // true (value comparison)
`

**When to use**: Performance-critical data types, primitives with behavior, math types.
**Interview context**: "Value types eliminated boxing overhead in our high-throughput trading engine."

---

## Universal Generics (Java 25 preview, Java 27 stable)

**What**: Generics over primitives and value types.

`java
ArrayList<int> numbers = new ArrayList<>();
numbers.add(42);
int x = numbers.get(0);  // no boxing!

HashMap<String, double> scores = new HashMap<>();
`

**When to use**: Collections of primitives, performance-sensitive data processing.
**Interview context**: "Universal generics mean List<double> is as efficient as double[] with type safety."

---

## AOT Compilation / Project Leyden (Java 24+ preview)

**What**: Ahead-of-time compilation for instant startup.

`java
// java.base compiled AOT for near-instant startup
// jlink creates optimized runtime images
`

**Interview context**: "AOT compilation reduces startup from seconds to milliseconds, making Java competitive with Node.js and Go for serverless."

---

## Cheatsheet Summary: Feature by Version

| Feature | Preview | Stable | JEP |
|---------|---------|--------|-----|
| Lambda expressions | — | Java 8 | 126 |
| Stream API | — | Java 8 | 107 |
| Optional | — | Java 8 | 172 |
| Date/Time API | — | Java 8 | 310 |
| Default methods | — | Java 8 | 126 |
| Module System | — | Java 9 | 261 |
| Collection factories | — | Java 9 | 269 |
| var | — | Java 10 | 286 |
| HTTP Client | Java 9 | Java 11 | 321 |
| Text blocks | Java 13 | Java 15 | 378 |
| Switch expressions | Java 12 | Java 14 | 361 |
| Records | Java 14 | Java 16 | 395 |
| Pattern matching instanceof | Java 14 | Java 16 | 394 |
| Sealed classes | Java 15 | Java 17 | 409 |
| Pattern matching switch | Java 17 | Java 21 | 441 |
| Record patterns | Java 19 | Java 21 | 440 |
| Virtual threads | Java 19 | Java 21 | 444 |
| Sequenced collections | — | Java 21 | 431 |
| String templates | Java 21 | Withdrawn before Java 23 — never shipped | 430/459 |
| Stream Gatherers | Java 22 | Java 25 | 461 |
| Structured concurrency | Java 19 | Java 25 | 462 |
| Scoped values | Java 20 | Java 25 | 463 |
| Value objects | Java 25 | Java 27 | 401 |
| Universal generics | Java 25 | Java 27 | 401 |
| AOT compilation | Java 24 | Java 27 | Leyden |
