# Code Deep Dive — Java Performance Engineering (performance-deep)

Annotated Java 17+ snippets for JMH, JIT, profiling, GC latency. Paste into `src/main/java`.

## Snippet 1: JMH benchmarks
What it shows: canonical use of JMH benchmarks; resource handling; observable output.
```java
// performance-deep snippet 1: JMH benchmarks
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: JMH benchmarks");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of JMH benchmarks; failure mode; how to observe in debugger/profiler.

## Snippet 2: JIT C1/C2 & inlining
What it shows: canonical use of JIT C1/C2 & inlining; resource handling; observable output.
```java
// performance-deep snippet 2: JIT C1/C2 & inlining
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: JIT C1/C2 & inlining");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of JIT C1/C2 & inlining; failure mode; how to observe in debugger/profiler.

## Snippet 3: escape analysis
What it shows: canonical use of escape analysis; resource handling; observable output.
```java
// performance-deep snippet 3: escape analysis
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: escape analysis");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of escape analysis; failure mode; how to observe in debugger/profiler.

## Snippet 4: allocation profiling
What it shows: canonical use of allocation profiling; resource handling; observable output.
```java
// performance-deep snippet 4: allocation profiling
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: allocation profiling");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of allocation profiling; failure mode; how to observe in debugger/profiler.

## Snippet 5: async-profiler/JFR
What it shows: canonical use of async-profiler/JFR; resource handling; observable output.
```java
// performance-deep snippet 5: async-profiler/JFR
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: async-profiler/JFR");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of async-profiler/JFR; failure mode; how to observe in debugger/profiler.

## Snippet 6: GC pause tuning
What it shows: canonical use of GC pause tuning; resource handling; observable output.
```java
// performance-deep snippet 6: GC pause tuning
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: GC pause tuning");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of GC pause tuning; failure mode; how to observe in debugger/profiler.

## Pitfalls
- JMH benchmarks: silent misconfig; always assert invariants.
- JIT C1/C2 & inlining: silent misconfig; always assert invariants.
- escape analysis: silent misconfig; always assert invariants.
- allocation profiling: silent misconfig; always assert invariants.
// note 0: trace JMH benchmarks in debugger.
// note 1: trace JIT C1/C2 & inlining in debugger.
// note 2: trace escape analysis in debugger.
// note 3: trace allocation profiling in debugger.
// note 4: trace async-profiler/JFR in debugger.
// note 5: trace GC pause tuning in debugger.
// note 6: trace lock contention in debugger.
