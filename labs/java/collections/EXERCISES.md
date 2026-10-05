# Exercises — Java Collections Fundamentals (collections)

8 hands-on drills on List/Set/Map, equals/hashCode, sorting. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore ArrayList vs LinkedList
Goal: demonstrate ArrayList vs LinkedList in the context of java collections fundamentals.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of ArrayList vs LinkedList. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: ArrayList vs LinkedList
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections ex1: ArrayList vs LinkedList");
  }
}
```
Expected: working code + 1-paragraph write-up of ArrayList vs LinkedList.

## Ex 2: Measure HashSet/TreeSet
Goal: demonstrate HashSet/TreeSet in the context of java collections fundamentals.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of HashSet/TreeSet (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: HashSet/TreeSet
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections ex2: HashSet/TreeSet");
  }
}
```
Expected: working code + 1-paragraph write-up of HashSet/TreeSet.

## Ex 3: Break HashMap internals
Goal: demonstrate HashMap internals in the context of java collections fundamentals.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for HashMap internals (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: HashMap internals
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections ex3: HashMap internals");
  }
}
```
Expected: working code + 1-paragraph write-up of HashMap internals.

## Ex 4: Fix + harden equals/hashCode contract
Goal: demonstrate equals/hashCode contract in the context of java collections fundamentals.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for equals/hashCode contract. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: equals/hashCode contract
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections ex4: equals/hashCode contract");
  }
}
```
Expected: working code + 1-paragraph write-up of equals/hashCode contract.

## Ex 5: Warm-up: explore comparators
Goal: demonstrate comparators in the context of java collections fundamentals.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of comparators. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: comparators
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections ex5: comparators");
  }
}
```
Expected: working code + 1-paragraph write-up of comparators.

## Ex 6: Measure streams basics
Goal: demonstrate streams basics in the context of java collections fundamentals.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of streams basics (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: streams basics
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("collections ex6: streams basics");
  }
}
```
Expected: working code + 1-paragraph write-up of streams basics.

