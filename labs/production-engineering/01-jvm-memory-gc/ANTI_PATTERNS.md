# ANTI-PATTERNS: JVM Memory & Garbage Collection
## Lab 01 | Production Engineering Academy

---

## Anti-Pattern 1: The Static Cache / Unbounded Collection Memory Leak

### The Mistake
Using standard Java collections (`HashMap`, `ArrayList`, `ConcurrentHashMap`) as caches with no eviction policy, no weak/soft references, and no maximum size limit.

```java
// FATAL ANTI-PATTERN: Infinite growth in Old Gen
@Component
public class SessionSecurityManager {
    // Unbounded static map storing token -> security principal
    private static final Map<String, UserSession> SESSIONS = new ConcurrentHashMap<>();

    public void registerSession(String token, UserSession session) {
        SESSIONS.put(token, session); // Never evicted on logout or expiration!
    }
}
```

### Why It Fails in Production
1. Objects stored in `static` fields are referenced directly by the `ClassLoader`, acting as roots in the GC root set.
2. They are NEVER eligible for garbage collection during minor or major GCs.
3. Over days or weeks in production, millions of expired sessions accumulate, filling Old Generation.
4. Old Gen occupancy crosses GC thresholds, triggering continuous, long Stop-The-World (STW) Full GCs until `java.lang.OutOfMemoryError: Java heap space`.

### Production War Story
A Fintech payment gateway suffered a total outage every 18 days. Engineering teams suspected a memory leak in Netty or off-heap allocations and spent weeks tuning `-XX:MaxDirectMemorySize` and switching from G1 to ZGC. When heap dumps were finally captured with `jcmd <pid> GC.heap_dump /dumps/heap.hprof` and inspected via Eclipse Memory Analyzer (MAT), an unbounded `ConcurrentHashMap<UUID, PaymentAuditRecord>` held 4.2 GB of heap across 11 million dead transactions.

### The Correct Production Pattern
Use bounded caches with explicit eviction policies (LRU/W-TinyLFU) using Caffeine:

```java
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import java.time.Duration;

@Component
public class SessionSecurityManager {
    private final Cache<String, UserSession> sessionCache = Caffeine.newBuilder()
            .maximumSize(50_000) // Upper memory bound
            .expireAfterWrite(Duration.ofMinutes(30)) // Fixed TTL
            .expireAfterAccess(Duration.ofMinutes(15)) // Idle timeout
            .recordStats() // Expose metrics to Micrometer/Prometheus
            .build();

    public void registerSession(String token, UserSession session) {
        sessionCache.put(token, session);
    }

    public UserSession getSession(String token) {
        return sessionCache.getIfPresent(token);
    }
}
```

---

## Anti-Pattern 2: `ThreadLocal` Leak in Thread Pools

### The Mistake
Storing state in `ThreadLocal` variables within web applications running inside pooled thread environments (Tomcat, Jetty, Netty, ForkJoinPool) without explicit clean-up.

```java
// DANGEROUS: Leaks memory and cross-contaminates requests
public class UserContextHolder {
    private static final ThreadLocal<SecurityContext> CONTEXT = new ThreadLocal<>();

    public static void set(SecurityContext ctx) {
        CONTEXT.set(ctx);
    }

    public static SecurityContext get() {
        return CONTEXT.get();
    }
    // Missing remove()!
}
```

### Why It Fails in Production
1. Worker threads in thread pools do not terminate after a request finishes; they return to the pool to handle subsequent requests.
2. `ThreadLocal` stores data inside `thread.threadLocals` (a `ThreadLocalMap`).
3. While the `ThreadLocal` object itself might be weak-referenced in the map entry, the **value** is strongly referenced by the thread.
4. If the class was loaded by a custom ClassLoader (e.g., in OSGi, plugin systems, or Tomcat application undeploy), the entire `ClassLoader` and all its loaded classes are pinned in Metaspace, causing `java.lang.OutOfMemoryError: Metaspace`.

### The Correct Production Pattern
Always use a `try-finally` block or an `AutoCloseable` scope:

```java
public class SecurityContextScope implements AutoCloseable {
    private static final ThreadLocal<SecurityContext> CONTEXT = new ThreadLocal<>();

    private final SecurityContext previous;

    public SecurityContextScope(SecurityContext newContext) {
        this.previous = CONTEXT.get();
        CONTEXT.set(newContext);
    }

    public static SecurityContext current() {
        return CONTEXT.get();
    }

    @Override
    public void close() {
        if (previous != null) {
            CONTEXT.set(previous);
        } else {
            CONTEXT.remove(); // CRITICAL: Always remove on pool exit
        }
    }
}

// In Filter / Interceptor:
public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
    try (SecurityContextScope scope = new SecurityContextScope(extractContext(req))) {
        chain.doFilter(req, res);
    } // Automatically invokes remove() even on unhandled RuntimeException
}
```

---

## Anti-Pattern 3: Massive Allocation in Inner Loops (GC Churn)

### The Mistake
Allocating transient helper objects, large byte arrays, or strings inside hot loops processing high-throughput events.

```java
// BAD: Generates gigabytes of garbage per second
public void processBatch(List<OrderEvent> batch) {
    for (OrderEvent event : batch) {
        // Creates a new ObjectMapper, SimpleDateFormat, and byte buffer per item
        ObjectMapper mapper = new ObjectMapper();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        byte[] buffer = new byte[65536]; 
        
        String json = mapper.writeValueAsString(event);
        log.info("Processing: " + json + " at " + sdf.format(new Date()));
        // ...
    }
}
```

### Why It Fails in Production
1. This leads to **allocation rates exceeding several GB/s**.
2. Eden fills up in milliseconds, triggering constant Young GCs.
3. Short-lived objects survive young GC because they are still being processed when a collection triggers; they prematurely promote into Survivor spaces and Old Generation.
4. Premature promotion degrades G1/ZGC efficiency, forcing CPU cores to spend 40%+ of their cycles doing garbage collection instead of application logic.

### The Correct Production Pattern
Reuse immutable, thread-safe instances and avoid unnecessary allocations:

```java
public class OrderBatchProcessor {
    // Singleton, thread-safe instances initialized once
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final DateTimeFormatter FORMATTER = 
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").withZone(ZoneOffset.UTC);

    public void processBatch(List<OrderEvent> batch) {
        for (OrderEvent event : batch) {
            if (log.isInfoEnabled()) {
                // Use structured logging or direct serialization without string concatenation
                log.info("Processing order {} at {}", event.getId(), FORMATTER.format(Instant.now()));
            }
            // Reuse shared or direct buffers if handling byte transfers
            processSingleOrder(event);
        }
    }
}
```

---

## Anti-Pattern 4: Disabling Explicit GC with `-XX:+DisableExplicitGC` Blindly

### The Mistake
Setting `-XX:+DisableExplicitGC` to prevent third-party libraries or legacy code from calling `System.gc()`.

### Why It Fails with Direct Memory / NIO
1. `ByteBuffer.allocateDirect()` allocates off-heap memory outside the JVM heap.
2. Direct byte buffers rely on `PhantomReference` cleaners (`sun.misc.Cleaner`).
3. If off-heap memory is exhausted, NIO internally calls `System.gc()` to prompt reference processing and reclaim direct buffers.
4. When `-XX:+DisableExplicitGC` is set, `System.gc()` becomes a no-op!
5. Result: The JVM crashes with `java.lang.OutOfMemoryError: Direct buffer memory` even though physical RAM and JVM heap are virtually empty!

### The Correct Solution
Instead of disabling explicit GC completely, convert it to concurrent GC execution:
```bash
# Good: System.gc() triggers concurrent background collection instead of STW stop-the-world
-XX:+ExplicitGCInvokesConcurrent
```

---

## Anti-Pattern 5: Sizing Java Heap Equal to Container RAM Limit

### The Mistake
Running in Kubernetes with `resources.limits.memory: 8Gi` and configuring:
`-Xms8g -Xmx8g`.

### Why It Fails
The JVM process memory footprint is substantially larger than `-Xmx`:
$$\text{Total Memory} = \text{Heap} + \text{Metaspace} + \text{Thread Stacks} + \text{Direct Memory (NIO)} + \text{Code Cache} + \text{GC Structures} + \text{Native Libs (glibc, jemalloc)}$$

If `-Xmx` is set to the cgroup limit, the Linux kernel OOM Killer immediately sends `SIGKILL` (Exit Code 137) to the Java process the moment native allocations, thread stacks, or off-heap buffers grow.

### The Correct Sizing Rule
For containers:
- Max Heap: **65% to 75%** of container memory limit.
- Container limit 8Gi $\rightarrow$ `-Xmx5500m` or `-XX:MaxRAMPercentage=70.0`.
