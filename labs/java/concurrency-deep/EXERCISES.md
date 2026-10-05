# Exercises — Concurrency Deep & Virtual Threads (concurrency-deep)

8 hands-on drills on JMM, Loom, structured concurrency, VarHandles. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore JMM happens-before
Goal: demonstrate JMM happens-before in the context of concurrency deep & virtual threads.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of JMM happens-before. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: JMM happens-before
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency-deep ex1: JMM happens-before");
  }
}
```
Expected: working code + 1-paragraph write-up of JMM happens-before.

## Ex 2: Measure virtual threads & carriers
Goal: demonstrate virtual threads & carriers in the context of concurrency deep & virtual threads.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of virtual threads & carriers (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: virtual threads & carriers
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency-deep ex2: virtual threads & carriers");
  }
}
```
Expected: working code + 1-paragraph write-up of virtual threads & carriers.

## Ex 3: Break structured concurrency
Goal: demonstrate structured concurrency in the context of concurrency deep & virtual threads.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for structured concurrency (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: structured concurrency
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency-deep ex3: structured concurrency");
  }
}
```
Expected: working code + 1-paragraph write-up of structured concurrency.

## Ex 4: Fix + harden scoped values
Goal: demonstrate scoped values in the context of concurrency deep & virtual threads.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for scoped values. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: scoped values
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency-deep ex4: scoped values");
  }
}
```
Expected: working code + 1-paragraph write-up of scoped values.

## Ex 5: Warm-up: explore ForkJoinPool
Goal: demonstrate ForkJoinPool in the context of concurrency deep & virtual threads.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of ForkJoinPool. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: ForkJoinPool
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency-deep ex5: ForkJoinPool");
  }
}
```
Expected: working code + 1-paragraph write-up of ForkJoinPool.

## Ex 6: Measure StampedLock/LongAdder
Goal: demonstrate StampedLock/LongAdder in the context of concurrency deep & virtual threads.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of StampedLock/LongAdder (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: StampedLock/LongAdder
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("concurrency-deep ex6: StampedLock/LongAdder");
  }
}
```
Expected: working code + 1-paragraph write-up of StampedLock/LongAdder.

