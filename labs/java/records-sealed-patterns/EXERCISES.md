# Exercises — Records, Sealed Classes & Patterns (records-sealed-patterns)

8 hands-on drills on data carriers, exhaustive switch, deconstruction. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore record canonical constructors
Goal: demonstrate record canonical constructors in the context of records, sealed classes & patterns.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of record canonical constructors. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: record canonical constructors
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("records-sealed-patterns ex1: record canonical constructors");
  }
}
```
Expected: working code + 1-paragraph write-up of record canonical constructors.

## Ex 2: Measure compact constructors
Goal: demonstrate compact constructors in the context of records, sealed classes & patterns.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of compact constructors (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: compact constructors
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("records-sealed-patterns ex2: compact constructors");
  }
}
```
Expected: working code + 1-paragraph write-up of compact constructors.

## Ex 3: Break sealed permits
Goal: demonstrate sealed permits in the context of records, sealed classes & patterns.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for sealed permits (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: sealed permits
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("records-sealed-patterns ex3: sealed permits");
  }
}
```
Expected: working code + 1-paragraph write-up of sealed permits.

## Ex 4: Fix + harden pattern matching switch
Goal: demonstrate pattern matching switch in the context of records, sealed classes & patterns.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for pattern matching switch. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: pattern matching switch
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("records-sealed-patterns ex4: pattern matching switch");
  }
}
```
Expected: working code + 1-paragraph write-up of pattern matching switch.

## Ex 5: Warm-up: explore guarded patterns
Goal: demonstrate guarded patterns in the context of records, sealed classes & patterns.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of guarded patterns. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: guarded patterns
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("records-sealed-patterns ex5: guarded patterns");
  }
}
```
Expected: working code + 1-paragraph write-up of guarded patterns.

## Ex 6: Measure record patterns
Goal: demonstrate record patterns in the context of records, sealed classes & patterns.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of record patterns (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: record patterns
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("records-sealed-patterns ex6: record patterns");
  }
}
```
Expected: working code + 1-paragraph write-up of record patterns.

