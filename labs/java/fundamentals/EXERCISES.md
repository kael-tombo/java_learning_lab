# Exercises — Java Fundamentals (fundamentals)

8 hands-on drills on syntax, OOP, JVM, classpath. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore types & operators
Goal: demonstrate types & operators in the context of java fundamentals.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of types & operators. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: types & operators
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("fundamentals ex1: types & operators");
  }
}
```
Expected: working code + 1-paragraph write-up of types & operators.

## Ex 2: Measure control flow
Goal: demonstrate control flow in the context of java fundamentals.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of control flow (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: control flow
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("fundamentals ex2: control flow");
  }
}
```
Expected: working code + 1-paragraph write-up of control flow.

## Ex 3: Break OOP pillars
Goal: demonstrate OOP pillars in the context of java fundamentals.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for OOP pillars (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: OOP pillars
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("fundamentals ex3: OOP pillars");
  }
}
```
Expected: working code + 1-paragraph write-up of OOP pillars.

## Ex 4: Fix + harden exceptions
Goal: demonstrate exceptions in the context of java fundamentals.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for exceptions. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: exceptions
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("fundamentals ex4: exceptions");
  }
}
```
Expected: working code + 1-paragraph write-up of exceptions.

## Ex 5: Warm-up: explore generics intro
Goal: demonstrate generics intro in the context of java fundamentals.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of generics intro. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: generics intro
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("fundamentals ex5: generics intro");
  }
}
```
Expected: working code + 1-paragraph write-up of generics intro.

## Ex 6: Measure JVM & bytecode
Goal: demonstrate JVM & bytecode in the context of java fundamentals.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of JVM & bytecode (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: JVM & bytecode
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("fundamentals ex6: JVM & bytecode");
  }
}
```
Expected: working code + 1-paragraph write-up of JVM & bytecode.

