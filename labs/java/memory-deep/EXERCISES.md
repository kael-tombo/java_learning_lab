# Exercises — JVM Memory Internals (memory-deep)

8 hands-on drills on heap regions, metaspace, stack, GC internals, JOL, NMT. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore heap vs stack
Goal: demonstrate heap vs stack in the context of jvm memory internals.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of heap vs stack. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: heap vs stack
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-deep ex1: heap vs stack");
  }
}
```
Expected: working code + 1-paragraph write-up of heap vs stack.

## Ex 2: Measure eden/survivor/old gen
Goal: demonstrate eden/survivor/old gen in the context of jvm memory internals.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of eden/survivor/old gen (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: eden/survivor/old gen
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-deep ex2: eden/survivor/old gen");
  }
}
```
Expected: working code + 1-paragraph write-up of eden/survivor/old gen.

## Ex 3: Break metaspace vs permgen
Goal: demonstrate metaspace vs permgen in the context of jvm memory internals.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for metaspace vs permgen (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: metaspace vs permgen
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-deep ex3: metaspace vs permgen");
  }
}
```
Expected: working code + 1-paragraph write-up of metaspace vs permgen.

## Ex 4: Fix + harden object header & alignment
Goal: demonstrate object header & alignment in the context of jvm memory internals.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for object header & alignment. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: object header & alignment
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-deep ex4: object header & alignment");
  }
}
```
Expected: working code + 1-paragraph write-up of object header & alignment.

## Ex 5: Warm-up: explore GC roots & reachability
Goal: demonstrate GC roots & reachability in the context of jvm memory internals.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of GC roots & reachability. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: GC roots & reachability
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-deep ex5: GC roots & reachability");
  }
}
```
Expected: working code + 1-paragraph write-up of GC roots & reachability.

## Ex 6: Measure NMT & JOL
Goal: demonstrate NMT & JOL in the context of jvm memory internals.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of NMT & JOL (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: NMT & JOL
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("memory-deep ex6: NMT & JOL");
  }
}
```
Expected: working code + 1-paragraph write-up of NMT & JOL.

