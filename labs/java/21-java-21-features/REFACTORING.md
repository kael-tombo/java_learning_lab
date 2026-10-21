# Refactoring with Java 21 Features

## Refactoring Concurrency: From Platform Threads to Virtual Threads

### Step 1: Replace Explicit Thread Creation
```java
// Before — manual thread management
Thread t = new Thread(() -> processRequest());
t.start();
try { t.join(5000); } catch (InterruptedException e) {}

// After — virtual thread
Thread t = Thread.startVirtualThread(() -> processRequest());
try { t.join(5000); } catch (InterruptedException e) {}
```

### Step 2: Replace Thread Pools
```java
// Before — fixed thread pool (limited scalability)
ExecutorService executor = Executors.newFixedThreadPool(200);
executor.submit(task);

// After — virtual thread per task (unlimited scalability)
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
executor.submit(task);
```

### Step 3: Replace Reactive/Async Code
```java
// Before — reactive chain (difficult to debug)
Mono<User> userMono = Mono.fromCallable(() -> userService.findById(id));
Mono<Address> addrMono = Mono.fromCallable(() -> addressService.findByUserId(id));
return Mono.zip(userMono, addrMono)
    .map(tuple -> new Response(tuple.getT1(), tuple.getT2()));

// After — synchronous code with virtual threads
User user = userService.findById(id);
Address addr = addressService.findByUserId(id);
return new Response(user, addr);
```

## Refactoring Conditional Logic: instanceof to Pattern Matching

### Step 4: Type Checking
```java
// Before — verbose instanceof+cast
if (shape instanceof Circle) {
    Circle c = (Circle) shape;
    double area = Math.PI * c.radius() * c.radius();
} else if (shape instanceof Rectangle) {
    Rectangle r = (Rectangle) shape;
    double area = r.width() * r.height();
}

// After — pattern matching
if (shape instanceof Circle c) {
    double area = Math.PI * c.radius() * c.radius();
} else if (shape instanceof Rectangle r) {
    double area = r.width() * r.height();
}
```

### Step 5: Type Dispatching with Switch
```java
// Before — if-else chain
String result;
if (obj instanceof Integer i) {
    result = "Int: " + i;
} else if (obj instanceof String s) {
    result = "Str: " + s;
} else {
    result = "Unknown";
}

// After — switch expression
String result = switch (obj) {
    case Integer i -> "Int: " + i;
    case String s  -> "Str: " + s;
    default        -> "Unknown";
};
```

## Refactoring Records: From POJOs to Records

### Step 6: Simple Data Carriers
```java
// Before — boilerplate POJO
public class Point {
    private final int x;
    private final int y;
    public Point(int x, int y) { this.x = x; this.y = y; }
    public int getX() { return x; }
    public int getY() { return y; }
    public boolean equals(Object o) { /* 20 lines */ }
    public int hashCode() { /* 10 lines */ }
    public String toString() { /* 5 lines */ }
}

// After — record
record Point(int x, int y) {}
```

## Refactoring Data Access: Simple Iteration to Sequenced Collections

### Step 7: Getting Last Element
```java
// Before — various workarounds
List<String> list = getItems();
String last = list.get(list.size() - 1);

// After — uniform API
SequencedCollection<String> seq = (SequencedCollection<String>) getItems();
String last = seq.getLast();
```

## Refactoring String Building: Concatenation to Safe Composition

> **Status**: The JVM 21/22 previewed String Templates (of the form `STR."..."`) and later withdrew them before JDK 23. The refactor below targets what compiles today.

### Step 8: Safe String Composition
```java
// Before — error-prone concatenation
String html = "<div class='" + cssClass + "'>" + content + "</div>";

// After — composed with formatting (never embed raw user values)
String html = "<div class='%s'>%s</div>".formatted(cssClass, content);

// The withdrawn preview would have spelled this:
// STR."<div class='\{cssClass}'>\{content}</div>"
```

## Refactoring Concurrency: Unstructured to Structured

### Step 9: Task Coordination
```java
// Before — unstructured, error-prone
Future<String> f1 = executor.submit(() -> fetchUser(id));
Future<String> f2 = executor.submit(() -> fetchAddress(id));
try {
    String user = f1.get();
    String addr = f2.get();
} catch (Exception e) {
    // Need to manually cancel remaining tasks
    f1.cancel(true);
    f2.cancel(true);
}

// After — structured, automatic cleanup
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> f1 = scope.fork(() -> fetchUser(id));
    Future<String> f2 = scope.fork(() -> fetchAddress(id));
    scope.join();
    scope.throwIfFailed();
    return new Response(f1.resultNow(), f2.resultNow());
}
```

## Migration Checklist

1. **Identify hotspots**: Find areas with high concurrency or complex if-else chains
2. **Enable preview features**: Configure build for Java 21 with `--enable-preview` where needed
3. **Test thoroughly**: Virtual threads change scheduling behavior; test with production-like loads
4. **Replace synchronized**: Swap `synchronized` for `ReentrantLock` to avoid pinning
5. **Remove ThreadLocal**: Replace with `ScopedValue` where appropriate
6. **Refactor gradually**: Migrate one service or module at a time
