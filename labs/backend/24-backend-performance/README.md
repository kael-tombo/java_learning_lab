# Lab 24: Backend Performance Optimization

## Overview
Master performance optimization techniques: JMH benchmarking, connection pooling, async I/O, caching strategies, and JVM tuning.

## Topics Covered
- JMH (Java Microbenchmark Harness)
- Connection pooling (HikariCP tuning)
- Asynchronous I/O and non-blocking patterns
- Caching strategies (Caffeine, Redis)
- JVM tuning (GC, heap sizing)
- Profiling with Async Profiler
- Database query optimization
- HTTP client performance
- Reactive performance patterns

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- Understanding of JVM internals

## Key Dependencies
`xml
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\24-backend-performance "THEORY.md") @"
# Theory: Backend Performance

## 1. JMH Benchmarks

JMH provides accurate microbenchmarks by:
- Forking JVMs to prevent optimization bias
- Warmup iterations to JIT compile code
- Blackhole to consume results preventing dead code elimination
- Benchmark modes: Throughput, AverageTime, SampleTime, SingleShotTime

## 2. Connection Pooling

HikariCP is the fastest connection pool:
- pool_size = T * (C - 1) where T=threads, C=connections per thread
- Rule of thumb: pool_size = cores * 2 + effective_spindle_count
- Monitor: active connections, pending requests, timeout rate

## 3. Caching Strategies

- **Cache-Aside**: Application manages cache (most common)
- **Read-Through**: Cache layer loads missing data
- **Write-Through**: Cache updated synchronously
- **Write-Behind**: Cache updated asynchronously
- **Cache-Aside with TTL**: Most common web pattern

## 4. Async I/O

Non-blocking I/O prevents thread-per-request model:
- WebFlux + Netty
- Virtual Threads (Project Loom)
- Reactive types (Mono/Flux)
- Database: R2DBC instead of JDBC

## 5. JVM Tuning Key Parameters

- -Xms/-Xmx: Heap size (start and max)
- -XX:+UseG1GC: Default GC for low pause times
- -XX:MaxGCPauseMillis=100: GC pause target
- -XX:+UseStringDeduplication: Deduplicate strings
- -XX:MetaspaceSize: Class metadata size
