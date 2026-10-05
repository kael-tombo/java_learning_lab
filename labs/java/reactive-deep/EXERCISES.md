# Exercises — Reactive Java Deep Dive (reactive-deep)

8 hands-on drills on Reactor, RxJava, Flow API, backpressure. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore Publisher/Subscriber
Goal: demonstrate Publisher/Subscriber in the context of reactive java deep dive.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of Publisher/Subscriber. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: Publisher/Subscriber
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("reactive-deep ex1: Publisher/Subscriber");
  }
}
```
Expected: working code + 1-paragraph write-up of Publisher/Subscriber.

## Ex 2: Measure Flux/Mono
Goal: demonstrate Flux/Mono in the context of reactive java deep dive.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of Flux/Mono (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: Flux/Mono
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("reactive-deep ex2: Flux/Mono");
  }
}
```
Expected: working code + 1-paragraph write-up of Flux/Mono.

## Ex 3: Break backpressure strategies
Goal: demonstrate backpressure strategies in the context of reactive java deep dive.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for backpressure strategies (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: backpressure strategies
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("reactive-deep ex3: backpressure strategies");
  }
}
```
Expected: working code + 1-paragraph write-up of backpressure strategies.

## Ex 4: Fix + harden schedulers
Goal: demonstrate schedulers in the context of reactive java deep dive.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for schedulers. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: schedulers
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("reactive-deep ex4: schedulers");
  }
}
```
Expected: working code + 1-paragraph write-up of schedulers.

## Ex 5: Warm-up: explore error handling
Goal: demonstrate error handling in the context of reactive java deep dive.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of error handling. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: error handling
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("reactive-deep ex5: error handling");
  }
}
```
Expected: working code + 1-paragraph write-up of error handling.

## Ex 6: Measure testing with StepVerifier
Goal: demonstrate testing with StepVerifier in the context of reactive java deep dive.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of testing with StepVerifier (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: testing with StepVerifier
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("reactive-deep ex6: testing with StepVerifier");
  }
}
```
Expected: working code + 1-paragraph write-up of testing with StepVerifier.

