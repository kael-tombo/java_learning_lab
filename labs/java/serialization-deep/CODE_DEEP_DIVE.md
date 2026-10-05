# Code Deep Dive — Deep Serialization (serialization-deep)

Annotated Java 17+ snippets for Java native, Jackson, Avro, Protobuf, versioning. Paste into `src/main/java`.

## Snippet 1: Serializable & serialVersionUID
What it shows: canonical use of Serializable & serialVersionUID; resource handling; observable output.
```java
// serialization-deep snippet 1: Serializable & serialVersionUID
import java.util.*;
public class Snippet1 {
  public static void demo() throws Exception {
    System.out.println("demo: Serializable & serialVersionUID");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Serializable & serialVersionUID; failure mode; how to observe in debugger/profiler.

## Snippet 2: Externalizable
What it shows: canonical use of Externalizable; resource handling; observable output.
```java
// serialization-deep snippet 2: Externalizable
import java.util.*;
public class Snippet2 {
  public static void demo() throws Exception {
    System.out.println("demo: Externalizable");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Externalizable; failure mode; how to observe in debugger/profiler.

## Snippet 3: Jackson databind
What it shows: canonical use of Jackson databind; resource handling; observable output.
```java
// serialization-deep snippet 3: Jackson databind
import java.util.*;
public class Snippet3 {
  public static void demo() throws Exception {
    System.out.println("demo: Jackson databind");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Jackson databind; failure mode; how to observe in debugger/profiler.

## Snippet 4: Avro schemas
What it shows: canonical use of Avro schemas; resource handling; observable output.
```java
// serialization-deep snippet 4: Avro schemas
import java.util.*;
public class Snippet4 {
  public static void demo() throws Exception {
    System.out.println("demo: Avro schemas");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Avro schemas; failure mode; how to observe in debugger/profiler.

## Snippet 5: Protobuf
What it shows: canonical use of Protobuf; resource handling; observable output.
```java
// serialization-deep snippet 5: Protobuf
import java.util.*;
public class Snippet5 {
  public static void demo() throws Exception {
    System.out.println("demo: Protobuf");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of Protobuf; failure mode; how to observe in debugger/profiler.

## Snippet 6: versioning & compatibility
What it shows: canonical use of versioning & compatibility; resource handling; observable output.
```java
// serialization-deep snippet 6: versioning & compatibility
import java.util.*;
public class Snippet6 {
  public static void demo() throws Exception {
    System.out.println("demo: versioning & compatibility");
    try (var scope = null) { /* resource goes here */ } catch (Exception e) { throw e; }
  }
}
```
Deep notes: API contract of versioning & compatibility; failure mode; how to observe in debugger/profiler.

## Pitfalls
- Serializable & serialVersionUID: silent misconfig; always assert invariants.
- Externalizable: silent misconfig; always assert invariants.
- Jackson databind: silent misconfig; always assert invariants.
- Avro schemas: silent misconfig; always assert invariants.
// note 0: trace Serializable & serialVersionUID in debugger.
// note 1: trace Externalizable in debugger.
// note 2: trace Jackson databind in debugger.
// note 3: trace Avro schemas in debugger.
// note 4: trace Protobuf in debugger.
// note 5: trace versioning & compatibility in debugger.
// note 6: trace security of deserialization in debugger.
