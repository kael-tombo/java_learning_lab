# StampedLock — History

## ReadWriteLock era (Java 5, 2004)

Java 5 shipped `ReentrantReadWriteLock` (JSR-166) with reentrant,
condition-supporting reader/writer semantics. It served well but carried
per-read CAS and queue costs plus the upgrade deadlock: a read-holding
thread could never safely promote to writer without releasing first.

## Optimistic concurrency background

The sample-then-validate idea predates Java: database optimistic
concurrency control (late 1970s–early 1980s literature) lets transactions
proceed without locking and validates at commit, aborting on conflict.
Operating-system sequence locks (seqlocks) apply the same shape to
reader/writer kernel data — version counter sampled around plain reads.
StampedLock is that lineage's JDK incarnation for user-space locking.

## StampedLock arrives (Java 8, 2014)

`java.util.concurrent.locks.StampedLock` was added in Java 8 as part of the
ongoing JSR-166 work led by Doug Lea. The design stripped owner tracking
out of the lock word to fund the optimistic mode and the atomic
read-to-write conversion — explicitly giving up reentrancy and conditions
in exchange. The javadoc documents the resulting obligations (side-effect
freedom, stamp recycling, non-reentrancy) rather than hiding them.

## What did not change since

The stamp protocol — 0-on-write-hold sampling, fenced validation, 0-on
contention conversion — has been stable since introduction. Later JDKs
carried the class forward with internal maintenance only; the documented
~1-year stamp-recycling bound and the `UnsupportedOperationException` on
both views' `newCondition()` remain as specified.

## Position in the curriculum

Lab 05 (`ReentrantReadWriteLock`) is the prerequisite contrast: reentrant,
condition-capable, upgrade-deadlocked. StampedLock is the specialist
alternative for read-mostly, short-section, callback-free state — and the
bridge to fully lock-free version-based schemes studied later.
