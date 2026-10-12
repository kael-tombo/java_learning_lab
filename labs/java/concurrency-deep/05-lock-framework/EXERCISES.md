# Exercises: Lock Framework

All snippets compile on JDK 9+ with no dependencies.

## 1. Mutex on raw AQS (write it)

```java
import java.util.concurrent.locks.AbstractQueuedSynchronizer;

class Mutex extends AbstractQueuedSynchronizer {
    void lock() { acquire(1); }
    void unlock() { release(1); }
    @Override protected boolean tryAcquire(int a) {
        if (compareAndSetState(0, 1)) { setExclusiveOwnerThread(Thread.currentThread()); return true; }
        return false;
    }
    @Override protected boolean tryRelease(int a) {
        if (getState() == 0 || getExclusiveOwnerThread() != Thread.currentThread())
            throw new IllegalMonitorStateException();
        setExclusiveOwnerThread(null); setState(0); return true;
    }
    @Override protected boolean isHeldExclusively() {
        return getState() == 1 && getExclusiveOwnerThread() == Thread.currentThread();
    }
}
```

Task: 8 threads × 50K increments under `Mutex` must total 400K. Then drop an
`unlock` on one path and watch the hang — that is the `finally` lesson.

## 2. `tryLock` with deadline

```java
ReentrantLock lock = new ReentrantLock();
lock.lock();
Thread t = new Thread(() -> {
    try {
        boolean got = lock.tryLock(300, TimeUnit.MILLISECONDS);
        System.out.println("acquired within deadline: " + got); // expect false
    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
});
t.start(); t.join(); lock.unlock();
```

Vary the deadline vs hold time; confirm `false` converts a hang into a branch.

## 3. Two-condition bounded buffer

Build `put`/`take` on one `ReentrantLock` with `notFull`/`notEmpty`. Producers
`while (count == N) notFull.await()`, consumers `while (count == 0)
notEmpty.await()`. Signal the *matching* condition after each mutation.
Run 4 producers + 4 consumers × 10K items; assert FIFO count integrity.

## 4. Semaphore cap audit

`Semaphore(3)` guarding a pool: after a fixed workload print
`availablePermits()` — must equal 3 at quiescence. Inject one double-release,
re-run, and show the drift to 4. Fix by pairing acquire/release in
try/finally.

## 5. Downgrade vs upgrade

Downgrade (safe): hold write, take read, release write, use read, release
read. Upgrade (deadlock demo — do with `tryLock` + timeout, never bare
`lock()`): hold read, `writeLock().tryLock(200ms)` returns `false` while your
own read is held. Explain why in one paragraph.

## 6. Fair vs nonfair observation

`new ReentrantLock(true/false)` + `isFair()` assertions (see
CODE_DEEP_DIVE.md section 1). Then run 8 contenders with 200ns bodies and
record victim p99 wait in each mode — report which mode collapses the tail.
