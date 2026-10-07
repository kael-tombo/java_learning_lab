# References: Locking & Synchronization

## Official Documentation
- [AbstractQueuedSynchronizer Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/AbstractQueuedSynchronizer.html)
- [ReentrantLock Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html)
- [StampedLock Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/StampedLock.html)
- [LockSupport Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/LockSupport.html)

## JEPs
- JEP 374: Deprecate and Disable Biased Locking

## Books
- *Java Concurrency in Practice* by Brian Goetz (Chapter 14: Building Custom Synchronizers)
- *The Art of Multiprocessor Programming* by Herlihy & Shavit
- *Java Performance: The Definitive Guide* by Scott Oaks

## Articles
- AQS Internals
- LockSupport Guide
- StampedLock Guide

## Source Code
- `java.base/java/util/concurrent/locks/AbstractQueuedSynchronizer.java`
- `java.base/java/util/concurrent/locks/ReentrantLock.java`
- `java.base/java/util/concurrent/locks/StampedLock.java`
- `java.base/java/util/concurrent/locks/LockSupport.java`
- `java.base/jdk/internal/misc/Unsafe.java`
