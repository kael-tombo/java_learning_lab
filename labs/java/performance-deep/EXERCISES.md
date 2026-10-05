# Exercises — Java Performance Engineering (performance-deep)

8 hands-on drills on JMH, JIT, profiling, GC latency. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore JMH benchmarks
Goal: demonstrate JMH benchmarks in the context of java performance engineering.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of JMH benchmarks. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: JMH benchmarks
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("performance-deep ex1: JMH benchmarks");
  }
}
```
Expected: working code + 1-paragraph write-up of JMH benchmarks.

## Ex 2: Measure JIT C1/C2 & inlining
Goal: demonstrate JIT C1/C2 & inlining in the context of java performance engineering.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of JIT C1/C2 & inlining (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: JIT C1/C2 & inlining
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("performance-deep ex2: JIT C1/C2 & inlining");
  }
}
```
Expected: working code + 1-paragraph write-up of JIT C1/C2 & inlining.

## Ex 3: Break escape analysis
Goal: demonstrate escape analysis in the context of java performance engineering.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for escape analysis (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: escape analysis
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("performance-deep ex3: escape analysis");
  }
}
```
Expected: working code + 1-paragraph write-up of escape analysis.

## Ex 4: Fix + harden allocation profiling
Goal: demonstrate allocation profiling in the context of java performance engineering.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for allocation profiling. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: allocation profiling
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("performance-deep ex4: allocation profiling");
  }
}
```
Expected: working code + 1-paragraph write-up of allocation profiling.

## Ex 5: Warm-up: explore async-profiler/JFR
Goal: demonstrate async-profiler/JFR in the context of java performance engineering.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of async-profiler/JFR. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: async-profiler/JFR
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("performance-deep ex5: async-profiler/JFR");
  }
}
```
Expected: working code + 1-paragraph write-up of async-profiler/JFR.

## Ex 6: Measure GC pause tuning
Goal: demonstrate GC pause tuning in the context of java performance engineering.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of GC pause tuning (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: GC pause tuning
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("performance-deep ex6: GC pause tuning");
  }
}
```
Expected: working code + 1-paragraph write-up of GC pause tuning.

