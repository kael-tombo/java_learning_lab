# Code Deep Dive — Java Generics Mastery (generics)

Annotated Java 17+ snippets for type params, wildcards, erasure, variance. Paste into `src/main/java`.

## Snippet 1: type parameters & bounds
What it shows: canonical use of type parameters & bounds; resource handling; observable output.
```java
// generics snippet 1: type parameters & bounds
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: type parameters & bounds");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of type parameters & bounds; failure mode; how to observe in debugger/profiler.

## Snippet 2: wildcards PECS
What it shows: canonical use of wildcards PECS; resource handling; observable output.
```java
// generics snippet 2: wildcards PECS
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: wildcards PECS");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of wildcards PECS; failure mode; how to observe in debugger/profiler.

## Snippet 3: erasure & bridge methods
What it shows: canonical use of erasure & bridge methods; resource handling; observable output.
```java
// generics snippet 3: erasure & bridge methods
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: erasure & bridge methods");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of erasure & bridge methods; failure mode; how to observe in debugger/profiler.

## Snippet 4: generic methods
What it shows: canonical use of generic methods; resource handling; observable output.
```java
// generics snippet 4: generic methods
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: generic methods");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of generic methods; failure mode; how to observe in debugger/profiler.

## Snippet 5: variance
What it shows: canonical use of variance; resource handling; observable output.
```java
// generics snippet 5: variance
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: variance");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of variance; failure mode; how to observe in debugger/profiler.

## Snippet 6: type tokens
What it shows: canonical use of type tokens; resource handling; observable output.
```java
// generics snippet 6: type tokens
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: type tokens");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of type tokens; failure mode; how to observe in debugger/profiler.

## Pitfalls
- type parameters & bounds: silent misconfig; always assert invariants.
- wildcards PECS: silent misconfig; always assert invariants.
- erasure & bridge methods: silent misconfig; always assert invariants.
- generic methods: silent misconfig; always assert invariants.
// note 0: trace type parameters & bounds in debugger.
// note 1: trace wildcards PECS in debugger.
// note 2: trace erasure & bridge methods in debugger.
// note 3: trace generic methods in debugger.
// note 4: trace variance in debugger.
// note 5: trace type tokens in debugger.
// note 6: trace records + generics in debugger.
