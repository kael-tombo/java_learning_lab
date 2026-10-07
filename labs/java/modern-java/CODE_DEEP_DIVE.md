# Code Deep Dive — Modern Java 17-25 (modern-java)

Annotated Java 17+ snippets for records, sealed classes, pattern matching, virtual threads, switch expressions. Paste into `src/main/java`.

## Snippet 1: records

Records (JEP 395, final in JDK 16) are immutable data carrier classes that automatically generate `equals`, `hashCode`, `toString`, and accessor methods. They reduce boilerplate and make data modeling more concise. The snippet below defines a `Point` record with a compact constructor for validation and a derived method.

```java
// modern-java snippet 1: records
public class Records {
    record Point(int x, int y) {
        Point {
            if (x < 0 || y < 0) {
                throw new IllegalArgumentException("Coordinates must be non-negative");
            }
        }

        double distanceToOrigin() {
            return Math.sqrt(x * x + y * y);
        }
    }

    public static void main(String[] args) {
        Point p = new Point(3, 4);
        System.out.println("Point: " + p);
        System.out.println("x: " + p.x() + ", y: " + p.y());
        System.out.println("Distance to origin: " + p.distanceToOrigin());
        try {
            new Point(-1, 5);
        } catch (IllegalArgumentException e) {
            System.out.println("Validation caught: " + e.getMessage());
        }
    }
}
```

Observed output:
```
Point: Point[x=3, y=4]
x: 3, y: 4
Distance to origin: 5.0
Validation caught: Coordinates must be non-negative
```

Pitfall: Records are shallowly immutable — if a record component is a mutable object (e.g., a `List` or array), the record's state can still be modified through that reference. For true immutability, use immutable collections (`List.of`, `Map.of`) or defensive copies in the compact constructor.

## Snippet 2: sealed classes

Sealed classes (JEP 409, final in JDK 17) restrict which classes can extend or implement them, enabling exhaustive pattern matching. The permitted subclasses must be in the same module or package. The snippet below defines a sealed `Shape` interface with `Circle` and `Rectangle` records.

```java
// modern-java snippet 2: sealed classes
public class SealedClasses {
    sealed interface Shape permits Circle, Rectangle {}

    record Circle(double radius) implements Shape {}

    record Rectangle(double width, double height) implements Shape {}

    static double area(Shape s) {
        return switch (s) {
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Rectangle r -> r.width() * r.height();
        };
    }

    public static void main(String[] args) {
        Shape circle = new Circle(2.0);
        Shape rect = new Rectangle(3.0, 4.0);
        System.out.println("Circle area: " + area(circle));
        System.out.println("Rectangle area: " + area(rect));
    }
}
```

Observed output:
```
Circle area: 12.566370614359172
Rectangle area: 12.0
```

Pitfall: Sealed classes require all permitted subclasses to be known at compile time. If you need to add a new subclass later (e.g., a plugin architecture), you must modify the sealed hierarchy. This makes sealed classes unsuitable for extensible frameworks where third parties need to add implementations.

## Snippet 3: pattern matching instanceof/switch

Pattern matching for `instanceof` (JEP 394, final in JDK 16) and switch (JEP 441, final in JDK 21) eliminates verbose casting and enables type-safe destructuring. The snippet below demonstrates both instanceof patterns and switch patterns with record deconstruction.

```java
// modern-java snippet 3: pattern matching instanceof/switch
public class PatternMatching {
    public static void main(String[] args) {
        Object obj = "hello world";

        if (obj instanceof String s && s.length() > 5) {
            System.out.println("Long string: " + s);
        }

        Object num = 42;
        String result = switch (num) {
            case Integer i -> "Integer: " + i;
            case String s -> "String: " + s;
            case Double d -> "Double: " + d;
            default -> "Other: " + num;
        };
        System.out.println(result);

        Object pair = new int[]{1, 2};
        if (pair instanceof int[] arr && arr.length == 2) {
            System.out.println("Array pair: " + arr[0] + ", " + arr[1]);
        }
    }
}
```

Observed output:
```
Long string: hello world
Integer: 42
Array pair: 1, 2
```

Pitfall: Switch patterns are not exhaustive by default — if you omit the `default` clause and a new permitted subtype is added, the compiler will catch it for sealed types but not for non-sealed types. For non-sealed types, always include a `default` clause or use `@SuppressWarnings` deliberately. Also, pattern matching in switch can throw `NullPointerException` if the selector is null and no `case null` is present.

## Snippet 4: text blocks

Text blocks (JEP 378, final in JDK 15) are multi-line string literals that preserve formatting and reduce escaping. They are ideal for JSON, SQL, HTML, and other structured text. The snippet below demonstrates text blocks with automatic indentation stripping.

```java
// modern-java snippet 4: text blocks
public class TextBlocks {
    public static void main(String[] args) {
        String json = """
            {
                "name": "Java",
                "version": 21,
                "features": [
                    "records",
                    "sealed classes",
                    "pattern matching"
                ]
            }
            """;

        String sql = """
            SELECT id, name, email
            FROM users
            WHERE active = true
            ORDER BY name
            """;

        System.out.println("JSON:");
        System.out.println(json);
        System.out.println("SQL:");
        System.out.println(sql);
    }
}
```

Observed output:
```
JSON:
{
    "name": "Java",
    "version": 21,
    "features": [
        "records",
        "sealed classes",
        "pattern matching"
    ]
}

SQL:
SELECT id, name, email
FROM users
WHERE active = true
ORDER BY name
```

Pitfall: Text blocks strip incidental whitespace based on the closing delimiter position, but they preserve all whitespace before the closing `"""`. If the closing delimiter is indented, that indentation is included in every line. Also, text blocks cannot be used for single-line strings — use regular string literals for those to avoid unnecessary overhead.

## Snippet 5: virtual threads

Virtual threads (JEP 444, final in JDK 21) are lightweight threads managed by the JVM that enable massive concurrency without the overhead of platform threads. They are ideal for I/O-bound workloads. The snippet below creates 100,000 virtual threads that each sleep briefly.

```java
// modern-java snippet 5: virtual threads
import java.time.Duration;
import java.util.concurrent.Executors;
import java.util.stream.IntStream;

public class VirtualThreads {
    public static void main(String[] args) throws Exception {
        long start = System.currentTimeMillis();
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            IntStream.range(0, 100_000).forEach(i -> {
                executor.submit(() -> {
                    Thread.sleep(Duration.ofMillis(10));
                    return i;
                });
            });
        }
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("Completed 100,000 virtual threads in " + elapsed + " ms");
    }
}
```

Observed output:
```text
Completed 100,000 virtual threads in 9866 ms
```

Pitfall: Virtual threads are not faster than platform threads for CPU-bound tasks — they are designed for I/O-bound workloads where threads spend most of their time blocked. Also, `synchronized` blocks and native calls can pin the carrier thread, reducing concurrency. Use `ReentrantLock` instead of `synchronized` for code that runs on virtual threads.

## Snippet 6: structured concurrency

Structured concurrency (JEP 453/462/480/499/505, preview in JDK 21-25) treats groups of concurrent tasks as a single unit of work, ensuring that task lifetimes are bounded by the enclosing scope. The snippet below uses `StructuredTaskScope.ShutdownOnFailure` to fetch a user and an order concurrently, failing fast if either fails.

**Note:** This snippet uses preview features. Compile with `javac --release 23 --enable-preview` and run with `java --enable-preview`. The API changed shape in JDK 25 (JEP 505): `StructuredTaskScope.open(Joiner.<T>allSuccessfulOrThrow())` and `scope.join()` returns a stream of subtasks. JDK 21-24 used `new StructuredTaskScope.ShutdownOnFailure()` and `join().throwIfFailed()`.

```java
// modern-java snippet 6: structured concurrency
import java.util.concurrent.ExecutionException;
import java.util.concurrent.StructuredTaskScope;

public class StructuredConcurrency {
    record User(String name) {}
    record Order(String id) {}
    record Combined(User user, Order order) {}

    static User fetchUser() throws InterruptedException {
        Thread.sleep(100);
        return new User("Alice");
    }

    static Order fetchOrder() throws InterruptedException {
        Thread.sleep(100);
        return new Order("ORD-123");
    }

    public static void main(String[] args) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var userTask = scope.fork(() -> fetchUser());
            var orderTask = scope.fork(() -> fetchOrder());
            scope.join().throwIfFailed();
            Combined result = new Combined(userTask.get(), orderTask.get());
            System.out.println("Result: " + result);
        }
    }
}
```

Observed output (run with `java --enable-preview StructuredConcurrency`):
```
Result: Combined[user=User[name=Alice], order=Order[id=ORD-123]]
```

Pitfall: Structured concurrency requires all tasks to complete before the scope closes. If a task hangs indefinitely, the entire scope hangs. Always use timeouts with `scope.joinUntil(Instant.now().plusSeconds(5))` or implement cancellation within the task. Also, the preview API has changed across JDK versions — code written for JDK 21 will not compile on JDK 25 without modification.
