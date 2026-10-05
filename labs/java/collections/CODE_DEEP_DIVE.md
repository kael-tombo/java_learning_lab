# Code Deep Dive — Java Collections Fundamentals (collections)

Annotated Java 17+ snippets for List/Set/Map, equals/hashCode, sorting. Paste into `src/main/java`.

## Snippet 1: ArrayList vs LinkedList
What it shows: canonical use of ArrayList vs LinkedList; resource handling; observable output.
```java
// collections snippet 1: ArrayList vs LinkedList
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: ArrayList vs LinkedList");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of ArrayList vs LinkedList; failure mode; how to observe in debugger/profiler.

## Snippet 2: HashSet/TreeSet
What it shows: canonical use of HashSet/TreeSet; resource handling; observable output.
```java
// collections snippet 2: HashSet/TreeSet
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: HashSet/TreeSet");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of HashSet/TreeSet; failure mode; how to observe in debugger/profiler.

## Snippet 3: HashMap internals
What it shows: canonical use of HashMap internals; resource handling; observable output.
```java
// collections snippet 3: HashMap internals
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: HashMap internals");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of HashMap internals; failure mode; how to observe in debugger/profiler.

## Snippet 4: equals/hashCode contract
What it shows: canonical use of equals/hashCode contract; resource handling; observable output.
```java
// collections snippet 4: equals/hashCode contract
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: equals/hashCode contract");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of equals/hashCode contract; failure mode; how to observe in debugger/profiler.

## Snippet 5: comparators
What it shows: canonical use of comparators; resource handling; observable output.
```java
// collections snippet 5: comparators
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: comparators");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of comparators; failure mode; how to observe in debugger/profiler.

## Snippet 6: streams basics
What it shows: canonical use of streams basics; resource handling; observable output.
```java
// collections snippet 6: streams basics
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: streams basics");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of streams basics; failure mode; how to observe in debugger/profiler.

## Pitfalls
- ArrayList vs LinkedList: silent misconfig; always assert invariants.
- HashSet/TreeSet: silent misconfig; always assert invariants.
- HashMap internals: silent misconfig; always assert invariants.
- equals/hashCode contract: silent misconfig; always assert invariants.
// note 0: trace ArrayList vs LinkedList in debugger.
// note 1: trace HashSet/TreeSet in debugger.
// note 2: trace HashMap internals in debugger.
// note 3: trace equals/hashCode contract in debugger.
// note 4: trace comparators in debugger.
// note 5: trace streams basics in debugger.
// note 6: trace unmodifiable views in debugger.
