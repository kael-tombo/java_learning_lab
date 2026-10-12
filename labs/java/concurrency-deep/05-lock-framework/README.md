# Lab 05 — Lock Framework (AQS): README

## What this lab covers

`AbstractQueuedSynchronizer` (AQS) is the engine behind `ReentrantLock`,
`Semaphore`, `CountDownLatch`, and `ReentrantReadWriteLock`: one volatile
`int state` plus a CLH-variant FIFO queue of waiter nodes. Subclasses define
what `state` means (lock count, permits, latch count) through
`tryAcquire`/`tryRelease`; AQS owns queuing, parking (`LockSupport.park`),
and wakeup.

## Why AQS instead of `synchronized`

`synchronized` (lab 02) gives one lock mode, one wait-set, no timeout, no
interruption, no fairness choice. AQS adds:

- `tryLock(timeout)` — bounded acquisition via timed queue nodes
- `lockInterruptibly()` — cancellation unlinks the node (`CANCELLED`)
- fair vs nonfair `ReentrantLock` (queue check vs barging CAS)
- multiple `ConditionObject` wait-queues per lock (`notFull`/`notEmpty`)
- shared mode (`Semaphore`, `CountDownLatch`, read locks)

## Map of this lab

- `THEORY.md` — state + queue, acquire path, fair/nonfair source, JDK 23
  status bits (`WAITING=1`, `COND=2`, `CANCELLED=0x80000000`), conditions,
  shared mode, 16/16-bit RW split (`MAX_COUNT=65535`)
- `CODE_DEEP_DIVE.md` — runnable snippets: barging contract, `tryLock`
  timeout, `ConditionObject` producer/consumer, semaphore uncapped permits,
  RW downgrade-vs-upgrade
- `ARCHITECTURE.md` / `INTERNALS.md` / `HOW_IT_WORKS.md` — layering, queue
  mechanics, acquire/release walkthrough
- `MATH_FOUNDATION.md` — barging throughput model, queueing sketch, RW
  bit arithmetic
- `STEP_BY_STEP.md` + `EXERCISES.md` — build a mutex on AQS, then conditions
- `PERFORMANCE.md`, `DEBUGGING.md`, `COMMON_MISTAKES.md`, `REFACTORING.md`
  — measurement and repair
- `QUIZ.md`, `FLASHCARDS.md`, `HISTORY.md`, `REFERENCES.md` — check and extend

## Prerequisites

- Lab 02 (`synchronized` block structure, single wait-set limit)
- Lab 03 (volatile/CAS — `compareAndSetState` is a CAS on `state`)
- Lab 04 (`LockSupport.park`/`unpark` basics)

## Starter commands

```bash
# compile the lab sources (adjust path to your checkout)
javac -d out $(find labs/java/concurrency-deep/05-lock-framework/src -name "*.java")
# run any snippet from CODE_DEEP_DIVE.md the same way
java -cp out FairWins
```

## Exit criteria

You can explain: what `state` means for lock vs semaphore vs latch; why the
head node is always a dummy; what nonfair barging buys and risks; why
`tryLock` barges even in fair mode; why RW upgrade deadlocks while downgrade
is safe; and where the JDK 23 status-bit change matters (and where it does not).
