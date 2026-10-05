# EXERCISES — Modern Java Deep Dive

## Exercise 1: Records & Serialization

### Task
Create a record-based domain model with proper serialization.

### Requirements
1. Define `Order`, `OrderItem`, `Customer` as records
2. Add validation in compact constructors
3. Implement custom serialization for sensitive fields
4. Test JSON serialization with Jackson

### Code Template
```java
public record Order(
    String orderId,
    Customer customer,
    List<OrderItem> items,
    Instant createdAt,
    OrderStatus status
) {
    // Compact constructor with validation
    public Order {
        // Validate
    }
    
    // Factory methods
    public static Order create(Customer customer, List<OrderItem> items) { ... }
    
    // Derived fields
    public BigDecimal total() { ... }
}

public record Customer(String id, String name, String email, Address address) { ... }
public record OrderItem(String productId, int quantity, BigDecimal unitPrice) { ... }
```

### Test Cases
- Valid order creation
- Invalid email throws exception
- JSON round-trip preserves data
- Sensitive fields masked in logs

---

## Exercise 2: Sealed Classes & Pattern Matching

### Task
Model a payment processing system using sealed hierarchies.

### Requirements
1. Define sealed `PaymentMethod` with `CreditCard`, `BankTransfer`, `DigitalWallet`, `Crypto`
2. Implement exhaustive switch for processing
3. Add pattern matching for validation
4. Use record patterns for decomposition

### Code Template
```java
public sealed interface PaymentMethod 
    permits CreditCard, BankTransfer, DigitalWallet, Crypto { }

public record CreditCard(String number, String expiry, String cvv) implements PaymentMethod { }
public record BankTransfer(String iban, String bic) implements PaymentMethod { }
public record DigitalWallet(String provider, String accountId) implements PaymentMethod { }
public record Crypto(String currency, String walletAddress) implements PaymentMethod { }

public PaymentResult process(PaymentMethod method) {
    return switch (method) {
        case CreditCard c -> processCard(c);
        case BankTransfer b -> processTransfer(b);
        case DigitalWallet d -> processWallet(d);
        case Crypto c -> processCrypto(c);
    };
}
```

---

## Exercise 3: Virtual Threads & Structured Concurrency

### Task
Build a high-throughput API aggregator using virtual threads.

### Requirements
1. Create `AggregatorService` calling 3 downstream services
2. Use `StructuredTaskScope.ShutdownOnFailure`
3. Compare performance: platform threads vs virtual threads
4. Handle partial failures gracefully

### Code Template
```java
public class AggregatorService {
    private final HttpClient httpClient = HttpClient.newBuilder()
        .executor(Executors.newVirtualThreadPerTaskExecutor())
        .build();
    
    public AggregatedResponse aggregate(String requestId) {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var userFuture = scope.fork(() -> userService.getUser(requestId));
            var ordersFuture = scope.fork(() -> orderService.getOrders(requestId));
            var paymentsFuture = scope.fork(() -> paymentService.getPayments(requestId));
            
            scope.join();
            scope.throwIfFailed();
            
            return new AggregatedResponse(
                userFuture.get(),
                ordersFuture.get(),
                paymentsFuture.get()
            );
        }
    }
}
```

### Benchmark
```bash
# Run with platform threads
- Dvirtual.threads=false

# Run with virtual threads  
- Dvirtual.threads=true

# Measure: throughput, latency, memory, CPU
```

---

## Exercise 4: Pattern Matching Switch

### Task
Implement a document processor with exhaustive pattern matching.

### Requirements
1. Define sealed `Document` with `Pdf`, `Word`, `Text`, `Spreadsheet`, `Image`
2. Process each type with specific logic
3. Use guarded patterns for validation
3. Handle null safely

### Code Template
```java
public sealed interface Document permits Pdf, Word, Text, Spreadsheet, Image { }

public record Pdf(byte[] content, int pages) implements Document { }
public record Word(byte[] content, String author) implements Document { }
public record Text(String content, Charset encoding) implements Document { }
public record Spreadsheet(byte[] content, int sheets) implements Document { }
public record Image(byte[] content, int width, int height) implements Document { }

public ProcessingResult process(Document doc) {
    return switch (doc) {
        case null -> ProcessingResult.failed("Null document");
        case Pdf p when p.pages() > 100 -> ProcessingResult.failed("PDF too large");
        case Pdf p -> extractText(p);
        case Word w when w.content().length > 10_000_000 -> ProcessingResult.failed("Word too large");
        case Word w -> extractText(w);
        case Text t -> ProcessingResult.success(t.content());
        case Spreadsheet s -> convertToCsv(s);
        case Image i -> ocr(i);
    };
}
```

---

## Exercise 5: String Templates (Preview)

### Task
Build a safe SQL query builder using string templates.

### Requirements
1. Create `SqlTemplate` processor
2. Prevent SQL injection
3. Support parameter binding
4. Handle null values

### Code Template
```java
// Preview feature - requires --enable-preview
import java.util.StringTemplate;

public class SqlTemplate {
    public static StringTemplate.Processor<PreparedStatement> PREPARED = (template) -> {
        String sql = template.fragments().get(0);
        List<Object> params = new ArrayList<>();
        
        for (int i = 0; i < template.values().size(); i++) {
            sql += "?";
            if (i < template.fragments().size() - 1) {
                sql += template.fragments().get(i + 1);
            }
            params.add(template.values().get(i));
        }
        
        return conn -> {
            PreparedStatement stmt = conn.prepareStatement(sql);
            for (int i = 0; i < params.size(); i++) {
                stmt.setObject(i + 1, params.get(i));
            }
            return stmt;
        };
    };
}

// Usage
String table = "users";
String column = "email";
var stmt = PREPARED."SELECT * FROM \{table} WHERE \{column} = \{email}";
```

---

## Exercise 6: Sequenced Collections

### Task
Implement an LRU cache using `SequencedMap`.

### Requirements
1. Use `LinkedHashMap` as `SequencedMap`
2. Implement `get`, `put`, `evict`
3. Add `reversed()` view for debugging
3. Thread-safe variant

### Code Template
```java
public class LRUCache<K, V> {
    private final SequencedMap<K, V> map;
    private final int capacity;
    
    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.map = new LinkedHashMap<>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                return size() > capacity;
            }
        };
    }
    
    public synchronized V get(K key) { return map.get(key); }
    public synchronized void put(K key, V value) { map.put(key, value); }
    public synchronized SequencedMap<K, V> reversedView() { return map.reversed(); }
}
```

---

## Exercise 7: Migration Challenge

### Task
Migrate legacy code to modern Java patterns.

### Legacy Code
```java
// Java 8 style - refactor this
public class UserService {
    private final Map<String, User> cache = new ConcurrentHashMap<>();
    
    public User findUser(String id) {
        User cached = cache.get(id);
        if (cached != null) return cached;
        
        User user = database.findById(id);
        if (user != null) {
            cache.put(id, user);
        }
        return user;
    }
    
    public List<User> findUsersByEmail(String email) {
        return database.findAll().stream()
            .filter(u -> u.getEmail().equals(email))
            .collect(Collectors.toList());
    }
}
```

### Modern Version Requirements
- Use records for `User`
- Use `Optional` for nullable returns
- Use `computeIfAbsent` for caching
- Use pattern matching for null checks
- Use sequenced collections where appropriate

---

## Exercise 8: Foreign Function Interface

### Task
Call a native library function using FFI.

### Requirements
1. Define memory layout for C struct
2. Link to native function
3. Call function with Java data
4. Handle memory lifecycle with Arena

### Code Template
```java
// C struct:
// typedef struct { int id; char name[32]; double score; } Player;

public class NativeInterop {
    private static final Linker LINKER = Linker.nativeLinker();
    private static final SymbolLookup LOOKUP = LINKER.defaultLookup();
    
    private static final MemoryLayout PLAYER_LAYOUT = MemoryLayout.structLayout(
        ValueLayout.JAVA_INT.withName("id"),
        MemoryLayout.sequenceLayout(32, ValueLayout.JAVA_BYTE).withName("name"),
        ValueLayout.JAVA_DOUBLE.withName("score")
    );
    
    public static void savePlayer(int id, String name, double score) {
        try (Arena arena = Arena.ofConfined()) {
            MemorySegment player = arena.allocate(PLAYER_LAYOUT);
            player.set(ValueLayout.JAVA_INT, 0, id);
            
            byte[] nameBytes = name.getBytes(StandardCharsets.UTF_8);
            MemorySegment nameSeg = player.asSlice(
                PLAYER_LAYOUT.byteOffset("name"), 32);
            nameSeg.copyFrom(MemorySegment.ofArray(nameBytes));
            
            player.set(ValueLayout.JAVA_DOUBLE, PLAYER_LAYOUT.byteOffset("score"), score);
            
            MethodHandle save = LINKER.downcallHandle(
                LOOKUP.find("save_player").orElseThrow(),
                FunctionDescriptor.ofVoid(ValueLayout.ADDRESS)
            );
            save.invokeExact(player);
        }
    }
}
```

---

## Exercise 9: Scoped Values

### Task
Implement request-scoped context propagation with virtual threads.

### Requirements
1. Define `RequestContext` with user, traceId, permissions
2. Use `ScopedValue` for propagation
3. Demonstrate inheritance in virtual threads
4. Compare with `ThreadLocal`

### Code Template
```java
public class RequestContext {
    private static final ScopedValue<RequestContext> CURRENT = ScopedValue.newInstance();
    
    private final String userId;
    private final String traceId;
    private final Set<String> permissions;
    
    public static RequestContext current() {
        return CURRENT.get();
    }
    
    public static <T> T runWith(RequestContext ctx, Callable<T> action) throws Exception {
        return ScopedValue.runWhere(CURRENT, ctx, action);
    }
    
    // In HTTP filter
    public void doFilter(Request req, Response res, FilterChain chain) {
        RequestContext ctx = new RequestContext(
            req.getHeader("X-User"),
            req.getHeader("X-Trace-Id"),
            parsePermissions(req)
        );
        RequestContext.runWith(ctx, () -> {
            chain.doFilter(req, res);
            return null;
        });
    }
}
```

---

## Exercise 10: Comprehensive Benchmark

### Task
Benchmark all modern Java features against legacy equivalents.

### Benchmarks to Run
1. **Record vs Class** - allocation, serialization, equality
2. **Virtual vs Platform Threads** - throughput, latency, memory
3. **Pattern Matching vs instanceof** - throughput
4. **Sealed vs Visitor** - maintainability, performance
5. **String Templates vs StringBuilder** - allocation, safety
6. **ScopedValue vs ThreadLocal** - memory, inheritance

### JMH Template
```java
@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
@Warmup(iterations = 3, time = 2)
@Measurement(iterations = 5, time = 2)
@Fork(3)
@State(Scope.Benchmark)
public class ModernJavaBenchmarks {
    
    @Param({"100", "1000", "10000"})
    int iterations;
    
    @Benchmark
    public void recordAllocation(Blackhole bh) {
        for (int i = 0; i < iterations; i++) {
            bh.consume(new Point(i, i * 2));
        }
    }
    
    @Benchmark
    public void classAllocation(Blackhole bh) {
        for (int i = 0; i < iterations; i++) {
            bh.consume(new PointClass(i, i * 2));
        }
    }
    
    record Point(int x, int y) {}
    static class PointClass { int x, y; PointClass(int x, int y) { this.x = x; this.y = y; } }
}
```