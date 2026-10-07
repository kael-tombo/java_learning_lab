# Threading Deep Dive — Ultra Deep Dive

## 1. Thread Lifecycle at the OS Level

### Java Thread States vs OS Thread States

| Java State | OS State (Linux) | Description |
|------------|-----------------|-------------|
| `NEW` | N/A | Thread created but not started |
| `RUNNABLE` | TASK_RUNNING | Actually running or ready to run |
| `BLOCKED` | TASK_INTERRUPTIBLE | Waiting for monitor lock |
| `WAITING` | TASK_INTERRUPTIBLE | `Object.wait()`, `Thread.join()`, `LockSupport.park()` |
| `TIMED_WAITING` | TASK_INTERRUPTIBLE | WAITING with timeout |
| `TERMINATED` | TASK_ZOMBIE | Thread finished execution |

### The `pthread_create` System Call

When `Thread.start()` is called, the JVM calls the OS to create a native thread:

```c
// HotSpot source: os_linux.cpp
pthread_t tid;
pthread_attr_t attr;
pthread_attr_init(&attr);
pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
// Set stack size from -Xss
pthread_attr_setstacksize(&attr, stack_size);
pthread_create(&tid, &attr, java_start, thread);
```

The `java_start` function is the native entry point that:
1. Sets up the JNI environment
2. Calls `JavaCalls::call()` to invoke `Thread.run()`
3. On completion, cleans up and exits

### Stack Allocation

Each thread gets its own native stack:

```
Thread Stack Layout:
┌─────────────────────────┐  high addresses
│    Stack frame N         │
├─────────────────────────┤
│    Stack frame N-1       │
├─────────────────────────┤
│    ...                   │
├─────────────────────────┤
│    Stack frame 1         │
├─────────────────────────┤
│    Thread-local storage  │
└─────────────────────────┘  low addresses (stack grows down)
```

Stack size defaults:
- Linux x64: 1MB
- Windows: 1MB (JVM default, but Windows default is smaller)
- macOS: varies

Controlled by `-Xss` or `-XX:ThreadStackSize`:
```bash
java -Xss256k   # 256KB stack
java -Xss2m     # 2MB stack
java -Xss1m     # 1MB stack
```

## 2. Loom Virtual Threads vs Platform Threads

Project Loom (virtual threads: previews JEP 425 in 19 and JEP 436 in 20, final as JEP 444 in Java 21) introduces **virtual threads** — lightweight threads managed by the JVM rather than the OS.

### Architecture

```
Platform Threads (traditional):
  [OS Thread 1]  → runs [Java Thread A]
  [OS Thread 2]  → runs [Java Thread B]
  [OS Thread 3]  → runs [Java Thread C]

Virtual Threads (Loom):
  [OS Thread 1]  → runs [Carrier Thread 1]
                    ┌─────────────────────┐
                    │ VT-A ────► VT-B     │  Mount/unmount
                    │ VT-C                │  on carrier
                    └─────────────────────┘
  [OS Thread 2]  → runs [Carrier Thread 2]
                    ┌─────────────────────┐
                    │ VT-D ────► VT-E     │
                    └─────────────────────┘
```

### Key Differences

| Aspect | Platform Thread | Virtual Thread |
|--------|----------------|----------------|
| **OS mapping** | 1:1 with OS thread | Many:1 with carrier thread |
| **Creation cost** | ~1ms + 1MB stack | ~1μs + small stack |
| **Max threads** | Thousands | Millions |
| **Stack** | Fixed (e.g., 1MB) | Dynamic (grows/shrinks) |
| **Pinning** | No | Yes (cannot unmount during certain ops) |
| **`Thread.ofVirtual()`** | N/A | Factory method |

### Creating Virtual Threads

```java
// Java 21+:
Thread vt = Thread.ofVirtual()
    .name("my-virtual-thread")
    .unstarted(() -> System.out.println("Hello"));
vt.start();

// Or via ExecutorService:
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> System.out.println("Hello"));
}
```

### Mount and Unmount

A virtual thread is **mounted** on a carrier thread while running, and **unmounted** (yielded) when it blocks:

```java
public static void main(String[] args) throws Exception {
    var threads = new ArrayList<Thread>();
    for (int i = 0; i < 100_000; i++) {
        int taskId = i;
        threads.add(Thread.ofVirtual().start(() -> {
            // Before blocking: mounted on carrier
            try { Thread.sleep(100); } catch (Exception e) {}
            // During sleep: UNMOUNTED from carrier
            // After sleep: re-mounted on (possibly different) carrier
        }));
    }
    for (var t : threads) t.join();
    System.out.println("Done! Used 100,000 virtual threads.");
}
```

### The Continuation

Virtual threads are built on **continuations** — a mechanism to capture and restore execution state:

```java
// Simplified Continuation API (internal to JDK):
Continuation cont = new Continuation(scope, () -> {
    System.out.println("Part 1");
    Continuation.yield(scope);  // Suspend
    System.out.println("Part 2");
});
cont.run();  // Prints "Part 1", yields
cont.run();  // Prints "Part 2"
```

The continuation captures the stack frames and can be suspended/resumed. This is the core mechanism behind virtual thread unmount/mount.

## 3. Carrier Thread Management

ForkJoinPool serves as the scheduler for virtual threads. Each carrier thread is a ForkJoinPool worker:

```java
// Internal structure:
ForkJoinPool pool = ForkJoinPool.commonPool();
// Each carrier thread:
//   - Has a work-stealing deque
//   - Runs virtual threads as ForkJoinTask<Void> submissions
//   - When a virtual thread parks, the carrier picks up the next task
```

### Carrier Thread Count

Default: `Runtime.getRuntime().availableProcessors()`

Controlled by:
```bash
-Djdk.virtualThreadScheduler.parallelism=N
-Djdk.virtualThreadScheduler.maxPoolSize=N
-Djdk.virtualThreadScheduler.minRunnable=N
```

### Work-Stealing

The ForkJoinPool scheduler uses work-stealing:
1. Each carrier has a deque of virtual threads
2. When a carrier's deque is empty, it steals from other carriers
3. This balances load without centralized coordination

## 4. Yield vs Park

### `Thread.yield()`

```java
Thread.yield();  // Hint to scheduler: I'm willing to give up CPU
```

- OS-level: `sched_yield()` (Linux) or `SwitchToThread()` (Windows)
- Java thread stays RUNNABLE (not WAITING)
- No guarantee: scheduler may immediately re-schedule
- Effect: May reduce CPU contention, but unpredictable

### `LockSupport.park()`

```java
LockSupport.park();  // Current thread blocks until unparked
// For virtual threads: unmounts from carrier!
```

- Java thread WAITING state
- For virtual threads: the carrier is freed to run another virtual thread
- Unpark via: `LockSupport.unpark(thread)`
- Also triggered by: `Object.wait()`, `Thread.sleep()`, blocking I/O

### Park/Unpark Protocol

```java
// Thread 1:
LockSupport.park();       // Block (or unmount)

// Thread 2:
Thread t1 = ...;
LockSupport.unpark(t1);   // Resume (or re-mount)
```

The permit is cumulative — two unpark() calls ensure at most one park() succeeds. This is a "binary semaphore" style mechanism.

## 5. Thread State Transitions with JFR Events

Java Flight Recorder (JFR) can monitor thread state transitions:

```java
// Recording thread states:
import jdk.jfr.*;

public class ThreadStateEvent extends Event {
    @Label("Thread Name")
    String threadName;
    
    @Label("Old State")
    String oldState;
    
    @Label("New State")
    String newState;
}

// Usage:
Thread.State oldState = Thread.currentThread().getState();
blockingOperation();
Thread.State newState = Thread.currentThread().getState();

ThreadStateEvent event = new ThreadStateEvent();
event.threadName = Thread.currentThread().getName();
event.oldState = oldState.name();
event.newState = newState.name();
event.commit();
```

### Common JFR Events for Threading

| Event | Description |
|-------|-------------|
| `jdk.ThreadStart` | Thread started |
| `jdk.ThreadEnd` | Thread ended |
| `jdk.ThreadSleep` | Thread.sleep() called |
| `jdk.ThreadPark` | LockSupport.park() |
| `jdk.JavaMonitorEnter` | Thread entering synchronized block |
| `jdk.JavaMonitorWait` | Object.wait() |
| `jdk.CPULoad` | CPU utilization |

### JFR Thread Dump

```bash
# Record thread states via JFR:
jcmd <pid> Thread.print -l
# Or via JMC: Java Mission Control → Threads view
```

## 6. `synchronized` Under the Hood

### Object Monitor

Each Java object has an associated monitor (implemented via the mark word):

```java
synchronized (obj) {  // monitorenter
    // critical section
}                     // monitorexit
```

The mark word encodes the lock state:

| State | Mark Word |
|-------|-----------|
| Unlocked (biased enabled) | Biasable pattern |
| Biased | Thread ID + epoch |
| Lightweight locked | Pointer to lock record¹ |
| Heavyweight locked | Pointer to OS mutex |

¹ Lock record is in the **stack frame** of the owning thread, not on the heap!

### Biased Locking (removed in Java 15, deprecated in 21)

```bash
-XX:+UseBiasedLocking  # Default pre-Java 15, removed in Java 21
```

Biased locking assumes one thread always owns the lock:
1. First acquisition: set thread ID in mark word
2. Subsequent acquisitions: check thread ID → fast path (no atomic ops)
3. Contention: revoke bias (expensive), upgrade to lightweight

**Removed because**: Maintenance cost > benefit. Modern CPUs handle uncontended CAS well.

### Lock Coarsening

The JIT can merge adjacent synchronized blocks:

```java
synchronized (lock) { a(); }
synchronized (lock) { b(); }
// JIT may merge:
synchronized (lock) { a(); b(); }
```

### Lock Elision (Escape Analysis)

If a lock object is thread-local (doesn't escape), the JIT removes the synchronization entirely:

```java
synchronized (new Object()) {  // Object never escapes this method
    // Lock elision! No synchronization in generated code
}
```

## 7. Thread-Local Variables

### ThreadLocal Implementation

```java
ThreadLocal<String> tl = new ThreadLocal<>();
tl.set("value");
String v = tl.get();
```

Internally:
```java
// Each Thread has a ThreadLocalMap
class Thread {
    ThreadLocal.ThreadLocalMap threadLocals;
}

// ThreadLocalMap is a hash map with weak references as keys
static class ThreadLocalMap {
    static class Entry extends WeakReference<ThreadLocal<?>> {
        Object value;
        Entry(ThreadLocal<?> k, Object v) {
            super(k);
            value = v;
        }
    }
}
```

### Memory Leak Risk

ThreadLocals can leak memory in thread pools:
```java
ThreadLocal<byte[]> tl = new ThreadLocal<>();
executor.submit(() -> {
    tl.set(new byte[1024 * 1024]);  // 1MB held until thread dies
    // Thread returns to pool → ThreadLocal stays!
});
```

**Always call `tl.remove()`** in a finally block when using ThreadLocal in thread pools.

### InheritableThreadLocal

```java
InheritableThreadLocal<String> itl = new InheritableThreadLocal<>();
itl.set("parent-value");

Thread child = new Thread(() -> {
    System.out.println(itl.get());  // "parent-value" — inherited!
});
child.start();
```

Passed via:
```java
// Thread.init():
if (inheritThreadLocals && parent.inheritableThreadLocals != null) {
    this.inheritableThreadLocals = 
        ThreadLocal.createInheritedMap(parent.inheritableThreadLocals);
}
```

## 8. Thread Interruption

### Cooperative Interruption

```java
Thread worker = new Thread(() -> {
    while (!Thread.currentThread().isInterrupted()) {
        doWork();
    }
});
worker.start();
// ... later:
worker.interrupt();  // Sets interrupt flag
```

### Interruptible Blocking

```java
try {
    Thread.sleep(10000);
} catch (InterruptedException e) {
    // Flag is CLEARED when InterruptedException is thrown!
    Thread.currentThread().interrupt();  // Re-set the flag
    return;  // Exit gracefully
}
```

When `InterruptedException` is thrown:
1. The interrupt flag is automatically cleared
2. Good practice: restore the flag via `Thread.currentThread().interrupt()`

## 9. `Thread.onSpinWait()` (Java 9+)

```java
// Busy-wait with spin loop hint:
while (!ready) {
    Thread.onSpinWait();  // Hint: this is a spin loop
}
```

On x86, this compiles to the `PAUSE` instruction. Benefits:
- Power saving (reduces CPU power consumption in spin loops)
- Better hyperthreading performance (frees pipeline resources)
- On ARM: yields to other threads

## 10. Thread Dump Analysis

### Generating Thread Dumps

```bash
# Method 1:
jstack <pid>

# Method 2:
jcmd <pid> Thread.print

# Method 3 (Windows):
<ctrl>+<break> in the console

# Method 4 (programmatic):
ThreadMXBean bean = ManagementFactory.getThreadMXBean();
ThreadInfo[] infos = bean.dumpAllThreads(true, true);
```

### Interpreting a Thread Dump

```
"my-thread" #23 prio=5 os_prio=0 cpu=123.45ms elapsed=456.78s tid=0x1234 nid=0x5678 WAITING
   java.lang.base/java.lang.Object.wait(Native Method)
   - waiting on <0x00000000deadbeef> (a java.util.LinkedList)
   at WorkerQueue.take(WorkerQueue.java:45)
   - locked <0x00000000deadbeef> (a java.util.LinkedList)
   at ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:600)

   Locked ownable synchronizers:
   - <0x00000000cafebabe> (a java.util.concurrent.locks.ReentrantLock$NonfairSync)
```

**Key fields**:
- `nid`: Native thread ID (OS-level)
- `tid`: Java thread ID
- `cpu`: CPU time consumed
- `elapsed`: Thread lifetime
- State: RUNNABLE, BLOCKED, WAITING, TIMED_WAITING
- Stack: Shows where the thread is (and what locks it holds/waits for)
