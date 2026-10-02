# Thread Creation & Virtual Threads — Exercises

## Exercise 1: Thread Creation Comparison
Create a program that starts 10,000 tasks using three approaches:
1. `new Thread(runnable).start()` (platform threads)
2. `Executors.newFixedThreadPool(100)` (platform thread pool)
3. `Executors.newVirtualThreadPerTaskExecutor()` (virtual threads)

Each task: sleep 10ms (simulate I/O), increment a counter.
Measure:
- Total time
- Peak memory (use `-Xmx` and `Runtime.totalMemory()`)
- Thread count (via `Thread.activeCount()` or JMX)

**Expected**: Virtual threads complete fastest with lowest memory.

---

## Exercise 2: Web Crawler with Virtual Threads
Implement a multi-threaded web crawler (similar to LeetCode 1242):
- Start from a seed URL
- Fetch HTML (use `java.net.http.HttpClient` with `HttpResponse.BodyHandlers.ofString()`)
- Extract links (regex or simple parser: `<a href="...">`)
- Filter to same hostname
- Use `ConcurrentHashMap.newKeySet()` for visited URLs
- Use `Executors.newVirtualThreadPerTaskExecutor()` for concurrency
- Limit: max 100 pages, max depth 3

**Deliverable**: List of crawled URLs. Handle errors gracefully (timeouts, 4xx/5xx).

---

## Exercise 3: Virtual Thread Pinning Demo
Demonstrate carrier thread pinning:
1. Create a `synchronized` method that sleeps 100ms
2. Submit 100 virtual threads calling this method
3. Monitor carrier threads (use `ThreadMXBean` or print `Thread.currentThread().getName()` inside)
4. Repeat with `ReentrantLock` instead of `synchronized`
5. Compare: with `synchronized`, only a few carriers run concurrently; with `Lock`, many virtual threads interleave

**Observation**: Pinning limits concurrency. Use `jstack` or `-Djdk.tracePinnedThreads=full` to detect.

---

## Exercise 4: ThreadLocal vs Virtual Threads
Create a `ThreadLocal<String>` to track a request ID.
- Submit 1000 virtual threads, each setting a unique request ID
- Each task: set ID, sleep 1ms, verify ID matches
- Verify no cross-contamination
- Compare with platform thread pool of size 10 — observe `ThreadLocal` reuse across tasks

**Insight**: Virtual threads provide true isolation; platform thread pools reuse `ThreadLocal` state.

---

## Exercise 5: Structured Concurrency with StructuredTaskScope
Use `StructuredTaskScope` (Java 21 preview, or `jdk.incubator.concurrent`):
- Define a scope that forks 3 subtasks: fetch user, fetch orders, fetch recommendations
- Each subtask runs in a virtual thread, simulates 50-200ms latency
- On success: combine results into a response object
- On any failure: cancel all other subtasks automatically (shutdownOnFailure)
- Handle timeout: shutdown after 500ms

**Pattern**:
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var user = scope.fork(() -> fetchUser(id));
    var orders = scope.fork(() -> fetchOrders(id));
    var recs = scope.fork(() -> fetchRecommendations(id));
    scope.join();           // wait for all
    scope.throwIfFailed();  // propagate exception
    return new Response(user.get(), orders.get(), recs.get());
}
```

---

## Starter Code Snippets

```java
// HttpClient for crawler (Java 11+)
HttpClient client = HttpClient.newBuilder()
    .followRedirects(HttpClient.Redirect.NORMAL)
    .connectTimeout(Duration.ofSeconds(5))
    .build();

HttpRequest request = HttpRequest.newBuilder(uri).GET().build();
HttpResponse<String> response = client.send(request, BodyHandlers.ofString());

// Detect pinning
// Run with: -Djdk.tracePinnedThreads=full -Djdk.virtualThreadScheduler.parallelism=4
```

```xml
<!-- For StructuredTaskScope (Java 21+) -->
<!-- No extra dependency needed; part of JDK -->
<!-- For preview features: --enable-preview --source 21 -->
```

---

## Reflection Questions
1. Why does `Executors.newCachedThreadPool()` not scale to 100,000 tasks but virtual threads do?
2. What happens to a virtual thread's stack when it unmounts? Where is it stored?
3. Why can't `ThreadLocal` be used to pass context across virtual thread boundaries (unlike platform threads)?
4. In what scenarios would `StructuredTaskScope` be preferable to `CompletableFuture.allOf()`?