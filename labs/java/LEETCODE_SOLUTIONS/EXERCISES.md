# Exercises — Algorithmic Patterns in Java (LEETCODE_SOLUTIONS)

8 hands-on drills on arrays/strings/DP/graphs/two-pointers/sliding-window. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore two pointers
Goal: demonstrate two pointers in the context of algorithmic patterns in java.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of two pointers. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: two pointers
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("LEETCODE_SOLUTIONS ex1: two pointers");
  }
}
```
Expected: working code + 1-paragraph write-up of two pointers.

## Ex 2: Measure sliding window
Goal: demonstrate sliding window in the context of algorithmic patterns in java.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of sliding window (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: sliding window
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("LEETCODE_SOLUTIONS ex2: sliding window");
  }
}
```
Expected: working code + 1-paragraph write-up of sliding window.

## Ex 3: Break hashing
Goal: demonstrate hashing in the context of algorithmic patterns in java.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for hashing (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: hashing
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("LEETCODE_SOLUTIONS ex3: hashing");
  }
}
```
Expected: working code + 1-paragraph write-up of hashing.

## Ex 4: Fix + harden binary search
Goal: demonstrate binary search in the context of algorithmic patterns in java.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for binary search. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: binary search
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("LEETCODE_SOLUTIONS ex4: binary search");
  }
}
```
Expected: working code + 1-paragraph write-up of binary search.

## Ex 5: Warm-up: explore DP knapsack/LIS
Goal: demonstrate DP knapsack/LIS in the context of algorithmic patterns in java.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of DP knapsack/LIS. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: DP knapsack/LIS
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("LEETCODE_SOLUTIONS ex5: DP knapsack/LIS");
  }
}
```
Expected: working code + 1-paragraph write-up of DP knapsack/LIS.

## Ex 6: Measure graphs BFS/DFS
Goal: demonstrate graphs BFS/DFS in the context of algorithmic patterns in java.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of graphs BFS/DFS (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: graphs BFS/DFS
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("LEETCODE_SOLUTIONS ex6: graphs BFS/DFS");
  }
}
```
Expected: working code + 1-paragraph write-up of graphs BFS/DFS.

