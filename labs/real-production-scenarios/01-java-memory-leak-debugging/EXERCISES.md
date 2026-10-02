# Lab 01 — Java Memory Leak Debugging: Exercises

## Overview
Hands-on exercises to build practical skills in detecting, diagnosing, and fixing Java memory leaks. Each exercise includes objectives, setup, steps, and validation criteria.

---

## Exercise 1: Heap Leak — Static Collection Accumulation

**Objective:** Identify and fix a classic heap leak caused by a static `Map` accumulating entries.

**Time:** 30 minutes

**Setup:**
```bash
cd labs/real-production-scenarios/01-java-memory-leak-debugging
./gradlew run --args="exercise1"  # Starts app with leak on port 8080
```

**Scenario:** A `UserSessionCache` uses `static Map<String, UserSession> sessions = new HashMap<>();` Sessions are added on login but never removed on logout.

**Steps:**
1. **Generate load:** Run `./load-test.sh exercise1` (simulates 100 logins/min for 10 min)
2. **Monitor heap:** `watch -n5 "jstat -gcutil $(pgrep -f exercise1)"`
3. **Capture heap dump:** When Old Gen > 80%, run `jcmd <pid> GC.heap_dump /tmp/heap.hprof`
4. **Analyze in Eclipse MAT:**
   - Open heap dump → Leak Suspects report
   - Find `UserSessionCache.sessions` in Dominator Tree
   - Trace path to GC roots → static field
5. **Fix:** Replace `HashMap` with `ConcurrentHashMap` + `ScheduledExecutorService` cleanup task, or use `Caffeine` cache with TTL.
6. **Validate:** Re-run load test, confirm Old Gen stabilizes < 60%.

**Deliverable:** Screenshot of MAT Leak Suspects report showing the leak, and fixed code snippet.

---

## Exercise 2: Metaspace Leak — ThreadLocal + ClassLoader

**Objective:** Diagnose a Metaspace leak caused by `ThreadLocal` holding a `ClassLoader` reference.

**Time:** 45 minutes

**Setup:**
```bash
./gradlew run --args="exercise2"  # Plugin-based app on port 8081
```

**Scenario:** A plugin system loads user code via `URLClassLoader`. A framework `ThreadLocal<PluginContext>` stores context per request but never calls `remove()`.

**Steps:**
1. **Generate load:** `./load-test.sh exercise2` (deploys 50 plugins, 10 requests/sec each)
2. **Monitor Metaspace:** `jcmd <pid> VM.native_memory summary | grep -A5 "Class"`
3. **Track ClassLoaders:** `watch -n10 "jcmd <pid> VM.classloader_stats | grep 'ClassLoader:' | wc -l"`
4. **Capture heap dump on OOM:** `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp`
5. **Analyze in MAT:**
   - Find `URLClassLoader` instances with large retained heap
   - Path to GC Roots → `ThreadLocalMap.Entry` → `PluginContext` → `URLClassLoader`
6. **Fix:** Add `try { ... } finally { pluginThreadLocal.remove(); }` in request filter.
7. **Validate:** Re-run, confirm ClassLoader count stabilizes, Metaspace growth < 10MB/hour.

**Deliverable:** MAT screenshot showing ThreadLocal → ClassLoader chain, fixed filter code.

---

## Exercise 3: Native Memory Leak — Direct ByteBuffer

**Objective:** Detect and fix a native memory leak from `ByteBuffer.allocateDirect()` not being released.

**Time:** 30 minutes

**Setup:**
```bash
./gradlew run --args="exercise3"  # High-throughput data pipeline on port 8082
```

**Scenario:** A `ZeroCopyProcessor` uses `ByteBuffer.allocateDirect(1MB)` per request but relies on finalizer for cleanup. Under load, finalizer can't keep up.

**Steps:**
1. **Generate load:** `./load-test.sh exercise3` (1000 req/sec, 1MB buffers)
2. **Monitor native memory:** `jcmd <pid> VM.native_memory detail | grep -A10 "Direct"`
3. **Check DirectBuffer count:** `jcmd <pid> GC.class_histogram | grep DirectByteBuffer`
4. **Analyze:** Direct buffers accumulate in `java.nio.DirectByteBuffer` — cleaner thread overwhelmed.
5. **Fix Options:**
   - (a) Explicit `Cleaner.clean()` via reflection (Java 8)
   - (b) `MemorySegment` + `Arena` (Java 20+ Foreign Function & Memory API)
   - (c) Pool direct buffers with `ReferenceQueue` cleanup
6. **Implement (b):** Use `Arena.ofConfined()` for request-scoped allocation.
6. **Validate:** Native memory stabilizes, no `OutOfMemoryError: Direct buffer memory`.

**Deliverable:** Before/after native memory graphs, Arena-based implementation.

---

## Exercise 4: Connection Pool Leak — HikariCP

**Objective:** Find and fix a database connection leak that exhausts the pool.

**Time:** 30 minutes

**Setup:**
```bash
./gradlew run --args="exercise4"  # Spring Boot app with HikariCP on port 8083
```

**Scenario:** A repository method opens a transaction but doesn't close the connection on exception path.

**Steps:**
1. **Generate load:** `./load-test.sh exercise4` (mix of success/error requests)
2. **Monitor pool:** `curl localhost:8083/actuator/metrics/hikaricp.connections.active`
3. **Trigger leak:** Send requests that cause `DataAccessException` (simulated)
4. **Observe:** Active connections climb, never return to pool, `PoolExhaustedException`
5. **Debug:** Enable HikariCP leak detection: `spring.datasource.hikari.leak-detection-threshold=30000`
6. **Analyze logs:** Stack trace shows leak location: `UserRepository.updateProfile()`
6. **Fix:** Ensure `Connection` closed in `finally` or use `@Transactional` properly.
7. **Validate:** Pool usage returns to baseline after error burst.

**Deliverable:** HikariCP leak detection log output, fixed repository method.

---

## Exercise 5: Listener Leak — Event Bus Registration

**Objective:** Identify a memory leak from unregistered event listeners.

**Time:** 25 minutes

**Setup:**
```bash
./gradlew run --args="exercise5"  # Event-driven service on port 8084
```

**Scenario:** Components register listeners on an `EventBus` in `@PostConstruct` but don't unregister in `@PreDestroy`.

**Steps:**
1. **Generate load:** Deploy/undeploy component 100 times via `./load-test.sh exercise5`
2. **Heap dump:** After 50 cycles, capture heap dump
3. **Analyze in MAT:** Search for `EventBus$Listener` instances — count grows with each deploy
4. **Path to GC Roots:** `EventBus.listeners` → `Listener` → Component instance → ClassLoader
5. **Fix:** Implement `DisposableBean` or `@PreDestroy` to call `eventBus.unregister(this)`
6. **Validate:** Redeploy cycles no longer increase listener count.

**Deliverable:** MAT object count trend graph, fixed lifecycle methods.

---

## Exercise 6: Cache Leak — Unbounded Guava Cache

**Objective:** Fix an unbounded cache causing gradual heap growth.

**Time:** 20 minutes

**Setup:**
```bash
./gradlew run --args="exercise6"  # Service with Guava Cache on port 8085
```

**Scenario:** `LoadingCache<Key, Value>` built without `maximumSize()` or `expireAfterWrite()`.

**Steps:**
1. **Load test:** `./load-test.sh exercise6` (unique keys per request)
2. **Monitor:** Cache size metric grows unbounded, heap follows
3. **Analyze:** `Cache.stats()` shows eviction count = 0
4. **Fix:** Add `.maximumSize(10_000).expireAfterWrite(10, TimeUnit.MINUTES)`
5. **Validate:** Cache size stabilizes, hit ratio > 80%.

**Deliverable:** Cache config before/after, hit ratio dashboard screenshot.

---

## Exercise 7: Finalizer Leak — Object with Finalizer

**Objective:** Understand how finalizers can delay reclamation and cause OOM.

**Time:** 20 minutes

**Setup:**
```bash
./gradlew run --args="exercise7"  # Legacy code with finalizers on port 8086
```

**Scenario:** A `NativeResource` class has `protected void finalize()` that calls native cleanup. High allocation rate overwhelms finalizer thread.

**Steps:**
1. **Load test:** `./load-test.sh exercise7` (10K allocations/sec)
2. **Monitor:** `jcmd <pid> GC.class_histogram | grep NativeResource` — count grows
3. **Check finalizer queue:** `jcmd <pid> GC.finalizer_info` (if available)
4. **Fix:** Replace finalizer with `Cleaner` (Java 9+) or `try-with-resources` + `AutoCloseable`
5. **Validate:** Object count stabilizes, no finalizer queue buildup.

**Deliverable:** Finalizer vs Cleaner comparison, refactored class.

---

## Exercise 8: String Intern Leak

**Objective:** Detect memory leak from excessive `String.intern()` usage.

**Time:** 15 minutes

**Setup:**
```bash
./gradlew run --args="exercise8"  # Parser interning user input on port 8087
```

**Scenario:** XML parser calls `intern()` on every attribute value (user-controlled), filling String Table (Metaspace).

**Steps:**
1. **Load test:** `./load-test.sh exercise8` (unique attribute values)
2. **Monitor:** Metaspace grows, `jcmd <pid> VM.native_memory | grep "String Table"`
3. **Analyze:** String Table size correlates with unique input count
4. **Fix:** Remove `intern()`, use `String` directly or bounded `ConcurrentHashMap` for deduplication
5. **Validate:** Metaspace stable under same load.

**Deliverable:** String Table size before/after, fixed parser code.

---

## Exercise 9: Classloader Leak — JDBC Driver

**Objective:** Fix the classic JDBC driver ClassLoader leak in web applications.

**Time:** 25 minutes

**Setup:**
```bash
./gradlew run --args="exercise9"  # Web app redeployment scenario on port 8088
```

**Scenario:** Application uses `DriverManager.registerDriver()` but doesn't deregister on undeploy. Each redeploy leaks the webapp ClassLoader.

**Steps:**
1. **Deploy app:** `./deploy.sh exercise9`
2. **Undeploy:** `./undeploy.sh exercise9`
3. **Repeat 10x**
4. **Check ClassLoaders:** `jcmd <pid> VM.classloader_stats | grep -c "WebappClassLoader"`
5. **Fix:** Implement `ServletContextListener.contextDestroyed()` to deregister drivers:
   ```java
   Enumeration<Driver> drivers = DriverManager.getDrivers();
   while (drivers.hasMoreElements()) {
       Driver d = drivers.nextElement();
       if (d.getClass().getClassLoader() == getClass().getClassLoader()) {
           DriverManager.deregisterDriver(d);
       }
   }
   ```
6. **Validate:** ClassLoader count returns to baseline after undeploy.

**Deliverable:** ClassLoader count trend across redeployments, context listener code.

---

## Exercise 10: Comprehensive Leak Hunt

**Objective:** Apply all techniques to find 3 different leaks in a realistic application.

**Time:** 60 minutes

**Setup:**
```bash
./gradlew run --args="exercise10"  # E-commerce checkout service on port 8089
```

**Scenario:** A checkout service has three hidden leaks:
1. ThreadLocal holding UserPrincipal (request-scoped)
2. Static cache of ProductCatalog with no eviction
3. Event listener not unregistered on shutdown

**Steps:**
1. **Baseline:** Run 5 min load test, capture heap/Metaspace baseline
2. **Extended run:** 30 min load test with varied traffic patterns
3. **Capture:** Heap dump + native memory summary at 10, 20, 30 min
4. **Analyze:** Use MAT + JFR + `jcmd` to identify all three leaks
5. **Fix all three:** Apply appropriate fixes from Exercises 1-9
6. **Validate:** 1-hour soak test, memory stable, no leaks detected

**Deliverable:** Leak investigation report with:
- Leak 1: Type, root cause, fix, validation
- Leak 2: Type, root cause, fix, validation
- Leak 3: Type, root cause, fix, validation
- Soak test results (memory graphs)

---

## Advanced Challenge: Production Leak Reproduction

**Objective:** Reproduce a real-world leak from a public incident report.

**Choose one:**
- Netflix Zuul ThreadLocal leak (2019)
- Apache Kafka KIP-411 consumer group memory leak
- Elasticsearch circuit breaker memory accounting bug
- HBase region server MemStore flush leak

**Deliverable:** Docker Compose reproducing the leak, analysis report, fix validation.

---

## Tools Reference Card

| Task | Command |
|---|---|
| Heap dump | `jcmd <pid> GC.heap_dump /path/heap.hprof` |
| Thread dump | `jcmd <pid> Thread.print > threads.txt` |
| ClassLoader stats | `jcmd <pid> VM.classloader_stats` |
| Native memory | `jcmd <pid> VM.native_memory detail` |
| GC histogram | `jcmd <pid> GC.class_histogram` |
| JFR recording | `jcmd <pid> JFR.start name=leak settings=profile duration=60s filename=leak.jfr` |
| MAT OQL | `SELECT * FROM java.util.HashMap WHERE retainedHeap > 1000000` |
| HikariCP leak log | Set `leakDetectionThreshold=30000` |

---

## Grading Rubric

| Criteria | Excellent (A) | Good (B) | Needs Work (C) |
|---|---|---|---|
| Root cause identification | Correct leak type + exact code location | Correct leak type, approximate location | Wrong leak type or missed leak |
| Fix quality | Production-ready, follows best practices | Works but has minor issues | Fix incomplete or introduces bugs |
| Validation | Soak test passes, metrics documented | Basic validation shown | No validation or validation fails |
| Tool proficiency | Uses MAT, JFR, jcmd fluently | Uses basic tools | Struggles with tools |
| Documentation | Clear report with screenshots | Adequate notes | Missing or unclear |