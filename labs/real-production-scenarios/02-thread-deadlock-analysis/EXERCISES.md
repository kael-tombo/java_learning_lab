# Lab 02 — Thread Deadlock Analysis: Exercises

## Overview
Hands-on exercises to build practical skills in detecting, analyzing, and resolving Java thread deadlocks. Each exercise includes objectives, setup, steps, and validation criteria.

---

## Exercise 1: Classic Synchronized Deadlock

**Objective:** Detect and fix a deadlock caused by inconsistent lock ordering with `synchronized` blocks.

**Time:** 30 minutes

**Setup:**
```bash
cd labs/real-production-scenarios/02-thread-deadlock-analysis
./gradlew run --args="exercise1"  # Starts deadlock demo on port 8080
```

**Scenario:** Two threads transfer money between accounts. `transfer(from, to)` locks `from` then `to`. Concurrent transfers A→B and B→A cause deadlock.

**Steps:**
1. **Trigger deadlock:** `./load-test.sh exercise1` (runs 100 concurrent transfers)
2. **Observe:** Requests hang, thread pool exhausts
3. **Capture thread dump:** `jcmd <pid> Thread.print > deadlock.txt`
4. **Analyze:** Look for "Found one Java-level deadlock" at end of dump
5. **Identify:** Thread-1 holds Account-A lock, wants Account-B. Thread-2 holds Account-B, wants Account-A.
6. **Fix:** Always lock accounts in consistent order (e.g., by `accountId` comparison):
   ```java
   Account first = from.id < to.id ? from : to;
   Account second = from.id < to.id ? to : from;
   synchronized(first) { synchronized(second) { ... } }
   ```
7. **Validate:** Re-run load test, confirm no hangs, all transfers complete.

**Deliverable:** Thread dump showing deadlock, fixed `transfer()` method.

---

## Exercise 2: ReentrantLock Deadlock (Not Detected by findDeadlockedThreads)

**Objective:** Diagnose a deadlock using `ReentrantLock` that `ThreadMXBean.findDeadlockedThreads()` misses.

**Time:** 35 minutes

**Setup:**
```bash
./gradlew run --args="exercise2"  # ReentrantLock-based resource manager on port 8081
```

**Scenario:** A `ResourceManager` uses `ReentrantLock` per resource. Two threads acquire locks in opposite order.

**Steps:**
1. **Trigger deadlock:** `./load-test.sh exercise2`
2. **Check JMX:** `jcmd <pid> Thread.print` — no "Found deadlock" message
3. **Why?** `findDeadlockedThreads()` only detects monitor (`synchronized`) deadlocks
4. **Manual analysis:** In thread dump, look for:
   - Thread-1: `WAITING` on `LockSupport.park()` — stack shows `ReentrantLock.lock()`
   - Thread-2: `WAITING` on `LockSupport.park()` — stack shows `ReentrantLock.lock()`
   - Each holds one lock, wants the other
5. **Use `findMonitorDeadlockedThreads()` (Java 8+):** Still null for ReentrantLock
6. **Fix:** Same consistent ordering, or use `tryLock(timeout)` with backoff:
   ```java
   while (!lock1.tryLock(100, MILLIS)) { /* backoff */ }
   try {
       while (!lock2.tryLock(100, MILLIS)) { /* backoff */ }
       try { ... } finally { lock2.unlock(); }
   } finally { lock1.unlock(); }
   ```
7. **Validate:** Load test completes, no stuck threads.

**Deliverable:** Thread dump analysis notes, fixed code with tryLock pattern.

---

## Exercise 3: Lock Ordering Violation in Framework Code

**Objective:** Find a deadlock where application code calls framework callbacks while holding locks.

**Time:** 40 minutes

**Setup:**
```bash
./gradlew run --args="exercise3"  # Spring-like DI container on port 8082
```

**Scenario:** `BeanFactory` holds `creationLock` while calling `@PostConstruct` which tries to get another bean (needs same lock).

**Steps:**
1. **Trigger:** `./load-test.sh exercise3` (parallel bean initialization)
2. **Thread dump:** Shows Thread-1 BLOCKED on `creationLock` held by Thread-2
3. **Thread-2 stack:** `BeanFactory.getBean()` → `createBean()` → `invokeInitMethods()` → `@PostConstruct` → `getBean()` (recursive)
4. **Root cause:** Lock held during callback violates "don't call foreign code with lock held"
5. **Fix options:**
   - (a) Release lock before callback: copy bean ref, release lock, call callback, re-acquire if needed
   - (b) Use `StampedLock` optimistic read for lookup
   - (c) Two-phase initialization: create all beans first, then initialize
6. **Implement (c):** Separate `createBean()` (with lock) from `initializeBean()` (no lock)
7. **Validate:** Parallel initialization works, no deadlock.

**Deliverable:** Call stack analysis, refactored initialization sequence.

---

## Exercise 4: Database Connection Pool Deadlock

**Objective:** Resolve a deadlock between application thread pool and database connection pool.

**Time:** 35 minutes

**Setup:**
```bash
./gradlew run --args="exercise4"  # Service with HikariCP on port 8083
```

**Scenario:** Thread pool size = 20, DB pool size = 10. Task A needs 2 DB connections, Task B needs 1. All threads running Task A → each holds 1 connection, waits for 2nd → pool exhausted → deadlock.

**Steps:**
1. **Trigger:** `./load-test.sh exercise4` (submits 20 Task A)
2. **Symptoms:** Threads `WAITING` on `HikariPool.getConnection()`, DB pool exhausted
3. **Analyze:** This is resource deadlock — threads hold connections while waiting for more
4. **Fix options:**
   - (a) Increase DB pool to > 20 (not always possible)
   - (b) Redesign Task A to need only 1 connection (refactor transaction boundary)
   - (c) Use `@Transactional` properly — single connection per transaction
   - (d) Separate thread pools: dedicated pool for multi-connection tasks
5. **Implement (c):** Ensure each `@Transactional` method uses exactly 1 connection
6. **Validate:** Load test with mixed tasks completes, pool usage stable.

**Deliverable:** Pool configuration before/after, transaction boundary fix.

---

## Exercise 5: Distributed Deadlock — Microservice Circular Wait

**Objective:** Analyze a distributed deadlock across service boundaries.

**Time:** 45 minutes

**Setup:**
```bash
./gradlew run --args="exercise5"  # Starts 3 services: Order, Payment, Inventory on ports 8084-8086
```

**Scenario:**
- Order Service calls Payment → Payment calls Inventory → Inventory calls Order (for validation)
- Each service uses synchronous HTTP (RestTemplate/WebClient)
- Thread pools saturate waiting for each other

**Steps:**
1. **Trigger:** `./load-test.sh exercise5` (places orders)
2. **Observe:** All 3 services show high thread usage, low CPU, requests timeout
3. **Thread dumps (all 3):** Threads `WAITING` on `HttpClient` response
4. **Distributed trace:** Use trace IDs to see call chain: Order→Payment→Inventory→Order
5. **Root cause:** Synchronous circular dependency + thread pool exhaustion
6. **Fix options:**
   - (a) Break cycle: Inventory validation async (event-driven)
   - (b) Timeouts + circuit breakers on all outbound calls
   - (c) Bulkhead pattern: separate thread pools per downstream
   - (d) Retry with jitter + idempotency
7. **Implement (b)+(c):** Add `@CircuitBreaker` + `@Bulkhead` (Resilience4j), 2s timeout
8. **Validate:** Load test — some requests fail fast (circuit open), others succeed, no total deadlock.

**Deliverable:** Distributed trace screenshot, circuit breaker config, bulkhead thread pool config.

---

## Exercise 6: Livelock — Retry Storm

**Objective:** Distinguish livelock from deadlock and fix retry-induced livelock.

**Time:** 30 minutes

**Setup:**
```bash
./gradlew run --args="exercise6"  # Cache with optimistic locking on port 8087
```

**Scenario:** Two threads retry `compareAndSet` on same key with no backoff → CPU 100%, no progress.

**Steps:**
1. **Trigger:** `./load-test.sh exercise6` (high contention on hot key)
2. **Observe:** CPU 100%, threads `RUNNABLE`, no BLOCKED/WAITING
3. **Thread dump:** Shows `while (!cas(...)) { /* spin */ }` — active but no progress
4. **Difference from deadlock:** Threads not blocked, but make no forward progress
5. **Fix:** Add exponential backoff + jitter:
   ```java
   long backoff = 1;
   while (!cas(key, oldVal, newVal)) {
       Thread.sleep(ThreadLocalRandom.current().nextLong(backoff));
       backoff = Math.min(backoff * 2, MAX_BACKOFF);
   }
   ```
6. **Validate:** CPU normal, throughput recovers, latency distribution healthy.

**Deliverable:** CPU graph before/after, backoff implementation.

---

## Exercise 7: Lock Striping Gone Wrong

**Objective:** Fix a deadlock caused by incorrect lock striping implementation.

**Time:** 30 minutes

**Setup:**
```bash
./gradlew run --args="exercise7"  # Striped cache on port 8088
```

**Scenario:** `StripedCache` uses `locks[hash(key) % N]`. Two keys hash to same stripe but need atomic multi-key operation.

**Steps:**
1. **Trigger:** `./load-test.sh exercise7` (multi-key operations)
2. **Deadlock:** Thread-1 locks stripe-5 for key-A, wants stripe-3 for key-B. Thread-2 opposite.
3. **Problem:** Striping reduces contention but doesn't eliminate lock ordering issues for multi-key ops
4. **Fix:** For multi-key operations, acquire all needed stripes in consistent global order:
   ```java
   int[] stripes = {stripe(key1), stripe(key2), ...};
   Arrays.sort(stripes);
   for (int s : stripes) locks[s].lock();
   try { ... } finally { for (int s : stripes) locks[s].unlock(); }
   ```
5. **Validate:** Multi-key operations complete, no deadlock.

**Deliverable:** Fixed striping acquisition logic.

---

## Exercise 8: CompletableFuture Deadlock (Thread Pool Exhaustion)

**Objective:** Diagnose deadlock from `CompletableFuture` tasks submitting to same pool.

**Time:** 35 minutes

**Setup:**
```bash
./gradlew run --args="exercise8"  # Async pipeline on port 8089
```

**Scenario:** `CompletableFuture.supplyAsync(() -> { return otherFuture.get(); }, sharedPool)` — task waits on another future in same pool.

**Steps:**
1. **Trigger:** `./load-test.sh exercise8`
2. **Symptoms:** All pool threads `WAITING` on `Future.get()`, no threads to complete the futures
3. **Thread dump:** Pool threads parked on `LockSupport.park()` in `FutureTask.get()`
4. **Root cause:** Thread pool starvation — tasks waiting on each other in same pool
5. **Fix options:**
   - (a) Separate pools: `supplyAsync(task, ioPool)` for blocking, `cpuPool` for compute
   - (b) Use `CompletableFuture.thenCompose()` chaining instead of `.get()`
   - (c) Virtual threads (Java 21+) — no pool exhaustion
6. **Implement (b):** Refactor to `future.thenCompose(result -> nextStep(result))`
7. **Validate:** Pipeline completes, no thread starvation.

**Deliverable:** Refactored async chain, virtual thread alternative.

---

## Exercise 9: Read-Write Lock Writer Starvation

**Objective:** Fix writer starvation in `ReentrantReadWriteLock` causing apparent deadlock.

**Time:** 25 minutes

**Setup:**
```bash
./gradlew run --args="exercise9"  # Read-heavy cache on port 8090
```

**Scenario:** Continuous read lock acquisition prevents write lock — writes wait indefinitely.

**Steps:**
1. **Trigger:** `./load-test.sh exercise9` (high read rate, occasional writes)
2. **Observe:** Write threads `WAITING` on `WriteLock`, never acquire
3. **Cause:** `ReentrantReadWriteLock` non-fair — readers can starve writers
4. **Fix:** Use fair `ReentrantReadWriteLock(true)` or `StampedLock` optimistic reads
5. **Implement StampedLock:**
   ```java
   long stamp = lock.tryOptimisticRead();
   if (!lock.validate(stamp)) {
       stamp = lock.readLock();
       try { return read(); } finally { lock.unlockRead(stamp); }
   }
   // Write: long stamp = lock.writeLock(); try { write(); } finally { lock.unlockWrite(stamp); }
   ```
6. **Validate:** Writes complete within SLO, read throughput maintained.

**Deliverable:** StampedLock implementation, latency comparison.

---

## Exercise 10: Comprehensive Deadlock Hunt

**Objective:** Find and fix 3 different deadlock types in a realistic order management system.

**Time:** 60 minutes

**Setup:**
```bash
./gradlew run --args="exercise10"  # Order service with payments, inventory, shipping on port 8091
```

**Scenario:** Three hidden deadlocks:
1. Account transfer deadlock (Exercise 1 pattern)
2. ReentrantLock deadlock in payment processor (Exercise 2)
3. Distributed deadlock: Order→Payment→Inventory→Order (Exercise 5)

**Steps:**
1. **Baseline:** Run 5 min load test, capture thread dumps every 30s
2. **Extended run:** 15 min load test with varied traffic
3. **Analyze:** Use `jcmd Thread.print` + `jstack -l` + distributed traces
4. **Identify all three:** Match patterns from Exercises 1, 2, 5
5. **Fix all three:** Apply consistent ordering, tryLock, circuit breakers
6. **Validate:** 30-min soak test, zero stuck threads, all SLOs met.

**Deliverable:** Deadlock investigation report with:
- Deadlock 1: Type, stack traces, fix, validation
- Deadlock 2: Type, stack traces, fix, validation
- Deadlock 3: Type, stack traces, fix, validation
- Soak test results

---

## Tools Reference Card

| Task | Command |
|---|---|
| Thread dump (jcmd) | `jcmd <pid> Thread.print > threads.txt` |
| Thread dump (jstack) | `jstack -l <pid> > threads.txt` |
| Deadlock detection | `jcmd <pid> Thread.print -deadlock` |
| JMX deadlock | `jcmd <pid> JMX.findDeadlockedThreads` |
| Thread CPU usage | `top -H -p <pid>` (Linux) |
| Lock contention | `jcmd <pid> JFR.start name=lock settings=profile duration=60s` |
| VisualVM | Attach to PID → Threads tab → "Thread Dump" |
| Arthas (online) | `thread -b` (find blocked), `thread <id>` (stack) |

---

## Grading Rubric

| Criteria | Excellent (A) | Good (B) | Needs Work (C) |
|---|---|---|---|
| Deadlock identification | Correct type + exact lock/cycle | Correct type, approximate location | Missed deadlock or wrong type |
| Root cause analysis | Full call chain + Coffman condition | Basic cause identified | Superficial or incorrect |
| Fix quality | Production-ready, no new issues | Works but minor concerns | Fix incomplete or introduces bugs |
| Tool proficiency | Uses jcmd, jstack, traces fluently | Uses basic tools | Struggles with thread dumps |
| Validation | Soak test passes, metrics documented | Basic validation | No validation or fails |