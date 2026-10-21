# Architectural Patterns with Java 21 Features

## Virtual Threads: Thread-Per-Request Architecture

### Traditional Model (Fixed Thread Pool)
```
HTTP Requests → [   Thread Pool (N)   ] → Process → Response
                ┌─ Thread-1 ─┐
                ├─ Thread-2 ─┤
                ├─ ...       ┤
                └─ Thread-N ─┘
```
Limitation: N = ~200-500 threads maximum. Queue backs up under load.

### Virtual Thread Model (Thread-Per-Request)
```
HTTP Requests → [   Virtual Thread per Request   ] → Process → Response
                ┌─ VT-1 (Carrier-1) ─┐
                ├─ VT-2 (Carrier-1) ─┤
                ├─ VT-3 (Carrier-2) ─┤
                ├─ VT-4 (Carrier-3) ─┤
                ├─ VT-5 (Carrier-2) ─┤
                ├─ ...                ┤
                └─ VT-M (Carrier-N) ─┘
```
Benefit: M virtual threads share N carrier threads (N = CPU cores).

### Architectural Implication
Virtual threads enable a return to simple thread-per-request architecture without reactive backends. Services can handle 10x-100x more concurrent connections with the same hardware.

## Pattern Matching: Dispatch Architecture

### Before: Visitor Pattern (Complex)
```java
interface ShapeVisitor<R> {
    R visit(Circle c);
    R visit(Rectangle r);
    R visit(Triangle t);
}

class AreaVisitor implements ShapeVisitor<Double> {
    public Double visit(Circle c) { return Math.PI * c.r() * c.r(); }
    public Double visit(Rectangle r) { return r.w() * r.h(); }
    public Double visit(Triangle t) { return 0.5 * t.b() * t.h(); }
}
```

### After: Pattern Matching Switch (Simple)
```java
record Circle(double r) implements Shape {}
record Rectangle(double w, double h) implements Shape {}
record Triangle(double b, double h) implements Shape {}

double area(Shape s) {
    return switch (s) {
        case Circle(double r) -> Math.PI * r * r;
        case Rectangle(var w, var h) -> w * h;
        case Triangle(var b, var h) -> 0.5 * b * h;
    };
}
```

Architecturally, pattern matching replaces the Visitor pattern for many use cases, reducing coupling between types and operations.

## Sequenced Collections: Pipeline Architecture

Sequenced collections enable clean pipeline processing:

```java
record Event(String id, long timestamp, String type) {}

class EventPipeline {
    private final SequencedCollection<Event> buffer = new LinkedHashSet<>();
    
    public void ingest(Event e) {
        buffer.addLast(e);  // Add to end
        if (buffer.size() > 1000) {
            buffer.removeFirst();  // Evict oldest
        }
    }
    
    public Stream<Event> latest() {
        return buffer.reversed().stream();  // Most recent first
    }
    
    public void replay() {
        buffer.forEach(this::process);  // Insertion order
    }
}
```

## Structured Concurrency: Microservice Architecture

### Before: Fan-Out with Manual Coordination
```java
// Caller must manage each service call individually
List<Future<ServiceResult>> futures = new ArrayList<>();
for (Service s : services) {
    futures.add(executor.submit(() -> s.call(request)));
}
// Must manually handle failures and timeouts
```

### After: Structured Fan-Out
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    List<Future<ServiceResult>> futures = services.stream()
        .map(s -> scope.fork(() -> s.call(request)))
        .toList();
    
    scope.join();
    scope.throwIfFailed();
    
    return futures.stream()
        .map(Future::resultNow)
        .toList();
}
```

### Circuit Breaker Pattern with Structured Concurrency
```java
public Response callWithFallback(Request req) {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Future<Response> primary = scope.fork(() -> primaryService.call(req));
        // Secondary is a backup with longer timeout
        Future<Response> fallback = scope.fork(() -> {
            Thread.sleep(100);  // Wait to see if primary fails
            return fallbackService.call(req);
        });
        
        scope.join();
        scope.throwIfFailed();
        
        return primary.resultNow();
    } catch (Exception e) {
        // Fallback already started or completed
    }
    return fallbackResult;
}
```

## Combined Architecture: Modern Java Microservice

The real power emerges when all features are combined:

```java
// Modern Java 21 microservice
@Service
public class OrderService {
    
    public OrderResponse processOrder(OrderRequest request) {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            // Pattern matching on request type
            Future<Customer> customer = scope.fork(() -> 
                switch (request) {
                    case RegisteredOrder(var id, var items, var cId)
                        when cId > 0 -> customerRepo.findById(cId);
                    case GuestOrder(var id, var items, var email)
                        -> createGuestCustomer(email);
                    case null -> throw new ValidationException("null request");
                });
            
            Future<Inventory> inventory = scope.fork(() -> 
                switch (request.items()) {
                    case SequencedCollection<Item> items 
                        when items.getFirst().isDigital() 
                        -> processDigitalItems(items);
                    case SequencedCollection<Item> items 
                        -> processPhysicalItems(items);
                });
            
            scope.join();
            scope.throwIfFailed();
            
            // Message built without the withdrawn String Templates preview
            return new OrderResponse(
                "Order " + request.id() + " processed for "
                    + customer.resultNow().name(),
                inventory.resultNow().items()
            );
        }
    }
}
```
