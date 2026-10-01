# Virtual Threads — Deep Dive: Platform vs Virtual Threads, Pinning, Structured Concurrency

> Why does `Lab.massiveConcurrency()` launch 10,000 threads in milliseconds while
> 10,000 platform `Thread`s would OOM — and why does wrapping a `synchronized`
> block in a virtual thread silently erase that win?
> This guide traces the answer from the carrier-thread scheduler to the pinning rule.

All claims grounded in `01-core-java/50-virtual-threads/src/main/java/com/learning/virtualthreads/Lab.java`
(methods `creatingVirtualThreads`, `platformVsVirtual`, `massiveConcurrency`,
`structuredConcurrency`, `pinnedThreads`, `bestPractices`),
`01-core-java/05-concurrency/src/main/java/com/learning/concurrency/ThreadBasicsDemo.java`
(`SynchronizedCounter`, `ReentrantLockCounter`, `ThreadPoolExample`, `FutureExample`,
`VolatileFlag`, `ThreadLocalExample`), and
`AdvancedConcurrencyDemo.java` (`CountDownLatchExample`, `CyclicBarrierExample`, semaphore).

---

## 1. THEORY — Mental models

### 1.1 Platform threads: 1:1 with the OS

A platform thread (`new Thread(...)`, `Thread.ofPlatform()`) is a one-to-one wrapper
around an OS thread. Each carries a large pre-committed stack (~1 MB by default),
a kernel scheduling entry, and full `synchronized`/native/JNI compatibility.
`Lab.platformVsVirtual()` prints the punchline:

```
Platform threads: 1:1 with OS threads, ~1MB stack
Virtual threads:  M:N with carrier threads, ~few KB stack
```

Mental model: platform threads are **hotel rooms** — expensive to build, you pool
and reuse them (`ThreadPoolExample` with `Executors.newFixedThreadPool(n)` exists
precisely because creating a platform thread per task is unaffordable).

`ThreadBasicsDemo.main()` shows the classic pattern: create 2 threads, `start()`,
`join()`, then hand 100 increments to a 2-thread pool. Every reuse decision in
that file is a workaround for thread-creation cost.

### 1.2 Virtual threads: M:N on carrier threads

A virtual thread (`Thread.startVirtualThread(...)`, `Thread.ofVirtual()...start()`)
is a cheap Java object scheduled by the JDK onto a small pool of platform
**carrier threads** (default: one per CPU core, in a `ForkJoinPool`).
Blocking operations (`Thread.sleep`, socket read, `Future.get`, lock park) cause
the virtual thread to **unmount** — the carrier is freed to run another virtual
thread, and the blocked VT resumes later.

Mental model: virtual threads are **sticky notes on a whiteboard** — you create
one per task and throw it away. `Lab.massiveConcurrency()` creates 10,000 of them
in a loop with a `CountDownLatch(10_000)`; each sleeps 1 ms and counts down.
Platform threads would fail at ~10k (stack memory + scheduler collapse); virtual
threads scale to 100k+ because idle VTs cost a few KB of heap, not a kernel stack.

`Lab.platformVsVirtual()` verifies identity at runtime:

```java
Thread.startVirtualThread(() ->
    System.out.println(Thread.currentThread().isVirtual())); // true
```

plus three facts to memorise: VTs are **daemon by default** (JVM exits without
joining them), `ThreadLocal` on 1M VTs is 1M copies (prefer parameters or scoped
values, JEP 429), and `InheritableThreadLocal` requires carrier-pool support.

### 1.3 Pinning: when a virtual thread stops being virtual

`Lab.pinnedThreads()` states the rule exactly:

> A virtual thread is **pinned** to its carrier when (1) inside a `synchronized`
> block/method, or (2) calling a native method (JNI).

While pinned, a blocking call **blocks the carrier too** — the M:N scheduler
cannot unmount, so one blocked VT idles a whole OS thread and starves every VT
queued behind it:

```
Carrier T1: [VT pinned][BLOCKED] -> carrier blocked
Carrier T2: [VT unpinned]        -> can yield
```

Why: `synchronized` owns an OS-level monitor that the carrier must hold, and JNI
frames live outside the heap where the unmount machinery cannot reach.
Mitigations from the lab, in priority order:

1. Replace `synchronized` with `ReentrantLock` (`ThreadBasicsDemo.ReentrantLockCounter`
   is the drop-in pattern — `lock()`/`unlock()` in `finally` parks cooperatively
   and never pins).
2. Keep `synchronized` regions short and never call I/O/`sleep()` inside them.
3. Detect with `-Djdk.tracePinnedThreads=1` (prints a stack trace whenever
   pinning blocks a carrier).

Interview one-liner: *pinning downgrades a virtual thread to a platform thread
for the duration of the monitor hold.*

### 1.4 Structured concurrency: treating subtasks as one unit

`Lab.structuredConcurrency()` uses `Executors.newVirtualThreadPerTaskExecutor()`
(one fresh VT per submitted task, auto-closed) to fan out `user` + `order` futures
and `get()` both. The printed contract is the real `StructuredTaskScope` semantic
(preview API, same idea):

- all subtasks complete before the parent continues (no thread leaks);
- `ShutdownOnFailure`: one subtask throws → siblings cancelled;
- `ShutdownOnSuccess`: one subtask succeeds → siblings cancelled (hedged requests).

Contrast with `ThreadBasicsDemo.FutureExample` / `AdvancedConcurrencyDemo.CountDownLatchExample`:
raw `ExecutorService` + `Future` + `CountDownLatch` leaves lifetime management to
you (`shutdown()`, `awaitTermination`, interrupt paths). Structured scope makes the
lifetime **syntactic** — exiting the `try` block guarantees cleanup, the same way
try-with-resources guarantees a stream closes. Deterministic lifetime is the point,
not speed.

### 1.5 When NOT to use virtual threads (`Lab.bestPractices()`)

| DO (I/O-bound) | DON'T |
|---|---|
| HTTP calls, DB queries, file I/O — threads spend life *waiting* | CPU-bound number crunching (no waiting ⇒ no unmount benefit; use platform pool sized to cores) |
| Many concurrent connections (server per-request thread) | Long `synchronized` blocks (pinning — see 1.3) |
| Task-per-request (`newVirtualThreadPerTaskExecutor`) | Pooling VTs (they are cheap; pooling reintroduces queueing bugs) |
| Fan-out with structured scope | Storing per-request state in `ThreadLocal` at 1M-thread scale |

---

## 2. CODE_DEEP_DIVE — Grounded in the real files

### 2.1 Creating virtual threads (`Lab.creatingVirtualThreads()`, lines 20–42)

Three equivalent spellings:

```java
var vt1 = Thread.startVirtualThread(() -> ...);            // fire-and-forget, join later
var vt2 = Thread.ofVirtual().name("my-vt").start(() -> ...); // named builder
var builder = Thread.ofVirtual().name("pool-");            // prefix builder: pool-0, pool-1…
for (int i = 0; i < 3; i++) threads.add(builder.start(() -> ...));
vt1.join(); vt2.join(); for (var t : threads) t.join();    // VTs are daemon: must join
```

Teaching points: the `name("pool-")` builder auto-suffixes (observe `pool-0…`
in output); `join()` is mandatory because daemon VTs do not keep the JVM alive —
dropping the joins makes `main` exit before tasks print, the #1 beginner bug.

### 2.2 Platform vs virtual, line by line (`Lab.platformVsVirtual()`, lines 44–60)

```java
System.out.println("Platform: " + Thread.currentThread().isVirtual()); // false in main
var vt = Thread.startVirtualThread(() -> {
    System.out.println("Virtual: " + Thread.currentThread().isVirtual()); // true
});
vt.join();
```

`isVirtual()` is the runtime discriminator — use it in assertions
(`assertFalse(Thread.currentThread().isVirtual())` in platform tests,
`assertTrue(...)` inside VT tasks). The stack-trace line in the lab
(`getStackTrace()[2]`) shows the carrier frame underneath the virtual frames:
proof that a VT stack is a heap object interpreted by the carrier, not a
contiguous OS stack — which is exactly why it starts at a few KB and grows.

### 2.3 Massive concurrency (`Lab.massiveConcurrency()`, lines 62–85)

```java
var latch = new CountDownLatch(10_000);
for (int i = 0; i < 10_000; i++)
    Thread.startVirtualThread(() -> {
        try { Thread.sleep(1); } catch (InterruptedException e) {}
        latch.countDown();
    });
latch.await();
```

This is `AdvancedConcurrencyDemo.CountDownLatchExample` scaled 3 → 10,000.
With platform threads the equivalent loop allocates ~10 GB of stacks and
thousands of kernel threads; with VTs the loop completes in milliseconds because
`Thread.sleep(1)` unmounts instead of blocking a carrier. Reproduce the lesson:
replace `Thread.startVirtualThread` with `Thread.ofPlatform().start` and watch
for `OutOfMemoryError: unable to create native thread` (do it once, in a VM you
can kill). The lab's comment ("Ideal for I/O-bound workloads") is the boundary:
`sleep`/`socket-read` unmounts, `for(;;) Math.sqrt` does not.

### 2.4 Structured fan-out (`Lab.structuredConcurrency()`, lines 87–110)

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    Future<String> user  = executor.submit(() -> { Thread.sleep(50); return "User-1"; });
    Future<String> order = executor.submit(() -> { Thread.sleep(30); return "Order-100"; });
    System.out.println("Result: " + user.get() + " | " + order.get());
} // close() waits for all tasks — bounded lifetime
```

Compare against `ThreadBasicsDemo.ThreadPoolExample.shutdown()` (manual
`shutdown()` + `awaitTermination(5s)` + `shutdownNow()` fallback) and
`FutureExample.getFutureResult()` (bare `future.get()` with optional timeout).
The executor-per-task pattern deletes all three manual steps: the try-block exit
*is* the shutdown. Exercise 3 makes the failure-mode difference concrete
(one subtask throws → who cancels the sibling?).

### 2.5 The pinning fix, mapped to `ThreadBasicsDemo` (`Lab.pinnedThreads()` + `SynchronizedCounter` vs `ReentrantLockCounter`)

Unsafe-under-VT pattern (pins whenever the I/O blocks while holding the monitor):

```java
public synchronized void fetchAndUpdate() {       // SynchronizedCounter style
    value++;                                       // + hypothetical blockingCall();
}
```

Fixed pattern (yields the carrier while parked):

```java
private final ReentrantLock lock = new ReentrantLock();  // ReentrantLockCounter style
public void fetchAndUpdate() {
    lock.lock();
    try { value++; /* blockingCall(); — unmounts cleanly */ }
    finally { lock.unlock(); }
}
```

Bonus from `ThreadBasicsDemo`: `ReadWriteCounter` (many concurrent readers, one
writer) and `AtomicCounter` (CAS, no lock at all) both compose with VTs without
pinning — prefer atomics for counters, `ReentrantReadWriteLock` for read-heavy
maps, plain `ReentrantLock` everywhere else a VT might block.

### 2.6 What stays the same: pools, atomics, visibility

Virtual threads do **not** change the memory model. `VolatileFlag`
(visibility), `UnsafeCounter` (read-modify-write race), `ProducerConsumer`
(`wait`/`notifyAll` with `while` guard against spurious wakeups),
`DeadlockExample`/`DeadlockFree` (lock ordering) all behave identically on VTs.
The 05-concurrency module is therefore prerequisite reading: VTs change *scheduling
cost*, not *correctness rules*.

---

## 3. MATH_FOUNDATION — Complexity analysis

Let n = tasks, c = carriers (≈ cores), S_plat ≈ 1 MB, S_vt ≈ few KB heap,
B = fraction of task time spent blocked on I/O.

| Model | Memory | Scheduling | Throughput bound |
|---|---|---|---|
| One platform thread per task (`new Thread` loop) | O(n · S_plat): 10k threads ≈ 10 GB stacks → OOM | OS preemptive, ~µs context switch + kernel entry | min(n, cores) running; rest are parked kernel objects |
| Fixed pool (`newFixedThreadPool(k)`, k≈cores/2×) | O(k · S_plat), bounded | Queueing: tasks wait in `BlockingQueue` | Little's-law bound: throughput ≤ k / mean_service_time; I/O-bound tasks idle carriers |
| Virtual thread per task | O(n · S_vt): 10k VTs ≈ tens of MB heap | User-mode unmount on block, ~ns–µs | Effective parallelism ≈ B·n concurrent waiters on c carriers; ideal when B → 1 |
| Pinned VT (`synchronized` + blocking I/O) | O(n · S_vt) heap **plus** c carriers held | Degrades to platform-thread scheduling: carrier blocked | Throughput collapses to ≤ c concurrent blockers; pinning fraction p multiplies carrier demand by 1/(1−p) |

Worked example (`massiveConcurrency`): n = 10,000, each task sleeps 1 ms.
Platform cost ≈ 10,000 × 1 MB = 10 GB committed stacks (fails). VT cost ≈
10,000 × ~2–5 KB = 20–50 MB heap on c ≈ 8 carriers; elapsed ≈ 1 ms of sleep +
scheduler churn, i.e. tens of ms. Speedup is not CPU speedup — it is the removal
of the thread-count ceiling for B ≈ 1 workloads.

Amdahl corollary for pinning: with p = fraction of VT time pinned-and-blocked,
required carriers ≈ n·p; if n·p > c the pool saturates and tail latency explodes
even though "we use virtual threads". Hence rule: drive p → 0 with `ReentrantLock`.

---

## 4. EXERCISES

1. **Ceiling demo**: in `Lab.massiveConcurrency()`, swap `Thread.startVirtualThread`
   for `Thread.ofPlatform().unstarted(...)` + `start()`. At what n does your machine
   throw `OutOfMemoryError: unable to create native thread`? Restore and confirm
   the VT version passes 10k (then try 100k).
2. **Daemon trap**: delete the `join()` calls in `creatingVirtualThreads()`.
   Run three times. Explain the missing/flaky output using the daemon-default rule.
3. **Failure cancellation**: in `structuredConcurrency()`, make the `order` task
   throw after 10 ms while `user` sleeps 5 s. Time the try-block exit with
   `newVirtualThreadPerTaskExecutor` vs a raw `newFixedThreadPool(2)` +
   `Future.get()` with no cancellation. Which one leaks the 5 s task, and what
   single `finally`/`close` line fixes the executor version?
4. **Pinning hunt**: wrap a `Thread.sleep(200)` inside a `synchronized` method,
   launch 2×cores VTs through it, and run with `-Djdk.tracePinnedThreads=1`.
   Paste one trace line. Then convert the method to `ReentrantLockCounter` style
   and show the trace disappears and wall-time drops.
5. **ThreadLocal bomb**: store a 1 KB `byte[]` in a `ThreadLocal` inside 100k VTs
   (with `remove()` omitted) vs passing the array as a lambda parameter. Compare
   peak heap (`Runtime.totalMemory()-freeMemory()`) and explain why `bestPractices()`
   bans `ThreadLocal` at VT scale, referencing `ThreadBasicsDemo.ThreadLocalExample.cleanup()`.

---

## 5. QUIZ

1. What is the scheduling difference between a platform thread and a virtual thread, and what does it imply for per-thread stack cost?
2. Name the two pinning conditions and explain why pinning destroys the scalability win.
3. What lifetime guarantee does structured concurrency (`newVirtualThreadPerTaskExecutor` / `StructuredTaskScope`) give that raw `ExecutorService` + `Future` does not?
4. Your VT service is I/O-bound but shows carrier saturation. You find a `synchronized` cache method doing a DB call. What is the minimal fix, and how do you verify it?
5. When should you *not* use virtual threads? Give two cases and the alternative for each.

<details><summary>Answers</summary>

1. Platform thread = 1:1 with an OS thread, ~1 MB pre-committed stack, kernel-scheduled. Virtual thread = M:N multiplexed by the JDK onto few carrier threads; stack is a heap object starting at a few KB. Hence ~10k platform threads OOM while 10k–1M VTs fit in heap (`massiveConcurrency` vs the platform swap in Exercise 1).
2. (a) Inside `synchronized` block/method, (b) calling native/JNI code. The VT cannot unmount, so a blocking call holds the whole carrier OS thread hostage — throughput collapses to carrier count and the M:N advantage vanishes. Fix with `ReentrantLock`, shrink the critical section, detect via `jdk.tracePinnedThreads=1`.
3. The try-block (scope) exit guarantees every subtask finished or was cancelled — no leaks, deterministic lifetime. Raw `ExecutorService` requires manual `shutdown()`/`awaitTermination`/`shutdownNow()` (`ThreadPoolExample`) and orphaned `Future`s keep running unless explicitly cancelled (Exercise 3).
4. Replace `synchronized` with `ReentrantLock` (`ReentrantLockCounter` pattern: `lock()`/`try-finally-unlock()`), keeping the DB call inside the lock if semantics require it — `LockSupport.park` unmounts cleanly. Verify with `-Djdk.tracePinnedThreads=1` (traces gone) and wall-time / carrier-utilisation drop under load.
5. CPU-bound work (no blocking ⇒ no unmount benefit; use a platform pool sized to cores, e.g. `newFixedThreadPool(cores)`) and code that must hold `synchronized`/JNI across blocking calls (refactor first, or stay on platform threads). Also: don't pool VTs (create fresh per task) and don't use `ThreadLocal` at VT scale (pass context explicitly / scoped values).

</details>

---

## 6. FLASHCARDS

- Q: Platform vs virtual thread mapping? → A: 1:1 OS thread (~1 MB) vs M:N on carrier threads (~KB heap object).
- Q: What unmounts a VT? → A: Blocking (sleep, socket read, `Future.get`, lock park) frees the carrier for another VT.
- Q: Two pinning conditions? → A: `synchronized` block/method; native/JNI call.
- Q: Why does pinning hurt? → A: Carrier blocked too; throughput capped at carrier count.
- Q: Pinning fix priority #1? → A: `synchronized` → `ReentrantLock` (`ReentrantLockCounter` pattern).
- Q: Detect pinning flag? → A: `-Djdk.tracePinnedThreads=1`.
- Q: Structured concurrency guarantee? → A: Scope exit ⇒ all subtasks done/cancelled; `ShutdownOnFailure` / `ShutdownOnSuccess` policies.
- Q: VT executor spelling? → A: `Executors.newVirtualThreadPerTaskExecutor()` in try-with-resources.
- Q: VTs daemon default + consequence? → A: Yes daemon — must `join()`/await scope or JVM exits early.
- Q: `ThreadLocal` at VT scale? → A: 1M VTs = 1M copies; pass params / scoped values; always `remove()` (`ThreadLocalExample.cleanup()`).
- Q: Don't-use-VT cases? → A: CPU-bound (platform pool ≈ cores); long pinned sections; never pool VTs.

---

## 7. MINI_PROJECT

**Per-request VT echo server.** Build a TCP server where each accepted connection
is handled by one virtual thread (`newVirtualThreadPerTaskExecutor`), replacing
the fixed-pool pattern from `ThreadBasicsDemo.ThreadPoolExample`:

1. Server accepts N concurrent clients; each handler sleeps 50 ms (simulated DB)
   then echoes. Benchmark N = 1k/10k clients: VT-per-request vs
   `newFixedThreadPool(50)`. Record wall-time and max heap.
2. Add a shared `synchronized` request counter with a `sleep` inside (deliberate
   pin). Reproduce carrier saturation, capture a `tracePinnedThreads` line.
3. Refactor to `AtomicCounter`/`ReentrantLockCounter` style; show saturation gone.
4. Wrap the per-connection fan-out (auth + profile fetch) in one structured scope:
   if auth fails, the profile fetch must be cancelled — assert via a test that the
   sibling task observed interruption within 500 ms.
5. Tests: daemon-join correctness (no flaky missing output), pin-free assertion
   (no `synchronized`-around-I/O in handler code — grep the source in the test),
   and a 10k-connection soak that the platform-thread variant fails.

---

## 8. REAL_WORLD_PROJECT

**Blocking-to-virtual web-service migration.** Take a Spring MVC (servlet,
thread-per-request) endpoint that fans out to 3 downstream HTTP calls
sequentially — the production shape `bestPractices()` targets ("task-per-request"):

1. Baseline on platform threads (Tomcat default pool ~200): load-test with 500
   concurrent users; record p50/p99 and thread-pool queue rejections.
2. Migrate to virtual threads (Spring Boot 3.2+: `spring.threads.virtual.enabled=true`
   or Tomcat's VT executor): same load test; document p99 change and the removal
   of pool-tuning. Map each step to `Lab` methods (`creatingVirtualThreads` →
   request threads, `structuredConcurrency` → downstream fan-out).
3. Pinning audit: grep for `synchronized` on request paths (cache, session,
   `ThreadBasicsDemo`-style counters); convert to `ReentrantLock`/`AtomicInteger`
   per §2.5; re-run with `jdk.tracePinnedThreads=1` in staging and attach the
   before/after trace delta.
4. Correctness hardening: replace request-scoped `ThreadLocal` with explicit
   parameters (cite `ThreadLocalExample.cleanup()` leak lesson); add a structured
   `ShutdownOnFailure` fan-out so one downstream failure cancels siblings instead
   of leaking `Future`s (cite `FutureExample` vs §2.4).
5. Ship with a runbook: when to scale carriers (carrier = core; add cores, not
   threads), dashboards (carrier utilisation, pinning events, VT count), and a
   rollback criterion (CPU-bound endpoint regression ⇒ revert that endpoint to a
   bounded platform pool per §1.5 table).
