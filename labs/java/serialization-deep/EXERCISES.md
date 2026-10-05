# Exercises — Deep Serialization (serialization-deep)

8 hands-on drills on Java native, Jackson, Avro, Protobuf, versioning. Run with JDK 17+; Maven for deps.

## Ex 1: Warm-up: explore Serializable & serialVersionUID
Goal: demonstrate Serializable & serialVersionUID in the context of deep serialization.
Steps:
1. Scaffold `ex1/Main.java`.
2. Create a minimal example of Serializable & serialVersionUID. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex1: Serializable & serialVersionUID
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("serialization-deep ex1: Serializable & serialVersionUID");
  }
}
```
Expected: working code + 1-paragraph write-up of Serializable & serialVersionUID.

## Ex 2: Measure Externalizable
Goal: demonstrate Externalizable in the context of deep serialization.
Steps:
1. Scaffold `ex2/Main.java`.
2. Benchmark two variants of Externalizable (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex2: Externalizable
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("serialization-deep ex2: Externalizable");
  }
}
```
Expected: working code + 1-paragraph write-up of Externalizable.

## Ex 3: Break Jackson databind
Goal: demonstrate Jackson databind in the context of deep serialization.
Steps:
1. Scaffold `ex3/Main.java`.
2. Write a failing case for Jackson databind (OOM/leak/race/wrong-output). Capture stack trace or JFR event; explain root cause.
3. Add a JUnit test asserting the outcome.
```java
// ex3: Jackson databind
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("serialization-deep ex3: Jackson databind");
  }
}
```
Expected: working code + 1-paragraph write-up of Jackson databind.

## Ex 4: Fix + harden Avro schemas
Goal: demonstrate Avro schemas in the context of deep serialization.
Steps:
1. Scaffold `ex4/Main.java`.
2. Fix the break above for Avro schemas. Add validation, timeout/backoff, or resource handling (try-with-resources/pool).
3. Add a JUnit test asserting the outcome.
```java
// ex4: Avro schemas
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("serialization-deep ex4: Avro schemas");
  }
}
```
Expected: working code + 1-paragraph write-up of Avro schemas.

## Ex 5: Warm-up: explore Protobuf
Goal: demonstrate Protobuf in the context of deep serialization.
Steps:
1. Scaffold `ex5/Main.java`.
2. Create a minimal example of Protobuf. Print key state before/after; assert one invariant with `assert`.
3. Add a JUnit test asserting the outcome.
```java
// ex5: Protobuf
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("serialization-deep ex5: Protobuf");
  }
}
```
Expected: working code + 1-paragraph write-up of Protobuf.

## Ex 6: Measure versioning & compatibility
Goal: demonstrate versioning & compatibility in the context of deep serialization.
Steps:
1. Scaffold `ex6/Main.java`.
2. Benchmark two variants of versioning & compatibility (e.g. default vs tuned). Record wall-time and one JVM metric (heap/GC/threads).
3. Add a JUnit test asserting the outcome.
```java
// ex6: versioning & compatibility
public class Main {
  public static void main(String[] a) throws Exception {
    System.out.println("serialization-deep ex6: versioning & compatibility");
  }
}
```
Expected: working code + 1-paragraph write-up of versioning & compatibility.

