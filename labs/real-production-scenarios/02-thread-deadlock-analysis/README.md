# Lab 02: Thread Deadlock Analysis — Google SRE Production Hang

## Situation Overview

A critical microservice in Google's production infrastructure experienced intermittent application hangs lasting 30 seconds during peak traffic periods. The service, a distributed locking coordinator written in Java, was responsible for managing lease coordination across 200+ nodes in a global deployment. Under high concurrency (10,000+ TPS), the service would become unresponsive for precisely 30 seconds before recovering automatically. These hangs occurred approximately 4-5 times per hour during peak windows, causing cascading timeouts across dependent services.

The application used synchronized blocks and intrinsic locks for state management. The hang duration of exactly 30 seconds was a strong indicator of a thread deadlock: Java's synchronized blocks have no timeout by default, but the application had a watchdog thread that detected unresponsive workers and reset them after 30 seconds. This masked the deadlock but prevented the team from seeing it clearly during initial investigations.

The incident involved Google SRE engineers, the Java Platform team, and database infrastructure engineers over 5 days. The root cause was nested synchronized blocks with inconsistent lock ordering across different code paths. Two threads could acquire locks A and B in opposite order, leading to a circular wait condition that neither thread could break free from.

## Severity Assessment

| Criteria | Rating | Details |
|----------|--------|---------|
| Impact Scope | P1 | 200+ nodes affected, cascading timeouts to dependent services |
| User Facing | Partial | Latency spikes of 30s+ for lease acquisition requests |
| Duration Per Event | 30 seconds | Deadlock broken by watchdog thread reset |
| Frequency | 4-5 times per hour | Only during peak traffic (>10K TPS) |
| Detectability | Low | No explicit deadlock signal; appeared as latency anomaly |
| Root Cause Complexity | Medium | Nested synchronized blocks with inconsistent ordering |
| Fix Complexity | Low | Consistent lock ordering or ReentrantLock with tryLock |
| Blast Radius | Service-wide | Affected all nodes in the global deployment |

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Google Production DC                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Distributed Lock Coordinator            │   │
│  │                                                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │   │
│  │  │ Node 1   │  │ Node 2   │  │ Node 3   │  ...   │   │
│  │  │ (JVM)    │  │ (JVM)    │  │ (JVM)    │       │   │
│  │  └──────────┘  └──────────┘  └──────────┘       │   │
│  │         │              │              │           │   │
│  │         └──────────────┴──────────────┘           │   │
│  │                        │                          │   │
│  │               ┌────────▼────────┐                 │   │
│  │               │  Distributed    │                 │   │
│  │               │  Lease Store    │                 │   │
│  │               │  (Spanner)      │                 │   │
│  │               └─────────────────┘                 │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Internal Architecture (Per Node)

```
┌──────────────────────────────────────────┐
│       Lock Coordinator Node (JVM)         │
│                                          │
│  ┌──────────────┐   ┌──────────────┐    │
│  │  Request      │   │  Lease        │   │
│  │  Handler Pool │──▶│  Manager      │   │
│  │  (20 threads) │   │  (synchronized)│  │
│  └──────────────┘   └──────┬───────┘    │
│                            │            │
│  ┌──────────────┐   ┌──────▼───────┐    │
│  │  Watchdog     │   │  Lock State   │   │
│  │  Thread       │   │  (HashMap)    │   │
│  │  (30s reset)  │   │  (synchronized)│  │
│  └──────────────┘   └──────────────┘    │
│                                          │
│  Lock Order 1: Lock A → Lock B          │
│  Lock Order 2: Lock B → Lock A  ← BUG! │
└──────────────────────────────────────────┘
```

## Locking Pattern (The Bug)

The application had two primary data structures protected by synchronized blocks:

1. **LeaseRegistry**: Manages active leases (keyed by lease ID)
2. **LockState**: Manages lock grants (keyed by resource ID)

Some code paths acquired locks in order: LeaseRegistry → LockState
Other code paths acquired locks in order: LockState → LeaseRegistry

When Thread 1 holds LeaseRegistry and waits for LockState, and Thread 2 holds LockState and waits for LeaseRegistry, a classic deadlock occurs.

## Learning Objectives

1. Identify deadlocks from thread dump analysis (3-sample technique)
2. Distinguish deadlocks from livelocks, starvation, and plain contention
3. Use jstack, VisualVM, and JFR for lock contention analysis
4. Fix deadlocks with consistent lock ordering
5. Use ReentrantLock.tryLock() with timeouts for deadlock prevention
6. Implement deadlock detection and recovery patterns
7. Apply Google SRE's "SLOs for internal services" methodology

## References

- Google SRE Book: "Eliminating Deadlocks in Distributed Systems" — (link removed)
- Oracle: "Java Thread Deadlock — Detection and Prevention" — https://docs.oracle.com/javase/tutorial/essential/concurrency/deadlock.html
- Oracle: "Java Locking Best Practices" — https://docs.oracle.com/javase/8/docs/technotes/guides/concurrency/locking.html
- Google SRE: "Debugging Production Deadlocks" — Google SRE Workbook, Chapter 12
- Microsoft: "Deadlock Detection Patterns" — Microsoft Patterns & Practices
- Baeldung: "Deadlock in Java" — https://www.baeldung.com/java-deadlock-livelock
- VisualVM Documentation — https://visualvm.github.io/
- JFR Events for Lock Instances — Oracle JDK Documentation

## Prerequisites

- JDK 11+ (for improved lock monitoring)
- jstack, jcmd, VisualVM, or JDK Mission Control
- Understanding of Java synchronized, ReentrantLock, and condition variables
- Familiarity with thread dump analysis

## Exercises

1. Analyze the provided thread dumps: identify blocked and waiting threads
2. Trace the lock ordering across different code paths
3. Determine which locks are involved in the deadlock cycle
4. Implement consistent lock ordering fix
5. Implement ReentrantLock.tryLock() with timeout and recovery
6. Write a unit test that detects the deadlock condition
7. Set up JFR monitoring for lock contention events

## Technical Deep Dive: Java Locking Internals

### The Four Coffman Conditions

For a deadlock to occur, all four of these conditions must hold simultaneously:

1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode. In Java, synchronized blocks and ReentrantLock both enforce mutual exclusion.

2. **Hold and Wait**: A thread holds at least one resource while waiting for another. In Java, nested synchronized blocks naturally create this condition.

3. **No Preemption**: Resources cannot be forcibly taken from a thread. Java's synchronized provides no preemption mechanism. ReentrantLock.lock() also does not preempt, but tryLock() does (it backs off if it cannot acquire).

4. **Circular Wait**: A cycle exists where Thread A waits for a resource held by Thread B, which waits for a resource held by Thread A. This is the condition that consistent lock ordering addresses.

### Why synchronized is Dangerous

The synchronized keyword provides no timeout mechanism. Once a thread enters a synchronized block and cannot acquire the next lock, it waits forever (until the lock is released). In thread-pooled environments, this means:

- The blocking thread occupies a thread pool slot
- Other tasks queue up waiting for a thread
- If enough threads are blocked, the entire application hangs
- No recovery is possible without external intervention (watchdog, kill, restart)

### The 3-Sample Thread Dump Technique

The correct way to distinguish deadlock from transient contention:

```
Sample 1 (T=0s): 
  Thread A: BLOCKED on Lock X
  Thread B: BLOCKED on Lock Y

Sample 2 (T=5s):
  Thread A: BLOCKED on Lock X (same)
  Thread B: BLOCKED on Lock Y (same)

Sample 3 (T=10s):
  Thread A: BLOCKED on Lock X (same)
  Thread B: BLOCKED on Lock Y (same)
  └── CONFIRMED DEADLOCK (no progress over 10 seconds with same locks)
```

If the threads had resolved between samples, it was temporary contention, not deadlock.

### ReentrantLock vs synchronized Decision Matrix

| Scenario | synchronized | ReentrantLock | Winner |
|----------|-------------|---------------|--------|
| Single lock, simple critical section | ✅ Simple | ✅ Works | synchronized |
| Nested locks, multiple code paths | ❌ No timeout | ✅ tryLock(timeout) | ReentrantLock |
| Fairness required | ❌ Unfair | ✅ Fair mode | ReentrantLock |
| Read-heavy workload | ❌ Exclusive | ✅ ReadWriteLock | ReadWriteLock |
| Interruptible locking | ❌ No | ✅ lockInterruptibly() | ReentrantLock |
| Condition variables | ❌ wait/notify only | ✅ Condition.await() | ReentrantLock |
| Low overhead | ✅ Lightweight | ❌ Slightly heavier | synchronized |
| Deadlock detection | ❌ Manual only | ✅ tryLock detection | ReentrantLock |

## Common Deadlock Patterns in Production

### Pattern 1: The Classic Nested Lock

Two locks acquired in different orders across methods. This is the most common deadlock pattern in enterprise Java applications.

### Pattern 2: The Callback Deadlock

A thread holds Lock A and calls a callback/listener that tries to acquire Lock A again (reentrant). If the lock is not reentrant, this is a self-deadlock. Java's synchronized and ReentrantLock are both reentrant, so this only applies to non-reentrant custom locks.

### Pattern 3: The Resource Pool Deadlock

Thread A holds Connection 1 and waits for Connection 2. Thread B holds Connection 2 and waits for Connection 1. This is a connection pool deadlock, common in multi-data-source scenarios.

### Pattern 4: The Thread Pool Deadlock

A fixed-size thread pool submits a task that waits for another task in the same pool. If the pool is full and all threads are blocked waiting, no thread is available to execute the dependent task. This is thread pool starvation, not technically a deadlock, but manifests identically.

## JFR Lock Event Analysis Guide

When analyzing JFR recordings for lock contention:

| JFR Event | What It Detects | How to Read |
|-----------|-----------------|-------------|
| jdk.JavaMonitorEnter | Thread entering synchronized block | High count = high contention |
| jdk.JavaMonitorWait | Thread waiting on Object.wait() | Pair with notify events |
| jdk.ThreadPark | Thread parked by LockSupport.park() | ReentrantLock contention |
| jdk.Lock (JDK 14+) | ReentrantLock acquisition | Shows lock identity, hold time |
| jdk.SyncOnValueBasedClass | Synchronizing on value-based class | Potential bug (e.g., Long, Double) |

## Practice Scenarios

### Scenario A: Diagnose a Deadlocked JVM
You receive an alert that the lock coordinator service is not responding. The thread dump shows multiple threads in BLOCKED state. Walk through the investigation using the CHECKLIST.md.

Steps:
1. Run `jstack -l <pid>` to capture thread dump
2. Search for "Found one Java-level deadlock" in the output
3. Identify the locks involved and their holders
4. Trace the call stack of each deadlocked thread
5. Determine which code paths acquired locks in inconsistent order

### Scenario B: Fix Inconsistent Lock Ordering
The deadlock involves three locks: CacheLock → DBLock → NetworkLock. Some methods acquire them in order A→B→C, others in B→A→C, and others in C→A→B. Establish the correct ordering and rewrite the inconsistent methods.

### Scenario C: Implement tryLock with Timeout
A codebase uses nested synchronized blocks throughout. Migrate it to ReentrantLock.tryLock() with 100ms timeout and retry logic. Test that the new code cannot deadlock even with inconsistent ordering.

## Advanced Topics

### Lock-Free Alternatives
For ultra-high-throughput scenarios, consider lock-free data structures:
- ConcurrentHashMap (lock-free reads, striped locks for writes)
- AtomicReference / AtomicLongFieldUpdater
- LongAdder (striped counters, better than AtomicLong for high contention)
- StampedLock (optimistic reads, no blocking for readers)

### Deadlock Detection in Distributed Systems
In microservice architectures, deadlocks can span multiple services:
- Service A holds Resource X and calls Service B for Resource Y
- Service B holds Resource Y and calls Service A for Resource X
- This creates a distributed deadlock that thread dumps cannot detect

Solutions:
1. Use distributed tracing to detect call cycles
2. Implement timeouts on all inter-service calls
3. Use a distributed lock manager (ZooKeeper, etcd)
4. Apply the same consistent ordering principle across service boundaries

### Performance Impact of Locking

Locking overhead increases with contention level:
- No contention: ~25ns for synchronized, ~50ns for ReentrantLock
- Low contention: ~1-10μs (CAS retries)
- High contention: ~1-100ms (thread scheduling, context switching)
- Deadlock: ∞ (until watchdog interference)

The key insight: deadlock is not just a correctness bug — it's potentially the most expensive performance bug in concurrent systems.

## Production Deadlock Recovery Patterns

### Pattern A: Deadlock Detection + Interrupt

Use ThreadMXBean.findDeadlockedThreads() to detect and interrupting one thread to break the cycle:

```java
ThreadMXBean bean = ManagementFactory.getThreadMXBean();
long[] deadlockedIds = bean.findDeadlockedThreads();
if (deadlockedIds != null) {
    for (long id : deadlockedIds) {
        ThreadInfo info = bean.getThreadInfo(id);
        // Interrupt the lowest-priority thread
        Thread.getAllStackTraces().keySet().stream()
            .filter(t -> t.getId() == id)
            .findFirst()
            .ifPresent(Thread::interrupt);
    }
}
```

### Pattern B: Watchdog Thread with Reset

The approach used in this incident — a watchdog resets the application after a timeout. This is a last resort because it loses all in-flight work.

### Pattern C: tryLock with Backoff

The cleanest approach — use ReentrantLock.tryLock() with timeout instead of synchronized or lock(). Threads that cannot acquire locks within the timeout release all held locks and retry, guaranteeing progress.

## Advanced Investigation Techniques

### Automated Deadlock Detection in CI/CD

Add deadlock detection to your CI/CD pipeline:

```java
@Test
void serviceShouldNotDeadlock() throws Exception {
    // Create high-concurrency scenario
    ExecutorService exec = Executors.newFixedThreadPool(50);
    CountDownLatch startLatch = new CountDownLatch(1);
    List<Future<?>> futures = new ArrayList<>();
    
    for (int i = 0; i < 100; i++) {
        futures.add(exec.submit(() -> {
            try {
                startLatch.await();
                // Exercise all methods that acquire locks
                service.methodA();
                service.methodB();
                service.methodC();
            } catch (Exception e) {
                // Interrupted during deadlock recovery
            }
        }));
    }
    
    startLatch.countDown(); // Release all threads at once
    
    // Check for deadlock after 10 seconds
    Thread.sleep(10000);
    ThreadMXBean bean = ManagementFactory.getThreadMXBean();
    long[] deadlocked = bean.findDeadlockedThreads();
    assertNull(deadlocked, "Deadlock detected! Deadlocked thread IDs: " +
        Arrays.toString(deadlocked));
    
    exec.shutdownNow();
}
```

### Using JFR for Lock Contention Analysis

Key JFR events for lock analysis:

1. **jdk.JavaMonitorEnter**: When a thread enters a synchronized block — look for high contention count
2. **jdk.JavaMonitorWait**: When a thread calls Object.wait() — look for long wait times
3. **jdk.ThreadPark**: When a thread parks (ReentrantLock contention) — look for frequent parking
4. **jdk.Lock (JDK 14+)**: ReentrantLock events — shows lock identity, hold time, queue length

In JDK Mission Control:
1. Open JFR recording
2. Go to "Threading" → "Lock Contention" view
3. Sort by "Contention Time" to find the most contended locks
4. Examine the stack traces for the contended locks
5. Identify lock ordering issues by comparing stack traces

### Analyzing Lock Contention with async-profiler

```bash
# Lock profiling
profiler.sh -d 60 -e lock -f /tmp/lock_flame.html <pid>

# Wall-clock profiling (includes blocked time)
profiler.sh -d 60 -e wall -f /tmp/wall_flame.html <pid>
```

Lock flame graphs show:
- Wide bars at the top = highly contended locks
- The calling methods of contended locks
- Thread state distribution (running vs. blocking)

## FAQ

### Q: How do I distinguish deadlock from livelock?
In a deadlock, threads are BLOCKED waiting for locks and make no progress. Thread dumps show BLOCKED state. In a livelock, threads are RUNNABLE but keep retrying the same operation (e.g., two threads keep yielding to each other). Livelock thread dumps show RUNNABLE state with repetitive stack traces.

### Q: Can synchronized blocks timeout?
No. The synchronized keyword has no timeout mechanism. Once a thread cannot acquire a nested lock, it waits indefinitely. Use ReentrantLock.tryLock(timeout) for nested locking.

### Q: What's the best way to detect deadlocks in production?
ThreadMXBean.findDeadlockedThreads() in a periodic health check is most reliable. JFR's jdk.JavaMonitorEnter events help identify lock contention. A scheduled task checking every 5 seconds provides early detection.

### Q: Can microservices experience distributed deadlocks?
Yes. Service A holds Resource X and calls Service B for Resource Y. Service B holds Resource Y and calls Service A for Resource X. Distributed tracing and consistent resource ordering across services prevent these.

### Q: Should I use synchronized or ReentrantLock?
Use synchronized for simple, single-lock critical sections. Use ReentrantLock for timeouts (tryLock), fair ordering, condition variables, or interruptible locking. For nested locks, always prefer ReentrantLock with tryLock.

### Q: Can the JVM detect deadlocks automatically?
Yes (JDK 6+). jstack/jcmd output includes "Found one Java-level deadlock" for intrinsic locks. ThreadMXBean.findDeadlockedThreads() detects all lock types (JDK 6u22+).

## Glossary

| Term | Definition |
|------|------------|
| Deadlock | Two or more threads blocked forever, each waiting for a resource held by another |
| Livelock | Threads active but making no progress due to mutual interference |
| Starvation | Thread perpetually denied access to a needed resource |
| Intrinsic Lock | Lock associated with every Java object (used by synchronized) |
| Explicit Lock | Lock object (ReentrantLock) with advanced features |
| Reentrant | Lock acquirable multiple times by the same thread |
| Fair Lock | Lock granting access to longest-waiting thread first |
| Coffman Conditions | Four necessary conditions for deadlock: ME, H&W, No Preemption, Circular Wait |
| Lock Ordering | Sequence in which multiple locks are acquired |
| tryLock | ReentrantLock method that acquires with timeout |
| Watchdog | Monitoring thread that detects and recovers from hangs |

