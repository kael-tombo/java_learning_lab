# MINI_PROJECT — Modern Java Deep Dive

## Project: Modern Java Service Framework

Build a production-ready microservice framework showcasing all modern Java 17-21+ features.

---

## Project Overview

**Duration:** 3-4 weeks (part-time)
**Complexity:** Advanced
**Prerequisites:** Complete THEORY, EXERCISES, CODE_DEEP_DIVE, VISION

---

## Deliverables

### 1. Domain Modeling Library (`modern-domain`)

A reusable library demonstrating algebraic data types with records and sealed classes.

```java
// Core types
public sealed interface Result<T, E> permits Success<T, E>, Failure<T, E> { }
public record Success<T, E>(T value) implements Result<T, E> { }
public record Failure<T, E>(E error) implements Result<T, E> { }

public sealed interface Option<T> permits Some<T>, None<T> { }
public record Some<T>(T value) implements Option<T> { }
public record None<T>() implements Option<T> { }

// Domain events
public sealed interface DomainEvent 
    permits UserRegistered, OrderPlaced, PaymentProcessed { }
public record UserRegistered(String userId, String email, Instant at) implements DomainEvent { }
public record OrderPlaced(String orderId, String userId, List<OrderItem> items, Instant at) implements DomainEvent { }

// Pattern matching utilities
public static <T, E, R> R match(Result<T, E> result, 
    Function<T, R> onSuccess, Function<E, R> onFailure) {
    return switch (result) {
        case Success(var v) -> onSuccess.apply(v);
        case Failure(var e) -> onFailure.apply(e);
    };
}
```

**Requirements:**
- Records for all data types
- Sealed hierarchies for exhaustive matching
- Serialization support (Jackson, Protobuf)
- Comprehensive test suite with property-based testing

---

### 2. Virtual Thread Web Framework (`modern-web`)

A lightweight HTTP framework built for virtual threads from the ground up.

```java
// Core server using virtual threads
public class ModernServer {
    private final HttpServer server;
    private final Router router;
    
    public ModernServer(int port) {
        this.server = HttpServer.create(new InetSocketAddress(port), 0);
        this.router = new Router();
        
        // Virtual thread executor for all requests
        ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
        server.setExecutor(executor);
        
        server.createContext("/", exchange -> {
            try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
                Request req = Request.from(exchange);
                Response resp = router.route(req);
                Response.send(exchange, resp);
            } catch (Exception e) {
                Response.error(exchange, 500, e.getMessage());
            }
        });
    }
}

// Declarative routing with pattern matching
public class Router {
    private final List<Route> routes = new ArrayList<>();
    
    public Router GET(String pattern, Handler handler) {
        routes.add(new Route("GET", compilePattern(pattern), handler));
        return this;
    }
    
    public Response route(Request req) {
        return routes.stream()
            .filter(r -> r.matches(req.method(), req.path()))
            .findFirst()
            .map(r -> r.handler().handle(req, r.extractParams(req.path())))
            .orElse(Response.notFound());
    }
}

// Pattern matching for path extraction
record Route(String method, Pattern pattern, Handler handler) {
    boolean matches(String method, String path) {
        return this.method.equals(method) && pattern.matcher(path).matches();
    }
    
    Map<String, String> extractParams(String path) {
        Matcher m = pattern.matcher(path);
        if (m.matches()) {
            Map<String, String> params = new HashMap<>();
            for (int i = 1; i <= m.groupCount(); i++) {
                params.put("param" + i, m.group(i));
            }
            return params;
        }
        return Map.of();
    }
}
```

**Requirements:**
- Virtual thread per request (no platform thread blocking)
- StructuredTaskScope for request-scoped parallel operations
- ScopedValue for request context propagation
- Pattern matching for route extraction
- Built-in structured logging with structured concurrency

---

### 3. Structured Concurrency Toolkit (`modern-concurrency`)

Advanced structured concurrency patterns beyond the basics.

```java
// Retry policy with structured concurrency
public class RetryPolicy {
    public static <T> T retry(Callable<T> task, RetryConfig config) {
        return StructuredTaskScope.runWithRetry(() -> {
            try { return task.call(); }
            catch (Exception e) { throw new RetryableException(e); }
        }, config);
    }
}

// Timeout with cancellation
public class Timeout {
    public static <T> T withTimeout(Duration timeout, Callable<T> task) {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var future = scope.fork(task);
            scope.joinUntil(Instant.now().plus(timeout));
            scope.throwIfFailed();
            return future.get();
        } catch (TimeoutException e) {
            throw new TimeoutException("Operation timed out after " + timeout);
        }
    }
}

// Rate limiting with virtual threads
public class RateLimiter {
    private final Semaphore permits;
    private final ScheduledExecutorService refiller;
    
    public RateLimiter(int permitsPerSecond) {
        this.permits = new Semaphore(permitsPerSecond);
        this.refiller = Executors.newSingleThreadScheduledExecutor();
        refiller.scheduleAtFixedRate(() -> permits.release(permitsPerSecond - permits.availablePermits()), 
            1, 1, TimeUnit.SECONDS);
    }
    
    public <T> T acquire(Callable<T> task) throws InterruptedException {
        permits.acquire();
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            return scope.fork(task).join();
        }
    }
}

// Parallel pipeline with backpressure
public class ParallelPipeline<T, R> {
    public static <T, R> List<R> process(List<T> items, Function<T, R> processor, int parallelism) {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            List<Subtask<R>> subtasks = items.stream()
                .map(item -> scope.fork(() -> processor.apply(item)))
                .toList();
            
            scope.join();
            scope.throwIfFailed();
            
            return subtasks.stream().map(Subtask::get).toList();
        }
    }
}
```

**Requirements:**
- Retry with exponential backoff + jitter
- Timeout with automatic cancellation
- Rate limiting integrated with virtual threads
- Bulkhead pattern for fault isolation
- Circuit breaker with structured concurrency

---

### 4. FFI Performance Module (`modern-ffi`)

High-performance native interop showcasing FFI over JNI.

```java
// Native library: libcompute.so
// int matrix_multiply(double* a, double* b, double* c, int n);
// void fft_transform(complex* data, int n);

// Java FFI binding
public class NativeCompute {
    private static final Linker LINKER = Linker.nativeLinker();
    private static final SymbolLookup LOOKUP = LINKER.defaultLookup();
    
    private static final MethodHandle MATRIX_MULTIPLY = LINKER.downcallHandle(
        LOOKUP.find("matrix_multiply").orElseThrow(),
        FunctionDescriptor.of(ValueLayout.JAVA_INT,
            ValueLayout.ADDRESS, ValueLayout.ADDRESS, ValueLayout.ADDRESS, ValueLayout.JAVA_INT)
    );
    
    private static final MethodHandle FFT_TRANSFORM = LINKER.downcallHandle(
        LOOKUP.find("fft_transform").orElseThrow(),
        FunctionDescriptor.ofVoid(ValueLayout.ADDRESS, ValueLayout.JAVA_INT)
    );
    
    public static double[][] multiply(double[][] a, double[][] b) {
        int n = a.length;
        try (Arena arena = Arena.ofConfined()) {
            MemorySegment aSeg = arena.allocateArray(ValueLayout.JAVA_DOUBLE, n * n);
            MemorySegment bSeg = arena.allocateArray(ValueLayout.JAVA_DOUBLE, n * n);
            MemorySegment cSeg = arena.allocateArray(ValueLayout.JAVA_DOUBLE, n * n);
            
            // Copy data
            for (int i = 0; i < n; i++) {
                aSeg.setAtIndex(ValueLayout.JAVA_DOUBLE, i * n, a[i]);
                bSeg.setAtIndex(ValueLayout.JAVA_DOUBLE, i * n, b[i]);
            }
            
            int result = (int) MATRIX_MULTIPLY.invokeExact(aSeg, bSeg, cSeg, n);
            if (result != 0) throw new RuntimeException("Native error: " + result);
            
            // Read result
            double[][] c = new double[n][n];
            for (int i = 0; i < n; i++) {
                c[i] = cSeg.toArray(ValueLayout.JAVA_DOUBLE, i * n, n);
            }
            return c;
        }
    }
}
```

**Requirements:**
- Matrix multiplication (BLAS replacement)
- FFT implementation
- Memory layout optimization (column-major vs row-major)
- Arena-scoped memory management
- Benchmark vs pure Java and JNI

---

## Technical Requirements

### Build Configuration
```xml
<!-- pom.xml -->
<properties>
    <maven.compiler.release>21</maven.compiler.release>
    <maven.compiler.compilerArgs>--enable-preview</maven.compiler.compilerArgs>
</properties>

<dependencies>
    <!-- Jackson for record serialization -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.15.0</version>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.datatype</groupId>
        <artifactId>jackson-datatype-jdk8</artifactId>
        <version>2.15.0</version>
    </dependency>
    
    <!-- Testing -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.24.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- Property-based testing -->
    <dependency>
        <groupId>org.junit-platform</groupId>
        <artifactId>junit-platform-commons</artifactId>
        <version>1.10.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

---

## Implementation Phases

### Phase 1: Domain Library (Week 1)
- [ ] Core Result/Option sealed types
- [ ] Domain event hierarchy
- [ ] Jackson/Protobuf serialization
- [ ] Property-based tests (jqwik)

### Phase 2: Web Framework (Week 2)
- [ ] Virtual thread HTTP server
- [ ] Pattern matching router
- [ ] ScopedValue request context
- [ ] Structured concurrency middleware

### Phase 3: Concurrency Toolkit (Week 3)
- [ ] Retry, timeout, rate limiting
- [ ] Circuit breaker, bulkhead
- [ ] Integration tests with chaos

### Phase 4: FFI Module (Week 3-4)
- [ ] Native library compilation (CMake)
- [ ] FFI bindings with Arena
- [ ] Benchmarks vs JNI vs Java

### Phase 5: Integration & Polish (Week 4)
- [ ] Sample application using all modules
- [ ] Documentation
- [ ] GraalVM native image support
- [ ] CI/CD pipeline

---

## Evaluation Criteria

| Criterion | Weight | Excellent (5) | Good (3) | Needs Work (1) |
|-----------|--------|---------------|----------|----------------|
| Modern Java Usage | 30% | All features used idiomatically | Most features used | Few features, legacy patterns |
| Architecture | 25% | Clean, modular, testable | Functional but coupled | Monolithic, hard to test |
| Virtual Thread Mastery | 20% | Proper VT usage, no pinning | Works but has pinning | Platform thread patterns |
| Structured Concurrency | 15% | Automatic cancellation, clear errors | Manual error handling | CompletableFuture chaos |
| FFI Implementation | 10% | Safe, performant, well-tested | Works but unsafe | JNI-style or broken |

---

## Stretch Goals

1. **GraalVM Native Image** - Compile entire framework to native executable
2. **Project Loom Continuations** - Custom continuation-based patterns
3. **Vector API Integration** - SIMD acceleration for compute module
4. **Observability** - OpenTelemetry integration with structured concurrency traces
5. **Custom Pattern Matching** - User-defined patterns for domain types

---

## Learning Outcomes

Upon completion, you will have:

- [ ] Built a domain modeling library with algebraic data types
- [ ] Created a virtual-thread-native web framework
- [ ] Implemented advanced structured concurrency patterns
- [ ] Built high-performance FFI bindings
- [ ] Integrated all pieces into a cohesive framework
- [ ] Benchmarked and optimized each component
- [ ] Produced a portfolio project demonstrating expert-level modern Java