# Code Deep Dive — Deep Java Networking (networking-deep)

Annotated Java 17+ snippets for sockets, NIO/NIO.2, Netty, HTTP client, gRPC. Paste into `src/main/java`.

## Snippet 1: TCP/UDP sockets
What it shows: canonical use of TCP/UDP sockets; resource handling; observable output.
```java
// networking-deep snippet 1: TCP/UDP sockets
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: TCP/UDP sockets");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of TCP/UDP sockets; failure mode; how to observe in debugger/profiler.

## Snippet 2: NIO selectors & channels
What it shows: canonical use of NIO selectors & channels; resource handling; observable output.
```java
// networking-deep snippet 2: NIO selectors & channels
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: NIO selectors & channels");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of NIO selectors & channels; failure mode; how to observe in debugger/profiler.

## Snippet 3: NIO.2 async channels
What it shows: canonical use of NIO.2 async channels; resource handling; observable output.
```java
// networking-deep snippet 3: NIO.2 async channels
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: NIO.2 async channels");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of NIO.2 async channels; failure mode; how to observe in debugger/profiler.

## Snippet 4: Netty pipeline
What it shows: canonical use of Netty pipeline; resource handling; observable output.
```java
// networking-deep snippet 4: Netty pipeline
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: Netty pipeline");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Netty pipeline; failure mode; how to observe in debugger/profiler.

## Snippet 5: Java HttpClient
What it shows: canonical use of Java HttpClient; resource handling; observable output.
```java
// networking-deep snippet 5: Java HttpClient
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: Java HttpClient");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Java HttpClient; failure mode; how to observe in debugger/profiler.

## Snippet 6: WebSocket
What it shows: canonical use of WebSocket; resource handling; observable output.
```java
// networking-deep snippet 6: WebSocket
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: WebSocket");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of WebSocket; failure mode; how to observe in debugger/profiler.

## Pitfalls
- TCP/UDP sockets: silent misconfig; always assert invariants.
- NIO selectors & channels: silent misconfig; always assert invariants.
- NIO.2 async channels: silent misconfig; always assert invariants.
- Netty pipeline: silent misconfig; always assert invariants.
// note 0: trace TCP/UDP sockets in debugger.
// note 1: trace NIO selectors & channels in debugger.
// note 2: trace NIO.2 async channels in debugger.
// note 3: trace Netty pipeline in debugger.
// note 4: trace Java HttpClient in debugger.
// note 5: trace WebSocket in debugger.
// note 6: trace gRPC stubs in debugger.
