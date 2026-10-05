# Exercises — Modern Java 17-25 (modern-java)

8 hands-on drills on records, sealed classes, pattern matching, virtual threads, switch expressions. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore records
Goal: demonstrate records in the context of modern java 17-25.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of records. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: records
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("modern-java ex1: records");
  }
}
```
Expected: working code + 1-paragraph write-up of records.

## Ex 2: Measure sealed classes
Goal: demonstrate sealed classes in the context of modern java 17-25.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of sealed classes (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: sealed classes
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("modern-java ex2: sealed classes");
  }
}
```
Expected: working code + 1-paragraph write-up of sealed classes.

## Ex 3: Break pattern matching instanceof/switch
Goal: demonstrate pattern matching instanceof/switch in the context of modern java 17-25.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for pattern matching instanceof/switch (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: pattern matching instanceof/switch
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("modern-java ex3: pattern matching instanceof/switch");
  }
}
```
Expected: working code + 1-paragraph write-up of pattern matching instanceof/switch.

## Ex 4: Fix + harden text blocks
Goal: demonstrate text blocks in the context of modern java 17-25.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for text blocks. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: text blocks
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("modern-java ex4: text blocks");
  }
}
```
Expected: working code + 1-paragraph write-up of text blocks.

## Ex 5: Warm-up: explore virtual threads
Goal: demonstrate virtual threads in the context of modern java 17-25.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of virtual threads. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: virtual threads
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("modern-java ex5: virtual threads");
  }
}
```
Expected: working code + 1-paragraph write-up of virtual threads.

## Ex 6: Measure structured concurrency
Goal: demonstrate structured concurrency in the context of modern java 17-25.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of structured concurrency (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: structured concurrency
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("modern-java ex6: structured concurrency");
  }
}
```
Expected: working code + 1-paragraph write-up of structured concurrency.

