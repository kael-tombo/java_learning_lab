# CompletableFuture & Work-Stealing — Exercises

## Exercise 1: Async Pipeline with CompletableFuture
Build a pipeline that:
1. `supplyAsync(() -> fetchUser(id))` — simulates DB call (50ms)
2. `thenCompose(user -> supplyAsync(() -> fetchOrders(user.id)))` — depends on user
3. `thenCombine(supplyAsync(() -> fetchRecommendations(user.id)), (orders, recs) -> new Dashboard(user, orders, recs))`
4. `exceptionally(ex -> fallbackDashboard())` — handles any failure

Measure total latency vs sequential execution. Run 100 iterations, verify all complete correctly.

**Bonus**: Add timeout using `completeOnTimeout(fallback, 200, TimeUnit.MILLISECONDS)` (Java 9+).

---

## Exercise 2: Parallel Reduction with ForkJoinPool
Implement parallel sum of a large `double[]` using `RecursiveTask<Double>`:
- Threshold: if range < 1000, compute sequentially
- Else: split mid, `fork()` left, `compute()` right, `join()` left, return sum
- Compare with `Arrays.stream(arr).parallel().sum()` and sequential loop

**Test**: Array of 10M doubles. Measure time, verify accuracy.

---

## Exercise 3: Work-Stealing Thread Pool Implementation
Extend the `WorkStealingThreadPool` from the LeetCode solution:
1. Add `submit(Callable<T>)` returning `Future<T>`
2. Add `invokeAll(Collection<Callable<T>>)` returning `List<Future<T>>`
3. Implement graceful shutdown: `shutdown()`, `awaitTermination(timeout)`
3. Add statistics: `getCompletedTaskCount()`, `getQueueSize()`

**Test**: Submit 10,000 tasks that increment a counter; verify all complete.

---

## Exercise 4: CompletableFuture Exception Handling Patterns
Create a service with three methods that may fail:
- `fetchUser(id)` — throws `UserNotFoundException` (checked)
- `fetchOrders(userId)` — throws `ServiceUnavailableException` (unchecked)
- `fetchPayments(userId)` — throws `TimeoutException` (checked)

Compose them with:
1. `exceptionally()` — return default user on any error
2. `handle()` — log error, return partial result
3. `thenCompose()` with `whenComplete()` — cleanup on success/failure

**Challenge**: Implement retry logic — on `ServiceUnavailableException`, retry up to 3 times with exponential backoff.

---

## Exercise 5: Benchmark: CompletableFuture vs ExecutorService vs ForkJoinTask
Create a JMH benchmark comparing:
1. `CompletableFuture.supplyAsync(...).thenApply(...).join()`
2. `ExecutorService.submit(Callable).get()` + manual composition
3. `ForkJoinTask` (RecursiveTask) for same computation
4. Virtual thread executor (`Executors.newVirtualThreadPerTaskExecutor()`)

Workload: 1000 independent tasks, each doing 1ms CPU + 1ms simulated I/O (LockSupport.parkNanos).

**Metrics**: Throughput (ops/sec), latency (p50, p99), CPU utilization.

**Analyze**: Why does each approach perform differently?

---

## Starter Code Snippets

```java
// RecursiveTask for parallel sum
static class SumTask extends RecursiveTask<Double> {
    final double[] arr; final int lo, hi;
    SumTask(double[] arr, int lo, int hi) { this.arr = arr; this.lo = lo; this.hi = hi; }
    @Override protected Double compute() {
        if (hi - lo < 1000) {
            double sum = 0; for (int i = lo; i < hi; i++) sum += arr[i]; return sum;
        }
        int mid = (lo + hi) >>> 1;
        SumTask left = new SumTask(arr, lo, mid);
        left.fork();
        double right = new SumTask(arr, mid, hi).compute();
        return left.join() + right;
    }
}

// CompletableFuture retry helper
static <T> CompletableFuture<T> withRetry(Supplier<CompletableFuture<T>> supplier, int maxRetries) {
    return supplier.get().exceptionallyCompose(ex -> {
        if (maxRetries <= 0 || !(ex.getCause() instanceof ServiceUnavailableException)) {
            throw new CompletionException(ex);
        }
        return CompletableFuture.delayedExecutor(100 * (4 - maxRetries), TimeUnit.MILLISECONDS)
            .thenCompose(v -> withRetry(supplier, maxRetries - 1));
    });
}
```

```xml
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-generator-annprocess</artifactId>
    <version>1.37</version>
</dependency>
```

---

## Reflection Questions
1. Why does `CompletableFuture.join()` throw unchecked `CompletionException` while `Future.get()` throws checked `ExecutionException`?
2. In work-stealing, why does stealing from the *tail* (oldest task) reduce contention with the victim?
3. What happens if a `RecursiveTask` calls `join()` on a task that hasn't been `fork()`ed?
4. How does `CompletableFuture` achieve "async" behavior without creating new threads for each stage?