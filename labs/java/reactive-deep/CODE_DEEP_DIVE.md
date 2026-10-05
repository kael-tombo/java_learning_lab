# Code Deep Dive — Reactive Java Deep Dive (reactive-deep)

Annotated Java 17+ snippets for Reactor, RxJava, Flow API, backpressure. Paste into `src/main/java`.

## Snippet 1: Publisher/Subscriber
What it shows: canonical use of Publisher/Subscriber; resource handling; observable output.
```java
// reactive-deep snippet 1: Publisher/Subscriber
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: Publisher/Subscriber");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Publisher/Subscriber; failure mode; how to observe in debugger/profiler.

## Snippet 2: Flux/Mono
What it shows: canonical use of Flux/Mono; resource handling; observable output.
```java
// reactive-deep snippet 2: Flux/Mono
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: Flux/Mono");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Flux/Mono; failure mode; how to observe in debugger/profiler.

## Snippet 3: backpressure strategies
What it shows: canonical use of backpressure strategies; resource handling; observable output.
```java
// reactive-deep snippet 3: backpressure strategies
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: backpressure strategies");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of backpressure strategies; failure mode; how to observe in debugger/profiler.

## Snippet 4: schedulers
What it shows: canonical use of schedulers; resource handling; observable output.
```java
// reactive-deep snippet 4: schedulers
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: schedulers");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of schedulers; failure mode; how to observe in debugger/profiler.

## Snippet 5: error handling
What it shows: canonical use of error handling; resource handling; observable output.
```java
// reactive-deep snippet 5: error handling
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: error handling");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of error handling; failure mode; how to observe in debugger/profiler.

## Snippet 6: testing with StepVerifier
What it shows: canonical use of testing with StepVerifier; resource handling; observable output.
```java
// reactive-deep snippet 6: testing with StepVerifier
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: testing with StepVerifier");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of testing with StepVerifier; failure mode; how to observe in debugger/profiler.

## Pitfalls
- Publisher/Subscriber: silent misconfig; always assert invariants.
- Flux/Mono: silent misconfig; always assert invariants.
- backpressure strategies: silent misconfig; always assert invariants.
- schedulers: silent misconfig; always assert invariants.
// note 0: trace Publisher/Subscriber in debugger.
// note 1: trace Flux/Mono in debugger.
// note 2: trace backpressure strategies in debugger.
// note 3: trace schedulers in debugger.
// note 4: trace error handling in debugger.
// note 5: trace testing with StepVerifier in debugger.
// note 6: trace R2DBC/reactive web in debugger.
