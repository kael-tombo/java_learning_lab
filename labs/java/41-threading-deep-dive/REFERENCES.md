# References: Threading Deep Dive

## Official Documentation
- [Java Concurrency Tutorial](https://docs.oracle.com/javase/tutorial/essential/concurrency/)
- [ThreadPoolExecutor Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)
- [ForkJoinPool Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.html)
- [CompletableFuture Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html)
- [StructuredTaskScope Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)

## JEPs (JDK Enhancement Proposals)
- JEP 155: Concurrency Updates (ForkJoinPool)
- JEP 266: CompletableFuture Enhancements
- JEP 428: Structured Concurrency (Incubator)
- JEP 444: Virtual Threads (Final)

## Books
- *Java Concurrency in Practice* by Brian Goetz
- *Concurrent Programming in Java* by Doug Lea
- *Java Performance: The Definitive Guide* by Scott Oaks

## Articles
- ForkJoinPool Internals
- [CompletableFuture Guide](https://www.baeldung.com/java-completablefuture)

## Deep Dive References
- [JLS Chapter 17 — Threads and Locks](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html) — Thread specification, wait/notify, memory model
- [JVMS §2.8 — Threads and Locks](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html) — JVM-level thread model
- [Project Loom Wiki](https://wiki.openjdk.org/display/loom/Main) — OpenJDK Loom project
- [Ron Pressler: State of Loom](https://www.youtube.com/watch?v=fDGaJ5a4SUA) — Keynote on virtual threads (JVM Language Summit)
- [HotSpot Thread Management](https://wiki.openjdk.org/display/HotSpot/ThreadManagement) — OpenJDK Wiki on thread internals
- [ForkJoinPool Work-Stealing Algorithm](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.html) — FJP documentation

## Source Code
- `java.base/java/util/concurrent/ThreadPoolExecutor.java`
- `java.base/java/util/concurrent/ForkJoinPool.java`
- `java.base/java/util/concurrent/CompletableFuture.java`
- `java.base/java/util/concurrent/StructuredTaskScope.java`
