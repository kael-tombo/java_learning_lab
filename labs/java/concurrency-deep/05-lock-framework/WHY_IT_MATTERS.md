# Why the Lock Framework Matters

## Everyday code that depends on it

- Every `ReentrantLock` in connection pools, caches, and task queues.
- Every `Semaphore`-bounded resource: JDBC pool slots, rate limiters,
  backpressure gates.
- Every `CountDownLatch` start gate in tests and service bootstrap.
- `ArrayBlockingQueue`'s two conditions (`notEmpty`/`notFull`) — the standard
  bounded buffer.
- `ReentrantReadWriteLock` in read-heavy caches and config registries.

## The bug classes it removes

- Single-wait-set thundering herd: `signal()` on the right condition wakes
  only the relevant waiters instead of `notifyAll()` waking everyone.
- Unbounded blocking: `tryLock(300, MILLISECONDS)` converts "hang forever"
  into a branch you can log, retry, or fail fast.
- Uncancellable waits: `lockInterruptibly()` lets shutdown interrupt a queued
  thread; interruption unlinks its node and heals the queue.

## The bug classes it introduces

- Forgotten `unlock`: no block structure means an exceptional path that skips
  `finally` wedges the lock at `state != 0` forever.
- Permit leaks: `Semaphore.release()` without a matching acquire inflates
  `state` past the intended cap — permits are uncapped, so over-release is
  silent growth, not an exception.
- Read-to-write upgrade deadlock: holding a read lock while requesting write
  blocks behind your own read hold — the classic self-deadlock, by design.
- Fair-mode throughput tax: queue checks plus unpark handoff latency on every
  acquisition under contention.

## Interview-grade one-liners

- "AQS is one `int state` plus a CLH-variant queue; subclasses define the
  state meaning."
- "Nonfair `lock()` barges with an unguarded CAS; fair `lock()` checks
  `hasQueuedThreads()` first."
- "Head is always a dummy; a thread becomes head exactly when it acquires."
- "`signal` moves a node between queues; it never transfers lock ownership."
- "Downgrade is safe, upgrade deadlocks."
