# Exercises — Java Memory Management (memory-management)

8 hands-on drills on allocation, GC tuning, leak detection, heap dumps. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore allocation paths (TLAB)
Goal: demonstrate allocation paths (TLAB) in the context of java memory management.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of allocation paths (TLAB). Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: allocation paths (TLAB)
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-management ex1: allocation paths (TLAB)");
  }
}
```
Expected: working code + 1-paragraph write-up of allocation paths (TLAB).

## Ex 2: Measure young/old GC
Goal: demonstrate young/old GC in the context of java memory management.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of young/old GC (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: young/old GC
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-management ex2: young/old GC");
  }
}
```
Expected: working code + 1-paragraph write-up of young/old GC.

## Ex 3: Break G1/ZGC/Shenandoah
Goal: demonstrate G1/ZGC/Shenandoah in the context of java memory management.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for G1/ZGC/Shenandoah (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: G1/ZGC/Shenandoah
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-management ex3: G1/ZGC/Shenandoah");
  }
}
```
Expected: working code + 1-paragraph write-up of G1/ZGC/Shenandoah.

## Ex 4: Fix + harden tuning flags
Goal: demonstrate tuning flags in the context of java memory management.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for tuning flags. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: tuning flags
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-management ex4: tuning flags");
  }
}
```
Expected: working code + 1-paragraph write-up of tuning flags.

## Ex 5: Warm-up: explore leak detection
Goal: demonstrate leak detection in the context of java memory management.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of leak detection. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: leak detection
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-management ex5: leak detection");
  }
}
```
Expected: working code + 1-paragraph write-up of leak detection.

## Ex 6: Measure heap dump analysis
Goal: demonstrate heap dump analysis in the context of java memory management.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of heap dump analysis (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: heap dump analysis
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-management ex6: heap dump analysis");
  }
}
```
Expected: working code + 1-paragraph write-up of heap dump analysis.

