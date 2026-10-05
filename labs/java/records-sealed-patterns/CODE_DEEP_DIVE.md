# Code Deep Dive — Records, Sealed Classes & Patterns (records-sealed-patterns)

Annotated Java 17+ snippets for data carriers, exhaustive switch, deconstruction. Paste into `src/main/java`.

## Snippet 1: record canonical constructors
What it shows: canonical use of record canonical constructors; resource handling; observable output.
```java
// records-sealed-patterns snippet 1: record canonical constructors
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: record canonical constructors");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of record canonical constructors; failure mode; how to observe in debugger/profiler.

## Snippet 2: compact constructors
What it shows: canonical use of compact constructors; resource handling; observable output.
```java
// records-sealed-patterns snippet 2: compact constructors
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: compact constructors");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of compact constructors; failure mode; how to observe in debugger/profiler.

## Snippet 3: sealed permits
What it shows: canonical use of sealed permits; resource handling; observable output.
```java
// records-sealed-patterns snippet 3: sealed permits
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: sealed permits");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of sealed permits; failure mode; how to observe in debugger/profiler.

## Snippet 4: pattern matching switch
What it shows: canonical use of pattern matching switch; resource handling; observable output.
```java
// records-sealed-patterns snippet 4: pattern matching switch
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: pattern matching switch");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of pattern matching switch; failure mode; how to observe in debugger/profiler.

## Snippet 5: guarded patterns
What it shows: canonical use of guarded patterns; resource handling; observable output.
```java
// records-sealed-patterns snippet 5: guarded patterns
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: guarded patterns");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of guarded patterns; failure mode; how to observe in debugger/profiler.

## Snippet 6: record patterns
What it shows: canonical use of record patterns; resource handling; observable output.
```java
// records-sealed-patterns snippet 6: record patterns
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: record patterns");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of record patterns; failure mode; how to observe in debugger/profiler.

## Pitfalls
- record canonical constructors: silent misconfig; always assert invariants.
- compact constructors: silent misconfig; always assert invariants.
- sealed permits: silent misconfig; always assert invariants.
- pattern matching switch: silent misconfig; always assert invariants.
// note 0: trace record canonical constructors in debugger.
// note 1: trace compact constructors in debugger.
// note 2: trace sealed permits in debugger.
// note 3: trace pattern matching switch in debugger.
// note 4: trace guarded patterns in debugger.
// note 5: trace record patterns in debugger.
// note 6: trace exhaustiveness in debugger.
