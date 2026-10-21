# Step-by-Step Guide to Java 21 Features

## Step 1: Setting Up Java 21

Ensure you have JDK 21 installed:

```bash
java -version
# Should output: openjdk version "21" 2023-09-19 LTS
```

If using Gradle, add to `build.gradle`:
```groovy
sourceCompatibility = '21'
targetCompatibility = '21'
```

## Step 2: Virtual Threads — Hello World

Create a simple virtual thread:

```java
public class VirtualThreadDemo {
    public static void main(String[] args) throws Exception {
        // Method 1: Using static factory
        Thread vt = Thread.startVirtualThread(() -> {
            System.out.println("Hello from " + Thread.currentThread());
        });
        vt.join();
        
        // Method 2: Using Builder
        Thread vt2 = Thread.ofVirtual()
            .name("worker")
            .start(() -> {
                System.out.println("Hello from " + Thread.currentThread().getName());
            });
        vt2.join();
        
        // Method 3: Using ExecutorService
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            executor.submit(() -> System.out.println("Hello from executor"));
        }
    }
}
```

## Step 3: Virtual Threads — Scale Testing

Test the scalability advantage:

```java
public class ScaleTest {
    public static void main(String[] args) throws Exception {
        int count = 100_000;
        
        // Platform threads — likely to fail or be very slow
        var platformStart = System.currentTimeMillis();
        try (var executor = Executors.newFixedThreadPool(1000)) {
            // This will struggle with high count
        }
        
        // Virtual threads — handles millions
        var vtStart = System.currentTimeMillis();
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < count; i++) {
                executor.submit(() -> {
                    try { Thread.sleep(1000); } catch (Exception e) {}
                });
            }
        }
        System.out.println("Virtual threads completed in " + 
            (System.currentTimeMillis() - vtStart) + "ms");
    }
}
```

## Step 4: Pattern Matching for instanceof

Transition from old-style to new-style:

```java
// Old way (before Java 16)
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}

// New way (Java 16+, instanceof pattern)
if (obj instanceof String s) {
    System.out.println(s.length());
}
```

## Step 5: Switch Pattern Matching — Type Patterns

```java
// Before Java 21 — verbose
String formatted;
if (obj instanceof Integer i) {
    formatted = "int: " + i;
} else if (obj instanceof Long l) {
    formatted = "long: " + l;
} else if (obj instanceof String s) {
    formatted = "str: " + s;
} else {
    formatted = "unknown";
}

// Java 21 — concise
String formatted = switch (obj) {
    case Integer i -> "int: " + i;
    case Long l    -> "long: " + l;
    case String s  -> "str: " + s;
    case null      -> "null";
    default        -> "unknown";
};
```

## Step 6: Record Patterns

```java
// Define records
record Point(int x, int y) {}
record Circle(Point center, double radius) {}

// Before Java 21 — manual deconstruction
Object obj = new Circle(new Point(3, 4), 5.0);
if (obj instanceof Circle) {
    Circle c = (Circle) obj;
    Point p = c.center();
    int x = p.x();
    int y = p.y();
    double r = c.radius();
    System.out.println("Circle at (" + x + "," + y + ") radius " + r);
}

// Java 21 — nested record pattern
if (obj instanceof Circle(Point(int x, int y), double r)) {
    System.out.println("Circle at (" + x + "," + y + ") radius " + r);
}
```

## Step 7: Sequenced Collections

```java
// Unified API for ordered collections
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
Deque<String> deque = new LinkedList<>(List.of("A", "B", "C"));
LinkedHashSet<String> set = new LinkedHashSet<>(List.of("A", "B", "C"));

// All three support these methods now:
System.out.println(list.getFirst());    // A
System.out.println(deque.getLast());    // C
System.out.println(set.reversed());     // [C, B, A]

list.addFirst("Z");   // [Z, A, B, C]
deque.addLast("Z");   // [A, B, C, Z]
set.removeFirst();    // removes A
```

## Step 8: String Building (String Templates were withdrawn)

> **Status**: String Templates were previewed in JDK 21/22 and withdrawn before JDK 23. No current JDK accepts the syntax — `--enable-preview` does not help for this feature, since no shipping JDK contains it. Build interpolated strings with `String.formatted`:

```java
String name = "João";
int age = 30;
String message = "Hello %s! Next year you'll be %d".formatted(name, age + 1);

// The withdrawn preview would have spelled this:
// STR."Hello \{name}! Next year you'll be \{age + 1}"

// With format specifiers
double price = 29.99;
String formatted = "Price: %10.2f".formatted(price);
```

## Step 9: Structured Concurrency

```java
import jdk.incubator.concurrent.*;

public class StructuredDemo {
    record Result(String user, String address) {}
    
    Result process(int userId) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            Future<String> user = scope.fork(() -> fetchUser(userId));
            Future<String> addr = scope.fork(() -> fetchAddress(userId));
            
            scope.join();
            scope.throwIfFailed();
            
            return new Result(user.resultNow(), addr.resultNow());
        }
    }
    
    private String fetchUser(int id) { return "User" + id; }
    private String fetchAddress(int id) { return "Addr" + id; }
}
```

## Step 10: Combining Features

The real power comes when features are combined:

```java
// Virtual threads + Pattern matching + Records
record Order(int id, String item, double price) {}

public void processOrders(Stream<Object> items) {
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        items.forEach(item -> executor.submit(() -> {
            String result = switch (item) {
                case Order(int id, String name, double price) when price > 100 
                    -> processPriorityOrder(id, name, price);
                case Order(var id, var name, var price) 
                    -> processRegularOrder(id, name, price);
                case String s -> "Received string: " + s;
                default -> "Unknown item";
            };
            System.out.println(result);
        }));
    }
}
```

This demonstrates how virtual threads simplify concurrency while pattern matching and records make data handling declarative and type-safe.
