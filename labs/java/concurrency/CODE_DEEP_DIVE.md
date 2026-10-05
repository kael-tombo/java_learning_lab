# Code Deep Dive — Java Concurrency Basics (concurrency)

Annotated Java 17+ snippets for threads, locks, executors, atomics. Paste into `src/main/java`.

## Snippet 1: Thread lifecycle
What it shows: canonical use of Thread lifecycle; resource handling; observable output.
```java
// concurrency snippet 1: Thread lifecycle
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: Thread lifecycle");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Thread lifecycle; failure mode; how to observe in debugger/profiler.

## Snippet 2: synchronized & volatile
What it shows: canonical use of synchronized & volatile; resource handling; observable output.
```java
// concurrency snippet 2: synchronized & volatile
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: synchronized & volatile");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of synchronized & volatile; failure mode; how to observe in debugger/profiler.

## Snippet 3: Locks & conditions
What it shows: canonical use of Locks & conditions; resource handling; observable output.
```java
// concurrency snippet 3: Locks & conditions
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: Locks & conditions");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Locks & conditions; failure mode; how to observe in debugger/profiler.

## Snippet 4: Executors & pools
What it shows: canonical use of Executors & pools; resource handling; observable output.
```java
// concurrency snippet 4: Executors & pools
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: Executors & pools");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Executors & pools; failure mode; how to observe in debugger/profiler.

## Snippet 5: Futures & CompletableFuture
What it shows: canonical use of Futures & CompletableFuture; resource handling; observable output.
```java
// concurrency snippet 5: Futures & CompletableFuture
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: Futures & CompletableFuture");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Futures & CompletableFuture; failure mode; how to observe in debugger/profiler.

## Snippet 6: atomics
What it shows: canonical use of atomics; resource handling; observable output.
```java
// concurrency snippet 6: atomics
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: atomics");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of atomics; failure mode; how to observe in debugger/profiler.

## Pitfalls
- Thread lifecycle: silent misconfig; always assert invariants.
- synchronized & volatile: silent misconfig; always assert invariants.
- Locks & conditions: silent misconfig; always assert invariants.
- Executors & pools: silent misconfig; always assert invariants.
// note 0: trace Thread lifecycle in debugger.
// note 1: trace synchronized & volatile in debugger.
// note 2: trace Locks & conditions in debugger.
// note 3: trace Executors & pools in debugger.
// note 4: trace Futures & CompletableFuture in debugger.
// note 5: trace atomics in debugger.
// note 6: trace deadlock avoidance in debugger.
