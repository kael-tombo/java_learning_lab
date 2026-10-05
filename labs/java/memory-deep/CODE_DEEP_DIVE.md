# Code Deep Dive — JVM Memory Internals (memory-deep)

Annotated Java 17+ snippets for heap regions, metaspace, stack, GC internals, JOL, NMT. Paste into `src/main/java`.

## Snippet 1: heap vs stack
What it shows: canonical use of heap vs stack; resource handling; observable output.
```java
// memory-deep snippet 1: heap vs stack
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: heap vs stack");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of heap vs stack; failure mode; how to observe in debugger/profiler.

## Snippet 2: eden/survivor/old gen
What it shows: canonical use of eden/survivor/old gen; resource handling; observable output.
```java
// memory-deep snippet 2: eden/survivor/old gen
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: eden/survivor/old gen");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of eden/survivor/old gen; failure mode; how to observe in debugger/profiler.

## Snippet 3: metaspace vs permgen
What it shows: canonical use of metaspace vs permgen; resource handling; observable output.
```java
// memory-deep snippet 3: metaspace vs permgen
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: metaspace vs permgen");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of metaspace vs permgen; failure mode; how to observe in debugger/profiler.

## Snippet 4: object header & alignment
What it shows: canonical use of object header & alignment; resource handling; observable output.
```java
// memory-deep snippet 4: object header & alignment
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: object header & alignment");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of object header & alignment; failure mode; how to observe in debugger/profiler.

## Snippet 5: GC roots & reachability
What it shows: canonical use of GC roots & reachability; resource handling; observable output.
```java
// memory-deep snippet 5: GC roots & reachability
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: GC roots & reachability");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of GC roots & reachability; failure mode; how to observe in debugger/profiler.

## Snippet 6: NMT & JOL
What it shows: canonical use of NMT & JOL; resource handling; observable output.
```java
// memory-deep snippet 6: NMT & JOL
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: NMT & JOL");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of NMT & JOL; failure mode; how to observe in debugger/profiler.

## Pitfalls
- heap vs stack: silent misconfig; always assert invariants.
- eden/survivor/old gen: silent misconfig; always assert invariants.
- metaspace vs permgen: silent misconfig; always assert invariants.
- object header & alignment: silent misconfig; always assert invariants.
// note 0: trace heap vs stack in debugger.
// note 1: trace eden/survivor/old gen in debugger.
// note 2: trace metaspace vs permgen in debugger.
// note 3: trace object header & alignment in debugger.
// note 4: trace GC roots & reachability in debugger.
// note 5: trace NMT & JOL in debugger.
// note 6: trace reference types in debugger.
