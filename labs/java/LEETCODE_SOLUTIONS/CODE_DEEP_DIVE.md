# Code Deep Dive — Algorithmic Patterns in Java (LEETCODE_SOLUTIONS)

Annotated Java 17+ snippets for arrays/strings/DP/graphs/two-pointers/sliding-window. Paste into `src/main/java`.

## Snippet 1: two pointers
What it shows: canonical use of two pointers; resource handling; observable output.
```java
// LEETCODE_SOLUTIONS snippet 1: two pointers
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: two pointers");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of two pointers; failure mode; how to observe in debugger/profiler.

## Snippet 2: sliding window
What it shows: canonical use of sliding window; resource handling; observable output.
```java
// LEETCODE_SOLUTIONS snippet 2: sliding window
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: sliding window");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of sliding window; failure mode; how to observe in debugger/profiler.

## Snippet 3: hashing
What it shows: canonical use of hashing; resource handling; observable output.
```java
// LEETCODE_SOLUTIONS snippet 3: hashing
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: hashing");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of hashing; failure mode; how to observe in debugger/profiler.

## Snippet 4: binary search
What it shows: canonical use of binary search; resource handling; observable output.
```java
// LEETCODE_SOLUTIONS snippet 4: binary search
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: binary search");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of binary search; failure mode; how to observe in debugger/profiler.

## Snippet 5: DP knapsack/LIS
What it shows: canonical use of DP knapsack/LIS; resource handling; observable output.
```java
// LEETCODE_SOLUTIONS snippet 5: DP knapsack/LIS
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: DP knapsack/LIS");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of DP knapsack/LIS; failure mode; how to observe in debugger/profiler.

## Snippet 6: graphs BFS/DFS
What it shows: canonical use of graphs BFS/DFS; resource handling; observable output.
```java
// LEETCODE_SOLUTIONS snippet 6: graphs BFS/DFS
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: graphs BFS/DFS");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of graphs BFS/DFS; failure mode; how to observe in debugger/profiler.

## Pitfalls
- two pointers: silent misconfig; always assert invariants.
- sliding window: silent misconfig; always assert invariants.
- hashing: silent misconfig; always assert invariants.
- binary search: silent misconfig; always assert invariants.
// note 0: trace two pointers in debugger.
// note 1: trace sliding window in debugger.
// note 2: trace hashing in debugger.
// note 3: trace binary search in debugger.
// note 4: trace DP knapsack/LIS in debugger.
// note 5: trace graphs BFS/DFS in debugger.
// note 6: trace heaps & top-K in debugger.
