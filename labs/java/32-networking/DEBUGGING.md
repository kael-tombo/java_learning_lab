# Debugging Guide

## Common Debugging Scenarios

### Scenario 1: Unexpected Null Values

Add null checks at service boundaries. Verify dependencies are properly injected. Use java.util.Objects.requireNonNull().

### Scenario 2: Wrong Results

Add logging at each transformation step. Verify input values. Check for integer overflow. Verify floating-point precision.

### Scenario 3: Concurrency Issues

Intermittent failures often indicate shared mutable state. Check synchronization. Use thread dumps to identify deadlocks.

## Debugging Tools

### JVM Flags
- -XX:+PrintGCDetails — GC logging
- -XX:+HeapDumpOnOutOfMemoryError — Auto heap dump
- -Xlog:all — Unified logging (Java 9+)

### Command-Line Tools
- jps — List Java processes
- jstack — Thread dump
- jmap — Heap dump
- jstat — GC statistics
- jcmd — Comprehensive diagnostic tool

### Visual Tools
- VisualVM — All-in-one monitoring
- JMC (Java Mission Control) — Flight recording analysis
- async-profiler — Low-overhead sampling profiler

## Debugging Process

1. Reproduce — Create a reliable way to trigger the bug
2. Isolate — Find the minimal test case
3. Diagnose — Use tools to understand what is happening
4. Fix — Apply the correction
5. Verify — Test the fix thoroughly
6. Prevent — Add tests to prevent regression

## Logging for Debugging

Add strategic logging at key decision points. Enable debug logging with -Dlogging.level.com.javaacademy=DEBUG.
