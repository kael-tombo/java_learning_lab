# Exercises — Java Concurrency Basics (concurrency)

8 hands-on drills on threads, locks, executors, atomics. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore Thread lifecycle
Goal: demonstrate Thread lifecycle in the context of java concurrency basics.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of Thread lifecycle. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: Thread lifecycle
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency ex1: Thread lifecycle");
  }
}
```
Expected: working code + 1-paragraph write-up of Thread lifecycle.

## Ex 2: Measure synchronized & volatile
Goal: demonstrate synchronized & volatile in the context of java concurrency basics.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of synchronized & volatile (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: synchronized & volatile
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency ex2: synchronized & volatile");
  }
}
```
Expected: working code + 1-paragraph write-up of synchronized & volatile.

## Ex 3: Break Locks & conditions
Goal: demonstrate Locks & conditions in the context of java concurrency basics.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for Locks & conditions (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: Locks & conditions
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency ex3: Locks & conditions");
  }
}
```
Expected: working code + 1-paragraph write-up of Locks & conditions.

## Ex 4: Fix + harden Executors & pools
Goal: demonstrate Executors & pools in the context of java concurrency basics.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for Executors & pools. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: Executors & pools
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency ex4: Executors & pools");
  }
}
```
Expected: working code + 1-paragraph write-up of Executors & pools.

## Ex 5: Warm-up: explore Futures & CompletableFuture
Goal: demonstrate Futures & CompletableFuture in the context of java concurrency basics.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of Futures & CompletableFuture. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: Futures & CompletableFuture
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency ex5: Futures & CompletableFuture");
  }
}
```
Expected: working code + 1-paragraph write-up of Futures & CompletableFuture.

## Ex 6: Measure atomics
Goal: demonstrate atomics in the context of java concurrency basics.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of atomics (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: atomics
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency ex6: atomics");
  }
}
```
Expected: working code + 1-paragraph write-up of atomics.

