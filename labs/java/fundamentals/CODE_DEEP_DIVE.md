# Code Deep Dive — Java Fundamentals (fundamentals)

Annotated Java 17+ snippets for syntax, OOP, JVM, classpath. Paste into `src/main/java`.

## Snippet 1: types & operators
What it shows: canonical use of types & operators; resource handling; observable output.
```java
// fundamentals snippet 1: types & operators
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: types & operators");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of types & operators; failure mode; how to observe in debugger/profiler.

## Snippet 2: control flow
What it shows: canonical use of control flow; resource handling; observable output.
```java
// fundamentals snippet 2: control flow
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: control flow");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of control flow; failure mode; how to observe in debugger/profiler.

## Snippet 3: OOP pillars
What it shows: canonical use of OOP pillars; resource handling; observable output.
```java
// fundamentals snippet 3: OOP pillars
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: OOP pillars");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of OOP pillars; failure mode; how to observe in debugger/profiler.

## Snippet 4: exceptions
What it shows: canonical use of exceptions; resource handling; observable output.
```java
// fundamentals snippet 4: exceptions
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: exceptions");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of exceptions; failure mode; how to observe in debugger/profiler.

## Snippet 5: generics intro
What it shows: canonical use of generics intro; resource handling; observable output.
```java
// fundamentals snippet 5: generics intro
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: generics intro");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of generics intro; failure mode; how to observe in debugger/profiler.

## Snippet 6: JVM & bytecode
What it shows: canonical use of JVM & bytecode; resource handling; observable output.
```java
// fundamentals snippet 6: JVM & bytecode
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: JVM & bytecode");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of JVM & bytecode; failure mode; how to observe in debugger/profiler.

## Pitfalls
- types & operators: silent misconfig; always assert invariants.
- control flow: silent misconfig; always assert invariants.
- OOP pillars: silent misconfig; always assert invariants.
- exceptions: silent misconfig; always assert invariants.
// note 0: trace types & operators in debugger.
// note 1: trace control flow in debugger.
// note 2: trace OOP pillars in debugger.
// note 3: trace exceptions in debugger.
// note 4: trace generics intro in debugger.
// note 5: trace JVM & bytecode in debugger.
// note 6: trace Maven/Gradle in debugger.
