# Code Deep Dive — Modern Java 17-25 (modern-java)

Annotated Java 17+ snippets for records, sealed classes, pattern matching, virtual threads, switch expressions. Paste into `src/main/java`.

## Snippet 1: records
What it shows: canonical use of records; resource handling; observable output.
```java
// modern-java snippet 1: records
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: records");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of records; failure mode; how to observe in debugger/profiler.

## Snippet 2: sealed classes
What it shows: canonical use of sealed classes; resource handling; observable output.
```java
// modern-java snippet 2: sealed classes
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: sealed classes");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of sealed classes; failure mode; how to observe in debugger/profiler.

## Snippet 3: pattern matching instanceof/switch
What it shows: canonical use of pattern matching instanceof/switch; resource handling; observable output.
```java
// modern-java snippet 3: pattern matching instanceof/switch
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: pattern matching instanceof/switch");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of pattern matching instanceof/switch; failure mode; how to observe in debugger/profiler.

## Snippet 4: text blocks
What it shows: canonical use of text blocks; resource handling; observable output.
```java
// modern-java snippet 4: text blocks
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: text blocks");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of text blocks; failure mode; how to observe in debugger/profiler.

## Snippet 5: virtual threads
What it shows: canonical use of virtual threads; resource handling; observable output.
```java
// modern-java snippet 5: virtual threads
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: virtual threads");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of virtual threads; failure mode; how to observe in debugger/profiler.

## Snippet 6: structured concurrency
What it shows: canonical use of structured concurrency; resource handling; observable output.
```java
// modern-java snippet 6: structured concurrency
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: structured concurrency");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of structured concurrency; failure mode; how to observe in debugger/profiler.

## Pitfalls
- records: silent misconfig; always assert invariants.
- sealed classes: silent misconfig; always assert invariants.
- pattern matching instanceof/switch: silent misconfig; always assert invariants.
- text blocks: silent misconfig; always assert invariants.
// note 0: trace records in debugger.
// note 1: trace sealed classes in debugger.
// note 2: trace pattern matching instanceof/switch in debugger.
// note 3: trace text blocks in debugger.
// note 4: trace virtual threads in debugger.
// note 5: trace structured concurrency in debugger.
// note 6: trace new HTTP client in debugger.
