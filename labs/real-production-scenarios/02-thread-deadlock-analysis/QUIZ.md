# Lab 02 — Thread Deadlock Analysis: Quiz

## Instructions
Answer 10 questions to test your knowledge of Java thread deadlock detection and analysis. Each has one correct answer. Answers and explanations are at the end.

---

## Questions

### Q1: Which of the four Coffman conditions for deadlock is violated by using a timeout when acquiring locks?
- A) Mutual Exclusion
- B) Hold and Wait
- C) No Preemption
- D) Circular Wait

### Q2: In a thread dump, what state indicates a thread is blocked waiting for a monitor lock?
- A) RUNNABLE
- B) BLOCKED
- C) WAITING
- D) TIMED_WAITING

### Q3: What is the difference between `BLOCKED` and `WAITING` thread states in a thread dump?
- A) BLOCKED = waiting for monitor; WAITING = waiting for notify/park
- B) BLOCKED = waiting for I/O; WAITING = waiting for lock
- C) BLOCKED = timed wait; WAITING = infinite wait
- D) No difference, they are synonyms

### Q4: You run `jcmd <pid> Thread.print` and see: `"Thread-1" BLOCKED on java.lang.Object@12345 owned by "Thread-2"`. Thread-2 shows `RUNNABLE`. What does this mean?
- A) Thread-1 holds the lock, Thread-2 wants it
- B) Thread-2 holds the lock, Thread-1 is blocked waiting for it
- C) Both threads are deadlocked
- D) Thread-1 is waiting for Thread-2 to finish

### Q5: Which tool can automatically detect deadlocks from a thread dump?
- A) jstack -l
- B) jcmd Thread.print -deadlock
- C) Both A and B
- D) Neither, manual analysis required

### Q6: A deadlock involves 3 threads: T1 holds L1 wants L2, T2 holds L2 wants L3, T3 holds L3 wants L1. What is the minimum number of threads that must be interrupted to break the deadlock?
- A) 1
- B) 2
- C) 3
- D) 0 (deadlock will resolve itself)

### Q7: What is the purpose of `ThreadMXBean.findDeadlockedThreads()`?
- A) Returns all threads in BLOCKED state
- B) Returns thread IDs involved in a monitor deadlock
- C) Returns threads waiting on I/O
- D) Returns threads holding the most locks

### Q8: Which lock ordering strategy prevents deadlocks?
- A) Always acquire locks in random order
- B) Always acquire locks in a consistent global order
- C) Never acquire more than one lock
- D) Use `tryLock()` with timeout for all locks

### Q9: In a Java application using `ReentrantLock`, you suspect a deadlock but `ThreadMXBean.findDeadlockedThreads()` returns null. Why?
- A) No deadlock exists
- B) `findDeadlockedThreads()` only detects monitor (synchronized) deadlocks, not `ReentrantLock`
- C) The deadlock involves only 2 threads
- D) The JVM version doesn't support it

### Q10: What is the correct way to use `tryLock()` with timeout to avoid deadlock?
- A) `lock.tryLock(5, TimeUnit.SECONDS)` — if false, retry immediately
- B) `lock.tryLock(5, TimeUnit.SECONDS)` — if false, release all held locks, wait randomly, retry
- C) `lock.tryLock()` — no timeout, same as `lock()`
- D) `lock.tryLock(5, TimeUnit.SECONDS)` — if false, throw exception and crash

---

## Answer Key

| Question | Answer | Explanation |
|---|---|---|
| 1 | **C** | Timeout allows preemption — if lock not acquired within time, thread releases held locks and retries, violating "No Preemption". |
| 2 | **B** | `BLOCKED` means waiting to enter a synchronized block/method (monitor). `WAITING` means `Object.wait()` or `LockSupport.park()`. |
| 3 | **A** | BLOCKED = waiting for monitor lock entry. WAITING = waiting indefinitely for another thread to perform an action (notify/park/unpark). |
| 4 | **B** | The thread dump explicitly states Thread-1 is BLOCKED on an object owned by Thread-2. Thread-2 holds the lock. |
| 5 | **C** | Both `jstack -l` and `jcmd Thread.print` include deadlock detection output at the end of the dump. |
| 6 | **A** | Interrupting any one thread in the cycle breaks the circular wait. That thread releases its lock, allowing the next to proceed. |
| 7 | **B** | `findDeadlockedThreads()` returns an array of thread IDs that are deadlocked on monitors. Returns null if no deadlock detected. |
| 8 | **B** | Consistent global lock ordering prevents circular wait. If all threads acquire L1 before L2, T1(L1→L2) and T2(L1→L2) cannot deadlock. |
| 9 | **B** | `ThreadMXBean.findDeadlockedThreads()` only detects deadlocks on intrinsic monitors (`synchronized`). For `Lock` objects, use `findMonitorDeadlockedThreads()` (Java 8+) or analyze thread dump manually. |
| 10 | **B** | On timeout, release ALL held locks, wait with jitter (random backoff), then retry. This breaks hold-and-wait and prevents livelock. |

---

## Scoring Guide
- **10/10**: Expert — can diagnose deadlocks in production under pressure
- **8-9/10**: Strong — solid understanding of thread states and lock mechanics
- **6-7/10**: Developing — review thread dump analysis and Coffman conditions
- **<6/10**: Needs study — revisit Java concurrency fundamentals