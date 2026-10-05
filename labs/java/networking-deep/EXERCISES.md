# Exercises — Deep Java Networking (networking-deep)

8 hands-on drills on sockets, NIO/NIO.2, Netty, HTTP client, gRPC. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore TCP/UDP sockets
Goal: demonstrate TCP/UDP sockets in the context of deep java networking.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of TCP/UDP sockets. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: TCP/UDP sockets
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("networking-deep ex1: TCP/UDP sockets");
  }
}
```
Expected: working code + 1-paragraph write-up of TCP/UDP sockets.

## Ex 2: Measure NIO selectors & channels
Goal: demonstrate NIO selectors & channels in the context of deep java networking.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of NIO selectors & channels (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: NIO selectors & channels
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("networking-deep ex2: NIO selectors & channels");
  }
}
```
Expected: working code + 1-paragraph write-up of NIO selectors & channels.

## Ex 3: Break NIO.2 async channels
Goal: demonstrate NIO.2 async channels in the context of deep java networking.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for NIO.2 async channels (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: NIO.2 async channels
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("networking-deep ex3: NIO.2 async channels");
  }
}
```
Expected: working code + 1-paragraph write-up of NIO.2 async channels.

## Ex 4: Fix + harden Netty pipeline
Goal: demonstrate Netty pipeline in the context of deep java networking.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for Netty pipeline. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: Netty pipeline
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("networking-deep ex4: Netty pipeline");
  }
}
```
Expected: working code + 1-paragraph write-up of Netty pipeline.

## Ex 5: Warm-up: explore Java HttpClient
Goal: demonstrate Java HttpClient in the context of deep java networking.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of Java HttpClient. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: Java HttpClient
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("networking-deep ex5: Java HttpClient");
  }
}
```
Expected: working code + 1-paragraph write-up of Java HttpClient.

## Ex 6: Measure WebSocket
Goal: demonstrate WebSocket in the context of deep java networking.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of WebSocket (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: WebSocket
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("networking-deep ex6: WebSocket");
  }
}
```
Expected: working code + 1-paragraph write-up of WebSocket.

