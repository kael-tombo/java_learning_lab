# Exercises — Deep Java Testing (testing-deep)

8 hands-on drills on JUnit5, Mockito, AssertJ, Testcontainers. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore JUnit5 lifecycle & extensions
Goal: demonstrate JUnit5 lifecycle & extensions in the context of deep java testing.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of JUnit5 lifecycle & extensions. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: JUnit5 lifecycle & extensions
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("testing-deep ex1: JUnit5 lifecycle & extensions");
  }
}
```
Expected: working code + 1-paragraph write-up of JUnit5 lifecycle & extensions.

## Ex 2: Measure parameterized tests
Goal: demonstrate parameterized tests in the context of deep java testing.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of parameterized tests (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: parameterized tests
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("testing-deep ex2: parameterized tests");
  }
}
```
Expected: working code + 1-paragraph write-up of parameterized tests.

## Ex 3: Break Mockito stubbing/verification
Goal: demonstrate Mockito stubbing/verification in the context of deep java testing.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for Mockito stubbing/verification (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: Mockito stubbing/verification
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("testing-deep ex3: Mockito stubbing/verification");
  }
}
```
Expected: working code + 1-paragraph write-up of Mockito stubbing/verification.

## Ex 4: Fix + harden AssertJ fluent assertions
Goal: demonstrate AssertJ fluent assertions in the context of deep java testing.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for AssertJ fluent assertions. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: AssertJ fluent assertions
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("testing-deep ex4: AssertJ fluent assertions");
  }
}
```
Expected: working code + 1-paragraph write-up of AssertJ fluent assertions.

## Ex 5: Warm-up: explore Testcontainers
Goal: demonstrate Testcontainers in the context of deep java testing.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of Testcontainers. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: Testcontainers
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("testing-deep ex5: Testcontainers");
  }
}
```
Expected: working code + 1-paragraph write-up of Testcontainers.

## Ex 6: Measure mutation testing
Goal: demonstrate mutation testing in the context of deep java testing.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of mutation testing (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: mutation testing
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("testing-deep ex6: mutation testing");
  }
}
```
Expected: working code + 1-paragraph write-up of mutation testing.

