package com.learning.virtualthreads;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

public class Lab {

    public static void main(String[] args) throws Exception {
        System.out.println("=== Virtual Threads Lab ===\n");

        creatingVirtualThreads();
        platformVsVirtual();
        massiveConcurrency();
        structuredConcurrency();
        pinnedThreads();
        bestPractices();
    }

    static void creatingVirtualThreads() throws Exception {
        System.out.println("--- Creating Virtual Threads ---");

        var vt1 = Thread.startVirtualThread(() ->
            System.out.println("  [" + Thread.currentThread().getName() + "] Hello from VT"));

        var vt2 = Thread.ofVirtual()
            .name("my-vt")
            .start(() -> System.out.println("  [" + Thread.currentThread().getName() + "] Named VT"));

        var builder = Thread.ofVirtual().name("pool-");
        var threads = new ArrayList<Thread>();
        for (int i = 0; i < 3; i++) {
            int task = i;
            threads.add(builder.start(() ->
                System.out.println("  [" + Thread.currentThread().getName() + "] Task " + task)));
        }

        vt1.join();
        vt2.join();
        for (var t : threads) t.join();
        System.out.println("  All virtual threads completed");
    }

    static void platformVsVirtual() throws Exception {
        System.out.println("\n--- Platform Thread vs Virtual Thread ---");
        System.out.println("  Platform: " + Thread.currentThread().isVirtual());

        var vt = Thread.startVirtualThread(() -> {
            System.out.println("  Virtual:  " + Thread.currentThread().isVirtual());
            System.out.println("  Carrier:  " + Thread.currentThread().getStackTrace()[2]);
        });
        vt.join();

        System.out.println("""
  Platform threads: 1:1 with OS threads, ~1MB stack
  Virtual threads:  M:N with carrier threads, ~few KB stack
  Virtual threads are daemon threads by default
  InheritableThreadLocal requires carrier thread pool
    """);
    }

    static void massiveConcurrency() throws Exception {
        System.out.println("--- Massive Concurrency ---");

        var latch = new CountDownLatch(10_000);
        long start = System.nanoTime();

        for (int i = 0; i < 10_000; i++) {
            int task = i;
            Thread.startVirtualThread(() -> {
                try { Thread.sleep(1); } catch (InterruptedException e) {}
                latch.countDown();
            });
        }

        latch.await();
        long elapsed = System.nanoTime() - start;
        System.out.printf("  10,000 virtual threads: %d ms%n", elapsed / 1_000_000);

        System.out.println("""
  Platform threads would fail at ~10k (OOM or too slow)
  Virtual threads can scale to 100k+ easily
  Ideal for: I/O-bound workloads
    """);
    }

    static void structuredConcurrency() throws Exception {
        System.out.println("\n--- Structured Concurrency (Virtual Threads) ---");

        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            Future<String> user = executor.submit(() -> {
                Thread.sleep(50);
                return "User-1";
            });
            Future<String> order = executor.submit(() -> {
                Thread.sleep(30);
                return "Order-100";
            });

            System.out.println("  Result: " + user.get() + " | " + order.get());
        }

        System.out.println("""
  StructuredTaskScope ensures:
  - All subtasks complete before parent continues
  - If one fails -> others cancelled (ShutdownOnFailure)
  - If one succeeds -> others cancelled (ShutdownOnSuccess)
  No thread leaks, deterministic lifetime
    """);
    }

    static void pinnedThreads() {
        System.out.println("\n--- Pinned Threads ---");
        System.out.println("""
  Virtual threads are "pinned" to carrier thread when:
  1. Inside synchronized block/method
  2. Calling native method (JNI)

  Pinned blocking blocks the carrier thread too:
    Carrier T1: [VT pinned][BLOCKED] -> carrier blocked
    Carrier T2: [VT unpinned] -> can yield

  Mitigation:
  - Use ReentrantLock instead of synchronized
  - Avoid long operations inside synchronized blocks
  - JVM flag: jdk.tracePinnedThreads=1 to detect
    """);
    }

    static void bestPractices() {
        System.out.println("--- Best Practices ---");
        System.out.println("""
  DO use VTs for:
  - I/O-bound workloads (HTTP calls, DB queries, file I/O)
  - Many concurrent connections (web servers)
  - Task-per-request model (each request = 1 VT)

  DON'T use VTs for:
  - CPU-bound computation (use platform threads)
  - Long-running synchronized blocks (pinning)
  - Pooling VTs (they're cheap, create fresh)

  ThreadLocal misuse: VTs are numerous, ThreadLocal is expensive
  Prefer: pass context as parameters or in scope values (JEP 429)
    """);
    }
}
