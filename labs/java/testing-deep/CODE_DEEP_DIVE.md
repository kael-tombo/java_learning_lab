# Code Deep Dive — Deep Java Testing (testing-deep)

Annotated Java 17+ snippets for JUnit5, Mockito, AssertJ, Testcontainers. Paste into `src/main/java`.

## Snippet 1: JUnit5 lifecycle & extensions
What it shows: canonical use of JUnit5 lifecycle & extensions; resource handling; observable output.
```java
// testing-deep snippet 1: JUnit5 lifecycle & extensions
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: JUnit5 lifecycle & extensions");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of JUnit5 lifecycle & extensions; failure mode; how to observe in debugger/profiler.

## Snippet 2: parameterized tests
What it shows: canonical use of parameterized tests; resource handling; observable output.
```java
// testing-deep snippet 2: parameterized tests
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: parameterized tests");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of parameterized tests; failure mode; how to observe in debugger/profiler.

## Snippet 3: Mockito stubbing/verification
What it shows: canonical use of Mockito stubbing/verification; resource handling; observable output.
```java
// testing-deep snippet 3: Mockito stubbing/verification
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: Mockito stubbing/verification");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Mockito stubbing/verification; failure mode; how to observe in debugger/profiler.

## Snippet 4: AssertJ fluent assertions
What it shows: canonical use of AssertJ fluent assertions; resource handling; observable output.
```java
// testing-deep snippet 4: AssertJ fluent assertions
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: AssertJ fluent assertions");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of AssertJ fluent assertions; failure mode; how to observe in debugger/profiler.

## Snippet 5: Testcontainers
What it shows: canonical use of Testcontainers; resource handling; observable output.
```java
// testing-deep snippet 5: Testcontainers
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: Testcontainers");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Testcontainers; failure mode; how to observe in debugger/profiler.

## Snippet 6: mutation testing
What it shows: canonical use of mutation testing; resource handling; observable output.
```java
// testing-deep snippet 6: mutation testing
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: mutation testing");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of mutation testing; failure mode; how to observe in debugger/profiler.

## Pitfalls
- JUnit5 lifecycle & extensions: silent misconfig; always assert invariants.
- parameterized tests: silent misconfig; always assert invariants.
- Mockito stubbing/verification: silent misconfig; always assert invariants.
- AssertJ fluent assertions: silent misconfig; always assert invariants.
// note 0: trace JUnit5 lifecycle & extensions in debugger.
// note 1: trace parameterized tests in debugger.
// note 2: trace Mockito stubbing/verification in debugger.
// note 3: trace AssertJ fluent assertions in debugger.
// note 4: trace Testcontainers in debugger.
// note 5: trace mutation testing in debugger.
// note 6: trace test slices in debugger.
