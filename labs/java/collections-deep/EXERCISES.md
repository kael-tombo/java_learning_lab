# Exercises — Deep Collections Engineering (collections-deep)

8 hands-on drills on hashing, trees, concurrent maps, custom structures. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore hash spreading & bins
Goal: demonstrate hash spreading & bins in the context of deep collections engineering.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of hash spreading & bins. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: hash spreading & bins
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections-deep ex1: hash spreading & bins");
  }
}
```
Expected: working code + 1-paragraph write-up of hash spreading & bins.

## Ex 2: Measure red-black trees
Goal: demonstrate red-black trees in the context of deep collections engineering.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of red-black trees (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: red-black trees
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections-deep ex2: red-black trees");
  }
}
```
Expected: working code + 1-paragraph write-up of red-black trees.

## Ex 3: Break ConcurrentHashMap
Goal: demonstrate ConcurrentHashMap in the context of deep collections engineering.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for ConcurrentHashMap (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: ConcurrentHashMap
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections-deep ex3: ConcurrentHashMap");
  }
}
```
Expected: working code + 1-paragraph write-up of ConcurrentHashMap.

## Ex 4: Fix + harden CopyOnWriteArrayList
Goal: demonstrate CopyOnWriteArrayList in the context of deep collections engineering.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for CopyOnWriteArrayList. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: CopyOnWriteArrayList
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections-deep ex4: CopyOnWriteArrayList");
  }
}
```
Expected: working code + 1-paragraph write-up of CopyOnWriteArrayList.

## Ex 5: Warm-up: explore immutable collections
Goal: demonstrate immutable collections in the context of deep collections engineering.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of immutable collections. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: immutable collections
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections-deep ex5: immutable collections");
  }
}
```
Expected: working code + 1-paragraph write-up of immutable collections.

## Ex 6: Measure Deque & queues
Goal: demonstrate Deque & queues in the context of deep collections engineering.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of Deque & queues (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: Deque & queues
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections-deep ex6: Deque & queues");
  }
}
```
Expected: working code + 1-paragraph write-up of Deque & queues.

