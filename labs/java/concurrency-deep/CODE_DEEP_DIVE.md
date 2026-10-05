# Code Deep Dive — Concurrency Deep & Virtual Threads (concurrency-deep)

Annotated Java 17+ snippets for JMM, Loom, structured concurrency, VarHandles. Paste into `src/main/java`.

## Snippet 1: JMM happens-before
What it shows: canonical use of JMM happens-before; resource handling; observable output.
```java
// concurrency-deep snippet 1: JMM happens-before
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: JMM happens-before");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of JMM happens-before; failure mode; how to observe in debugger/profiler.

## Snippet 2: virtual threads & carriers
What it shows: canonical use of virtual threads & carriers; resource handling; observable output.
```java
// concurrency-deep snippet 2: virtual threads & carriers
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: virtual threads & carriers");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of virtual threads & carriers; failure mode; how to observe in debugger/profiler.

## Snippet 3: structured concurrency
What it shows: canonical use of structured concurrency; resource handling; observable output.
```java
// concurrency-deep snippet 3: structured concurrency
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: structured concurrency");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of structured concurrency; failure mode; how to observe in debugger/profiler.

## Snippet 4: scoped values
What it shows: canonical use of scoped values; resource handling; observable output.
```java
// concurrency-deep snippet 4: scoped values
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: scoped values");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of scoped values; failure mode; how to observe in debugger/profiler.

## Snippet 5: ForkJoinPool
What it shows: canonical use of ForkJoinPool; resource handling; observable output.
```java
// concurrency-deep snippet 5: ForkJoinPool
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: ForkJoinPool");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of ForkJoinPool; failure mode; how to observe in debugger/profiler.

## Snippet 6: StampedLock/LongAdder
What it shows: canonical use of StampedLock/LongAdder; resource handling; observable output.
```java
// concurrency-deep snippet 6: StampedLock/LongAdder
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: StampedLock/LongAdder");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of StampedLock/LongAdder; failure mode; how to observe in debugger/profiler.

## Pitfalls
- JMM happens-before: silent misconfig; always assert invariants.
- virtual threads & carriers: silent misconfig; always assert invariants.
- structured concurrency: silent misconfig; always assert invariants.
- scoped values: silent misconfig; always assert invariants.
// note 0: trace JMM happens-before in debugger.
// note 1: trace virtual threads & carriers in debugger.
// note 2: trace structured concurrency in debugger.
// note 3: trace scoped values in debugger.
// note 4: trace ForkJoinPool in debugger.
// note 5: trace StampedLock/LongAdder in debugger.
// note 6: trace VarHandle in debugger.
