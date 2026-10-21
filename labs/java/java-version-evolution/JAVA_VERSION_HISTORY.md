# Java Version History — Complete Breakdown

> Covers JDK 1.0 through Java 27 (2026+). Versions after 27 are speculative based on JDK Enhancement Proposal (JEP) momentum.

---

## Java 1.0 (January 1996)
**Codename**: Oak / JDK 1.0  
**LTS**: No  
**Key Features**:
- First public release of Java ("Write Once, Run Anywhere")
- Applets (browser-based Java)
- AWT (Abstract Window Toolkit) for GUI
- Basic networking (java.net)
- Security manager and sandbox model
- Garbage collection (mark-sweep)
- 212 classes in 8 packages
- The HotJava browser (demonstration only)

**Interview Relevance**: Low — historical context only  
**Why**: Nobody uses Java 1.0; question may come up for "why was Java revolutionary?"  
**Sample Interview Question**:  
Q: "What made Java 1.0 revolutionary compared to C++ in 1996?"  
A: Automatic memory management (GC), platform independence via bytecode/JVM, security sandbox, no multiple inheritance (simpler), removal of manual pointers, built-in threading.

**Migration Tip**: N/A — there's nothing to migrate from.  
**Company Focus**: Historical trivia — rarely asked.

---

## Java 1.1 (February 1997)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- Inner classes (anonymous, local, nested)
- JDBC (Java Database Connectivity)
- RMI (Remote Method Invocation)
- JavaBeans component model
- AWT event delegation model (replaced event bubbling)
- Internationalization support (Unicode, Locale)
- JAR file format (ZIP-based archives)

**Interview Relevance**: Low  
**Why**: Inner classes still relevant but assumed knowledge.  
**Sample Interview Question**:  
Q: "What are anonymous inner classes and what limitation do they have compared to lambdas?"  
A: Anonymous inner classes create a separate .class file, cannot capture non-final variables (must be effectively final), and have verbose syntax. Lambdas (Java 8) are more concise and capture variables more efficiently.

```java
// Anonymous inner class (Java 1.1+)
button.addActionListener(new ActionListener() {
    @Override
    public void actionPerformed(ActionEvent e) {
        System.out.println("Clicked!");
    }
});

// Lambda (Java 8+)
button.addActionListener(e -> System.out.println("Clicked!"));
```

**Migration Tip**: Inner classes still work in modern Java. No migration needed.  
**Company Focus**: None specifically.

---

## Java 1.2 (December 1998)
**Codename**: Playground  
**LTS**: No  
**Key Features**:
- **Collections Framework** (List, Set, Map, Iterator, Collections utility)
- Swing GUI toolkit (replaced AWT for rich UIs)
- JIT (Just-In-Time) compiler
- Strictfp keyword
- Reference types (SoftReference, WeakReference, PhantomReference)
- JAR signing and digital signatures
- CORBA integration (deprecated later)

**Interview Relevance**: Medium — Collections Framework is foundational  
**Why**: Every interview touches collections; knowing they were introduced in 1.2 shows historical awareness.  
**Sample Interview Question**:  
Q: "What collections were introduced in Java 1.2 and how did they change Java programming?"  
A: ArrayList, LinkedList, HashMap, TreeMap, HashSet, TreeSet, Vector (retrofit), Stack (retrofit). They replaced ad-hoc arrays and custom data structures. The Iterator pattern unified traversal. Collections utility methods (sort, binarySearch, synchronizedXxx, unmodifiableXxx) reduced boilerplate.

**Migration Tip**: Avoid legacy collections (Vector, Stack, Hashtable, Enumeration) in modern code. Use ArrayList, Deque, ConcurrentHashMap, Iterator/ListIterator.  
**Company Focus**: Any company with old codebases still using Vector/Hashtable.

---

## Java 1.3 (May 2000)
**Codename**: Kestrel  
**LTS**: No  
**Key Features**:
- HotSpot JVM (default, replaced classic VM)
- JNDI (Java Naming and Directory Interface)
- RMI over IIOP (CORBA interoperability)
- JAXP (Java API for XML Processing) — basic DOM and SAX
- Sound API (javax.sound)
- Synthetic proxy classes (java.lang.reflect.Proxy)
- Timer API (java.util.Timer)

**Interview Relevance**: Low  
**Why**: Mostly infrastructure/enterprise features.  
**Sample Interview Question**:  
Q: "What is a dynamic proxy and when would you use it?"  
A: java.lang.reflect.Proxy creates proxy instances at runtime that implement one or more interfaces. Used in AOP frameworks (Spring), ORM lazy loading, and decoration patterns where you want to intercept method calls without compile-time coupling.

```java
InvocationHandler handler = (proxy, method, args) -> {
    System.out.println("Called: " + method.getName());
    return method.invoke(target, args);
};
MyInterface proxy = (MyInterface) Proxy.newProxyInstance(
    classLoader, new Class[]{MyInterface.class}, handler);
```

**Migration Tip**: Dynamic proxies are still used. Nothing to migrate.  
**Company Focus**: Enterprise shops with legacy EJB or CORBA systems.

---

## Java 1.4 (February 2002)
**Codename**: Merlin  
**LTS**: No  
**Key Features**:
- **assert keyword**
- **NIO (New I/O)** — channels, buffers, selectors, non-blocking I/O
- **Regular expressions** (java.util.regex)
- **Logging API** (java.util.logging)
- **Preferences API** (java.util.prefs)
- **LinkedHashMap, LinkedHashSet, IdentityHashMap**
- **Chained exceptions** (Throwable.initCause)

**Interview Relevance**: Low-Medium  
**Why**: NIO is still relevant for high-performance networking. assert and regex are universal.  
**Sample Interview Question**:  
Q: "How does NIO differ from IO in Java 1.4 and how has it evolved since?"  
A: NIO introduced channels (bidirectional), buffers (direct/indirect), and selectors (multiplexed I/O). Unlike IO's stream-oriented blocking reads, NIO supports non-blocking and multiplexed operations. Since 1.4: NIO.2 (Java 7) added Path, Files, WatchService, AIO. Java 11+ improved buffer handling.

**Migration Tip**: Replace java.io.File with java.nio.file.Path and Files API from Java 7. Avoid Selector for simple use cases; use higher-level frameworks (Netty, Vert.x).  
**Company Focus**: Low-latency trading, networking middleware.

---

## Java 5 (September 2004)
**Codename**: Tiger  
**LTS**: No  
**Key Features**:
- **Generics** (type-safe collections, parameterized types)
- **Enhanced for-each loop**
- **Autoboxing/unboxing** (int <-> Integer, etc.)
- **Varargs** (variable-length argument lists)
- **Annotations** (@Override, @Deprecated, @SuppressWarnings)
- **Enum type** (enum keyword, type-safe enums with methods/fields)
- **Static import**
- **Concurrency utilities** (java.util.concurrent — ExecutorService, Semaphore, ConcurrentHashMap, etc.)
- **StringBuilder** (unsynchronized version of StringBuffer)
- **Scanner class** (flexible input parsing)
- **Generics covariance/contravariance** (? extends, ? super)
- **printf-style formatting** (System.out.printf, String.format)

**Interview Relevance**: High  
**Why**: Generics, enums, annotations, and concurrency utilities are daily essentials. The Tiger release is a massive milestone.  
**Sample Interview Question**:  
Q: "Explain how generics work at compile time vs runtime. What is erasure?"  
A: Java generics use type erasure — generic type information is only checked at compile time and removed from bytecode. At runtime, `List<String>` is just `List`. This ensures backward compatibility with pre-generics code but means you cannot use `new T()`, `instanceof T`, or generic arrays. Bridge methods and raw types exist for compatibility.

```java
// Compile time: type-safe
List<String> names = new ArrayList<String>();
names.add("hello");
// String s = names.get(0); // implicit cast

// Runtime: erased to raw type
// List names = new ArrayList();

// Cannot do:
// if (obj instanceof List<String>) { }
// new T()
```

**Migration Tip**: Generics are backward compatible. Raw types still work but generate warnings. When migrating pre-5 code, add generics to collection declarations gradually.  
**Company Focus**: Universal — every Java shop.

---

## Java 6 (December 2006)
**Codename**: Mustang  
**LTS**: No  
**Key Features**:
- **Scripting API** (javax.script — run JavaScript, Groovy, etc. from Java)
- **Compiler API** (javax.tools — programmatic compilation)
- **Pluggable annotation processing** (javax.annotation.processing)
- **JAX-WS** (XML web services, replaced JAX-RPC)
- **JAXB** 2.0 (XML binding — annotations instead of xjc)
- **STAX** (Streaming API for XML)
- **JDBC 4.0** (auto-loading Driver, improved exception handling)
- **Console class** (System.console(), password reading)
- **Java Compiler API** (invoke javac programmatically)

**Interview Relevance**: Low  
**Why**: Mostly enterprise/web-service features. Annotation processing is somewhat niche.  
**Sample Interview Question**:  
Q: "What is pluggable annotation processing and what tools use it?"  
A: Pluggable annotation processing (JSR 269) allows compile-time processing of annotations. Tools use it for code generation: Lombok (@Getter, @Builder), MapStruct (DTO mapping), AutoService, Dagger 2. Processors run during compilation via javac's `-processor` flag or Maven/Gradle plugin config.

**Migration Tip**: Java 6 is ancient. If migrating, skip directly to Java 11 or 17. JAX-WS/JAXB were deprecated in Java 11 and removed in later versions.  
**Company Focus**: Any company maintaining pre-2015 codebases.

---

## Java 7 (July 2011)
**Codename**: Dolphin  
**LTS**: No  
**Key Features**:
- **Diamond operator** (List<String> list = new ArrayList<>();)
- **Try-with-resources** (AutoCloseable, try(Resource r = ...) { })
- **Multi-catch** (catch (IOException | SQLException e))
- **Strings in switch**
- **Binary literals** (int x = 0b1010;)
- **Underscores in numeric literals** (1_000_000)
- **NIO.2 File System API** (Path, Files, FileSystem, WatchService, DirectoryStream)
- **Fork/Join Framework** (ForkJoinPool, RecursiveTask, RecursiveAction)
- **Phaser** (flexible barrier synchronization)
- **InvokeDynamic** (JVM instruction for dynamic language support)
- **Automatic resource management improvements**

**Interview Relevance**: Medium  
**Why**: Try-with-resources, diamond, and NIO.2 are used daily. Fork/Join demonstrates concurrency knowledge.  
**Sample Interview Question**:  
Q: "Explain try-with-resources and how it handles closing multiple resources."  
A: Try-with-resources (Java 7) automatically closes any resource implementing AutoCloseable. Multiple resources are closed in reverse order of declaration. If both the try block and close() throw exceptions, the try block exception is primary and close() exceptions are suppressed (accessible via Throwable.getSuppressed()).

```java
try (FileInputStream is = new FileInputStream("a.txt");
     FileOutputStream os = new FileOutputStream("b.txt")) {
    is.transferTo(os);
} catch (IOException e) {
    // Close exceptions are suppressed here
    for (Throwable t : e.getSuppressed()) {
        // log suppressed exceptions
    }
}
```

**Migration Tip**: Replace finally-block resource cleanup with try-with-resources. Replace File with Path/Files. Replace manual String concatenation in switch with string switching.  
**Company Focus**: Universal — every Java programmer uses try-with-resources.

---

## Java 8 (March 2014)
**Codename**: (none)  
**LTS**: Yes  
**Key Features**:
- **Lambda expressions** (-> syntax, functional interfaces)
- **Stream API** (map, filter, reduce, collect, flatMap, parallelStream)
- **Optional<T>** (value container, null-safe chaining)
- **Date/Time API** (java.time — LocalDate, LocalTime, ZonedDateTime, Instant, Duration, Period)
- **Default methods in interfaces** (defender methods)
- **Static methods in interfaces**
- **Functional interfaces** (@FunctionalInterface, java.util.function — Predicate, Function, Consumer, Supplier, etc.)
- **Method references** (Class::staticMethod, instance::method, Class::new)
- **CompletableFuture** (async computation, chaining, combining)
- **java.util.stream.Collectors** (toList, groupingBy, partitioningBy, joining)
- **Nashorn JavaScript Engine** (jjs command)
- **Type annotations** (@NonNull String, etc.)
- **Repeating annotations**
- **Parallel array sorting** (Arrays.parallelSort)
- **Base64 encoding/decoding** (java.util.Base64)
- **StringJoiner**
- **HashMap performance improvement** (tree-based buckets for hash collisions)
- **Metaspace** (replaces PermGen, uses native memory)
- **JVM parameter improvements** (UseStringDeduplication, G1GC default)

**Interview Relevance**: CRITICAL — highest of all versions  
**Why**: Lambdas and streams transformed Java. Every interview asks about them. Java 8 is still the baseline for most enterprises.  
**Sample Interview Question**:  
Q: "How do lambdas capture variables? What is effectively final?"  
A: Lambdas capture local variables from the enclosing scope. Captured variables must be effectively final — not reassigned after initialization. This differs from anonymous inner classes (which required explicit final in Java 7). Lambdas also capture `this` differently: `this` in a lambda refers to the enclosing instance, not the lambda itself.

```java
String greeting = "Hello"; // effectively final
// greeting = "Hi"; // would not compile

Runnable r = () -> System.out.println(greeting + ", world!");

// Compare with anonymous class:
Runnable r2 = new Runnable() {
    @Override
    public void run() {
        // this refers to the anonymous class, not enclosing
    }
};
// Lambda:
Runnable r3 = () -> {
    // this refers to the enclosing instance
    System.out.println(this.toString());
};
```

**More Sample Interview Questions about Java 8**:

Q: "What is the difference between intermediate and terminal operations in streams?"  
A: Intermediate operations (map, filter, sorted, distinct, peek, limit, skip) return a new stream and are lazy — they don't execute until a terminal operation is invoked. Terminal operations (forEach, collect, reduce, count, anyMatch, allMatch, noneMatch, findFirst, findAny) trigger the pipeline execution and consume the stream. A stream can only have one terminal operation.

```java
// Nothing executes until collect() is called
List<String> result = names.stream()
    .filter(n -> n.startsWith("A"))
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());
```

Q: "How does Optional help avoid NullPointerException? What are its pitfalls?"  
A: Optional<T> forces the caller to consider the absent case. Methods: map, flatMap, filter, orElse, orElseGet, orElseThrow, ifPresent. Pitfalls: using Optional as a field type (not serializable), using Optional as a method parameter, calling get() without checking isPresent(), overusing with collections (use empty collections instead).

```java
// Good: Optional return type
public Optional<Customer> findById(Long id) {
    return Optional.ofNullable(cache.get(id));
}

// Calling code
Customer c = findById(42L)
    .orElseThrow(() -> new NotFoundException("Customer not found"));

// Avoid:
// Optional<Customer> field; // not serializable
// public void process(Optional<Customer> c) // bad parameter
```

Q: "Explain the Date/Time API introduced in Java 8. How is it better than java.util.Date?"  
A: The java.time package (JSR 310) was inspired by Joda-Time. Improvements: immutable and thread-safe classes, fluent API, clear separation between human time (LocalDate, LocalTime) and machine time (Instant), proper timezone handling (ZonedDateTime, ZoneId), duration/period for time math, no bad defaults (Date's year 1900 offset, month 0-index), comprehensive formatting/parsing.

```java
LocalDate today = LocalDate.now();
LocalDate xmas = LocalDate.of(2024, Month.DECEMBER, 25);
Period untilXmas = Period.between(today, xmas);

ZonedDateTime meeting = ZonedDateTime.of(
    LocalDateTime.of(2024, 6, 15, 14, 0),
    ZoneId.of("America/New_York")
);
Instant instant = meeting.toInstant(); // machine time
```

**Migration Tip**:  
- Replace java.util.Date and java.util.Calendar with java.time.*  
- Replace SimpleDateFormat with DateTimeFormatter (thread-safe)  
- Replace `new Date()` with `Instant.now()` or `LocalDateTime.now()`  
- Add `--add-modules java.xml.bind` for JAXB in some environments (removed in 11)  
- Ensure CI/CD pipeline supports JDK 8 (minimum Maven 3.1, Gradle 2.x)  

**Company Focus**: Absolute necessity for every company. Most still run Java 8.

---

## Java 9 (September 2017)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Module System (Project Jigsaw)** — java.base, module-info.java, exports, requires, opens
- **JShell** (REPL: Read-Eval-Print Loop)
- **Collection factory methods** (List.of(), Set.of(), Map.of())
- **Stream improvements** (takeWhile, dropWhile, ofNullable, iterate with predicate)
- **Optional improvements** (ifPresentOrElse, or, stream)
- **Private methods in interfaces**
- **Process API** (ProcessHandle, ProcessHandle.Info)
- **Reactive Streams** (java.util.concurrent.Flow — Publisher, Subscriber, Processor)
- **HTTP/2 client** (jdk.incubator.httpclient — incubator module)
- **Try-with-resources improvement** (effectively final variables)
- **Multi-release JARs** (compile code for different versions in a single JAR)
- **Diamond operator for anonymous classes** (Java 9+ allows <> with anonymous classes)
- **Stack-walking API** (java.lang.StackWalker)
- **@SafeVarargs improvement** (allowed on private methods)
- **String compact representation** (Latin-1 vs UTF-16 based on content)
- **G1 GC becomes default** (replaced CMS)
- **Deprecated Applet API**
- **JavaFX modularized**

**Interview Relevance**: Medium  
**Why**: Modules are important for large applications; JShell and collection factories are daily tools.  
**Sample Interview Question**:  
Q: "How does the module system affect the classpath? What is module-path vs classpath?"  
A: The module system (Jigsaw) introduces module-path, replacing the traditional classpath for modular JARs. Module declarations in module-info.java specify dependencies (requires) and exported packages (exports). Non-modular JARs go on the classpath, modular JARs on module-path. The module system provides strong encapsulation (reflection only allowed with opens), reliable configuration (no classpath order issues), and improved security.

```java
// module-info.java
module com.myapp {
    requires java.sql;
    requires org.slf4j;
    exports com.myapp.api;
    exports com.myapp.dto;
    opens com.myapp.internal to com.fasterxml.jackson.databind;
}
```

**Migration Tip**:  
- Add module-info.java for new applications  
- For existing apps, start with unnamed module (classpath) and gradually migrate  
- Watch for split packages (same package across multiple modules)  
- Use jdeps to analyze dependencies  
- java.se module includes most standard modules; java.se.ee for removed EE modules  

**Company Focus**: Companies with large monorepos or microservice architectures benefit from module boundaries.

---

## Java 10 (March 2018)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Local-variable type inference (var)** — must have initializer, cannot use for fields/method params/return types
- **Parallel full GC for G1** (worst-case latency improvement)
- **Application Data Sharing (CDS)** — default CDS archives for faster startup
- **Thread-local handshake** (low-latency JVM operations)
- **Root certificates** (CA certificates bundled with JDK)
- **Heap allocation on alternative devices** (NV-DIMM support)
- **Time-based release versioning** (JDK 10.0.1 format)
- **Consolidated JRE/JDK images** (no separate JRE, jlink creates custom runtimes)

**Interview Relevance**: Medium  
**Why**: var is controversial and commonly debated in interviews.  
**Sample Interview Question**:  
Q: "What are the rules and limitations of var in Java 10?"  
A: var can only be used for local variables with initializers (including for-each and for-loop indices). Cannot use var for fields, method parameters, return types, catch variables, or without initializer. var infers the compile-time type — it's not dynamic typing. Poly expressions (ternary, lambda, method reference) must have a known target type.

```java
var list = new ArrayList<String>(); // inferred as ArrayList<String>
var number = 42; // int, not Integer
var stream = list.stream(); // Stream<String>

// Invalid:
// var x; // no initializer
// var f = null; // type cannot be inferred from null
// public void method(var param) { } // no parameter
```

**Migration Tip**: Use var where it improves readability (obvious constructor types, complex generics). Avoid var when it obscures intent (List<String> vs var on a method call returning List<String>).  
**Company Focus**: All modern Java shops — some have explicit style guide rules about var.

---

## Java 11 (September 2018)
**Codename**: (none)  
**LTS**: Yes  
**Key Features**:
- **HTTP Client (standard)** — java.net.http.HttpClient, HttpRequest, HttpResponse, HTTP/2, WebSocket
- **Launch single-file source-code programs** (java HelloWorld.java — no javac needed)
- **String enhancements** (isBlank, lines, strip, stripLeading, stripTrailing, repeat)
- **Files enhancements** (readString, writeString for text files)
- **Collection.toArray(String[]::new)** — improved toArray with method reference
- **var in lambda parameters** ((@NotNull var x, var y) -> x + y) — consistent with local var
- **Nest-based access** (nested classes can access private members without synthetic accessors)
- **Optional.isEmpty()** — negation of isPresent()
- **Reading/Writing strings from files** (Files.readString, Files.writeString)
- **Flight Recorder** (Java Flight Recorder — now open source)
- **No more Java EE / CORBA modules** (removed: JAX-WS, JAXB, JAF, CORBA)
- **HttpClient replaces legacy HttpURLConnection**
- **Epsilon GC** (no-op GC for short-lived services)
- **ZGC** (experimental — low-latency, scalable, sub-millisecond pauses)
- **Dynamic class-file constants** (performance improvement for lambdas/strings)
- **Thread-local handshake (per-thread)**
- **Key agreement with Curve25519/448**
- **ChaCha20/Poly1305 cipher**
- **TLS 1.3**
- **Nestmates (JVM improvement for nested classes)**

**Interview Relevance**: High — especially HTTP Client, single-file programs, and removals  
**Why**: Java 11 is the second LTS after Java 8; most companies migrated 8 -> 11 or 8 -> 17.  
**Sample Interview Question**:  
Q: "What was removed from Java 11 compared to Java 8/9?"  
A: Java 11 removed Java EE modules (JAX-WS, JAXB, JAF, CORBA) that were deprecated in Java 9. These were in the java.se.ee module. Also removed: JavaFX (moved to OpenJFX as separate project), Nashorn engine (deprecated, removed in 15), Applet API. Applications using JAXB must add it as a third-party dependency (e.g., via Maven).

```java
// Java 11: HTTP Client standard
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .GET()
    .build();
HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());
```

Q: "How does running .java files directly work in Java 11?"  
A: `java HelloWorld.java` compiles and runs a single-file source-code program in memory. It's designed for small scripts and educational purposes. The program cannot use classes outside the source file unless on the classpath/modulepath. Only the first top-level class is executed. This is not meant for production but for prototyping.

**Migration Tip**:  
- Remove JAXB/JAX-WS from classpath or add explicit Maven dependencies  
- Replace HttpURLConnection with java.net.http.HttpClient  
- Update build tools: Gradle 5+, Maven 3.6+  
- Check for use of deprecated API (Nashorn, Applet, JavaFX)  

**Company Focus**: Every enterprise — this is the most common migration target.

---

## Java 12 (March 2019)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Switch expressions (preview)** — arrow syntax, no fall-through, expression form
- **Shenandoah GC** (low-pause, concurrent GC — experimental)
- **Microbenchmark suite** (JMH-based)
- **Compact number formatting** (NumberFormat.getCompactNumberInstance)
- **Files.mismatch(Path, Path)** — first byte difference position
- **Teeing Collector** (Collectors.teeing — two collectors in parallel)
- **Improved G1 GC** (abortable mixed collections for pause time predictability)
- **Default CDS archives** (improved startup time)
- **Promptly return unused memory** (G1 returns to OS)
- **JVM constants API** (class-file constant pool access)

**Interview Relevance**: Low  
**Why**: Switch expressions were still preview. Teeing collector is niche.  
**Sample Interview Question**:  
Q: "What is Collectors.teeing()?"  
A: Collectors.teeing() (Java 12) takes two downstream collectors and a merger function. It processes stream elements with both collectors simultaneously and merges results. Useful for computing multiple aggregates in a single pass.

```java
var stats = orders.stream()
    .collect(Collectors.teeing(
        Collectors.counting(),
        Collectors.summingDouble(Order::total),
        (count, sum) -> new OrderStats(count, sum)
    ));
```

**Migration Tip**: Switch expressions stabilized in Java 14. Use standard syntax until then or enable preview.  
**Company Focus**: Niche — mostly low-latency trading.

---

## Java 13 (September 2019)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Text blocks (preview)** — triple-quote """ multiline strings
- **Switch expressions (2nd preview)** — yield statement, refined
- **Reimplemented Socket API** (NIO-based, more scalable)
- **FileSystems.newFileSystem(Path, Map)** — better FS creation
- **ZGC improvements** — return unused heap to OS
- **Dynamic CDS archives**
- **Flying Saucer** (GraphicsEnvironment improvements)

**Interview Relevance**: Low-Medium  
**Why**: Text blocks are popular; still preview until Java 15.  
**Sample Interview Question**:  
Q: "What are text blocks and what advantages do they offer over traditional strings?"  
A: Text blocks (""" ... """) provide multiline string literals without escape sequences for newlines and quotes. They preserve indentation (via stripIndent), strip trailing spaces, and make SQL, JSON, HTML, and XML embedded strings readable. Introduced as preview in Java 13, standardized in Java 15.

```java
// Before text blocks (painful):
String json = "{\n" +
    "  \"name\": \"John\",\n" +
    "  \"age\": 30\n" +
    "}";

// After text blocks:
String json = """
    {
      "name": "John",
      "age": 30
    }
    """;
```

**Migration Tip**: Enable preview with --enable-preview to use text blocks before Java 15.  
**Company Focus**: Any shop that embeds SQL/JSON/XML in Java.

---

## Java 14 (March 2020)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Records (preview)** — compact class declaration for data carriers
- **Pattern matching for instanceof (preview)** — binding variable
- **Switch expressions (standard)** — stabilized from Java 12/13 preview
- **Text blocks (2nd preview)** — minor refinements (escape sequences for space/newline)
- **Helpful NullPointerExceptions** — JVM shows exactly which variable was null
- **Packaging tool (jpackage)** — platform-native installers (EXE, DMG, DEB)
- **NUMA-aware memory allocation for G1**
- **Foreign-Memory Access API (incubator)** — off-heap memory access
- **Non-Volatile Mapped Byte Buffers** — persistent memory

**Interview Relevance**: Medium  
**Why**: Records and pattern matching for instanceof are critical modern features. Switch expressions stabilized.  
**Sample Interview Question**:  
Q: "What are records in Java 14? What limitations do they have?"  
A: Records (JEP 359) are transparent data carriers with auto-generated constructor, accessors, equals, hashCode, toString. They are implicitly final, cannot extend other classes, cannot declare instance fields, and cannot be abstract. They can implement interfaces, have static fields, and define instance methods.

```java
// Record declaration (implicit: constructor, getters, equals, hashCode, toString)
public record Point(int x, int y) {}

// Usage
Point p = new Point(3, 4);
int x = p.x(); // accessor, not getX()
System.out.println(p); // Point[x=3, y=4]

// Canonical constructor with validation
public record PositivePoint(int x, int y) {
    public PositivePoint {
        if (x < 0 || y < 0) throw new IllegalArgumentException();
    }
}
```

**Migration Tip**: Replace Lombok @Data/@Value classes with records where appropriate. Record components are final (immutable).  
**Company Focus**: Modern Java shops moving to 17+.

---

## Java 15 (September 2020)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Text blocks (standard)** — finalized
- **Sealed classes (preview)** — permits clause, sealed interface/class
- **Pattern matching for instanceof (2nd preview)** — minor refinements
- **Records (2nd preview)** — added interfaces, sealed, records in local scopes
- **Hidden classes** — for bytecode manipulation frameworks (Lombok, proxies)
- **ZGC production-ready** — no longer experimental
- **Shenandoah GC production-ready** — no longer experimental
- **EdDSA signature algorithm**
- **Disabled biased locking** — performance improvement
- **Trees in documentation** (javadoc @param improvements)
- **Removed Nashorn** (finally removed)
- **Removed RMI compiler** (rmic)
- **Foreign-Memory Access API (2nd incubator)**

**Interview Relevance**: Medium  
**Why**: Sealed classes preview (important for domain modeling), text blocks final.  
**Sample Interview Question**:  
Q: "What are sealed classes and how do they improve domain modeling?"  
A: Sealed classes/interfaces restrict which other classes/interfaces may extend/implement them. This enables exhaustive pattern matching, prevents unintended subclassing, and expresses domain constraints. The permits clause lists allowed subclasses, which must be final, sealed, or non-sealed.

```java
public sealed interface Shape
    permits Circle, Rectangle, Triangle { }

public final class Circle implements Shape { }
public final class Rectangle implements Shape { }
public final class Triangle implements Shape { }

// Exhaustive switch (requires no default if all cases covered)
String area = switch (shape) {
    case Circle c -> "Circle area: " + Math.PI * c.radius() * c.radius();
    case Rectangle r -> "Rect area: " + r.width() * r.height();
    case Triangle t -> "Tri area: " + 0.5 * t.base() * t.height();
};
```

**Migration Tip**: Sealed classes stabilized in Java 17. Use with --enable-preview.  
**Company Focus**: Domain-driven design shops, fintech, modeling-heavy applications.

---

## Java 16 (March 2021)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Records (standard)** — finalized
- **Pattern matching for instanceof (standard)** — finalized
- **Sealed classes (2nd preview)** — improved
- **incubating: Foreign Linker API** — call native libraries (C) from Java
- **Vector API (incubator)** — SIMD vector operations
- **Elastic metaspace** — pool unused class metadata memory
- **Unix-Domain Socket Channels** — local inter-process communication
- **Stream.toList()** — immutable list collector (convenience method)
- **Day Period support** (DateTimeFormatter.ofPattern("B") — "in the morning")
- **java.lang.reflect.Proxy changes** — sealed proxy classes
- **DatagramSocket reimplementation** (replaces old plain socket impl)

**Interview Relevance**: Medium  
**Why**: Records and pattern matching for instanceof finalized — extremely common in modern Java.  
**Sample Interview Question**:  
Q: "What is pattern matching for instanceof and how is it better than traditional instanceof?"  
A: Pattern matching for instanceof combines type check, type cast, and scope-binding into one construct. The binding variable is scoped to the if block (or the else block for the negative case). No more redundant casts.

```java
// Before (Java 7-15):
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}

// After (Java 16+):
if (obj instanceof String s) {
    System.out.println(s.length()); // s is already String
}
```

**Migration Tip**: Replace all `if (x instanceof Foo) { Foo f = (Foo) x; }` patterns with `if (x instanceof Foo f)`.  
**Company Focus**: Universal for Java 16+ codebases.

---

## Java 17 (September 2021)
**Codename**: (none)  
**LTS**: Yes  
**Key Features**:
- **Sealed classes (standard)** — finalized
- **Pattern matching for switch (preview)** — switch on type patterns
- **Records (stable)** — already finalized in 16, repeated emphasis
- **Text blocks (stable)** — already finalized in 15
- **Foreign Function & Memory API (incubator)** — Panama project
- **Vector API (2nd incubator)** — SIMD
- **Switch expressions (stable)** — already stabilized in 14
- **Enhanced pseudo-random number generators** — new interfaces, implementations
- **New macOS rendering pipeline** — Metal API (replacing OpenGL)
- **Context-specific deserialization filters** — security against deserialization attacks
- **Strongly encapsulated JDK internals** — illegal access flagged by default, removal path for sun.misc.Unsafe
- **Deprecation of Security Manager** — for removal
- **Restore always-strict floating-point semantics** (strictfp by default)
- **Hex formatting/parsing** (toHexString, fromHexString utilities)
- **Loading of class files with specific CDS** (AppCDS for non-JDK classes)

**Interview Relevance**: Very High — the current default LTS for new projects  
**Why**: Java 17 is the most common modern LTS target after Java 8. Sealed classes, pattern matching for switch preview, records.  
**Sample Interview Question**:  
Q: "What changes in Java 17 affect migration from Java 11?"  
A: Major migration points: (1) Strong encapsulation of JDK internals — illegal reflective access now results in errors; add `--add-opens` flags or fix code. (2) Security Manager deprecated for removal. (3) Removed: Nashorn, RMI compiler, Java EE modules (already gone in 11), Applet API, AWT S splash screen removed. (4) New default for rounding: strictfp restored as always-on. (5) Pattern matching for switch available as preview.

```java
// Java 17 sealed classes + pattern matching preview
public sealed interface Vehicle permits Car, Truck, Motorcycle { }
public record Car(String model, int doors) implements Vehicle { }
public record Truck(int loadCapacity) implements Vehicle { }
public record Motorcycle(boolean hasSidecar) implements Vehicle { }

// Pattern matching for switch (preview in 17)
static String describe(Vehicle v) {
    return switch (v) {
        case Car c -> "Car with " + c.doors() + " doors";
        case Truck t -> "Truck with " + t.loadCapacity() + "kg capacity";
        case Motorcycle m -> "Motorcycle" + (m.hasSidecar() ? " with sidecar" : "");
    };
}
```

**Migration Tip**:  
- Run with `--illegal-access=deny` to detect reflection issues before upgrade  
- Replace all `sun.misc.Unsafe` usage where possible  
- Test with pattern matching preview enabled  
- Update build tools: Gradle 7.3+, Maven 3.8+  
- Check library compatibility (Spring Boot 2.5+, Hibernate 5.5+)  

**Company Focus**: Every company starting new projects or planning LTS migration.

---

## Java 18 (March 2022)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **UTF-8 by default** — charset changed from platform-dependent to UTF-8
- **Simple web server** — `jwebserver` CLI tool for static files
- **Code snippets in Javadoc** (`@snippet` tag)
- **Reimplementation of core reflection** (Method, Field, Constructor) with method handles
- **Vector API (3rd incubator)** — SIMD
- **Foreign Function & Memory API (2nd incubator)**
- **Pattern matching for switch (2nd preview)** — refinements
- **Internet-Address resolution SPI** — pluggable DNS resolver
- **Deprecation of finalization for removal**
- **G1 improvements** (automatic parallel full GC)
- **ZGC improvements** (generational ZGC preview)

**Interview Relevance**: Low  
**Why**: Mostly infrastructure changes. `jwebserver` is useful but minor.  
**Sample Interview Question**:  
Q: "What changed about default charset in Java 18?"  
A: Java 18 defaulted Charset to UTF-8 across all platforms. Previously, it depended on the OS locale. This affects FileReader, FileWriter, InputStreamReader, OutputStreamWriter, Formatter, Scanner, URLEncoder/URLDecoder without explicit charset. This is a subtle source of bugs for developers who assumed the old platform-dependent behavior.

**Migration Tip**: Check for code that relied on platform-dependent encoding (e.g., writing files with non-UTF-8 encodings). Add explicit charset parameters where needed.  
**Company Focus**: Low — most teams wouldn't notice the UTF-8 change.

---

## Java 19 (September 2022)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Virtual Threads (preview)** — Project Loom: lightweight, structured concurrency
- **Record patterns (preview)** — deconstruct records in pattern matching
- **Pattern matching for switch (3rd preview)** — more refinements
- **Foreign Function & Memory API (preview)** — finalized its design
- **Vector API (4th incubator)** — SIMD
- **Structured Concurrency (incubator)** — structured task management
- **Linux/RISC-V port**
- **Time-Loaded Reference Objects** (incubator for low-latency GC interaction)

**Interview Relevance**: High — virtual threads debut  
**Why**: Virtual threads are the most significant concurrency change since java.util.concurrent in Java 5.  
**Sample Interview Question**:  
Q: "What are virtual threads and how do they differ from platform threads?"  
A: Virtual threads (Project Loom) are lightweight threads managed by the JVM, not the OS. Millions can exist. They are cheap to create, block, and park. Platform threads are OS-managed, heavyweight (MB of stack), and limited to thousands. Virtual threads use carrier platform threads under the hood and yield during blocking operations.

```java
// Creating virtual threads (Java 19 preview)
Thread vThread = Thread.startVirtualThread(() -> {
    System.out.println("Hello from virtual thread");
});

// Using Executors.newVirtualThreadPerTaskExecutor()
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> executor.submit(() -> {
        Thread.sleep(1000);
        return i;
    }));
} // executor.close() waits for all tasks
```

**Migration Tip**: Enable preview features. Virtual threads require no code changes in most cases — just switch thread pools.  
**Company Focus**: High-throughput I/O services (web servers, microservices, databases).

---

## Java 20 (March 2023)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Virtual Threads (2nd preview)** — refinements, improved stability
- **Record patterns (2nd preview)** — more deconstruction options
- **Pattern matching for switch (4th preview)** — type patterns refinement
- **Foreign Function & Memory API (2nd preview)** — API refinement
- **Vector API (5th incubator)** — SIMD
- **Structured Concurrency (2nd incubator)** — improvements based on feedback
- **Scoped Values (incubator)** — inheritable thread-local alternative
- **Improved JVM debugging** (JDWP improvements)

**Interview Relevance**: Medium  
**Why**: Preview features maturing. Scoped values debut.  
**Sample Interview Question**:  
Q: "What are scoped values and how do they differ from ThreadLocal?"  
A: Scoped Values (incubator in Java 20) allow sharing immutable data within a thread (or virtual thread) without mutation overhead or memory leaks of ThreadLocal. Unlike ThreadLocal, scoped values are immutable once bound, don't require cleanup, and work correctly with virtual threads (which could outlive pool threads). They use StructuredTaskScope for fallback.

```java
// Scoped Value (conceptual, API in incubator)
final static ScopedValue<String> USER_ID = ScopedValue.newInstance();

ScopedValue.where(USER_ID, "user123", () -> {
    // Inside this scope, USER_ID.get() returns "user123"
    processRequest();
});
```

**Migration Tip**: Evaluate ScopedValues as a ThreadLocal replacement. Still incubating.  
**Company Focus**: Concurrency-intensive applications.

---

## Java 21 (September 2023) — Current LTS
**Codename**: (none)  
**LTS**: Yes  
**Key Features**:
- **Virtual Threads (standard)** — stable, production-ready
- **Sequenced Collections** — SequencedCollection, SequencedSet, SequencedMap interfaces
- **Record Patterns (standard)** — deconstruct records in pattern matching
- **Pattern Matching for Switch (standard)** — final, type patterns, guard clauses
- **String Templates (preview)** — STR, FMT, RAW template processors (withdrawn before JDK 23; not on any current JDK)
- **Structured Concurrency (preview)** — StructuredTaskScope for managing tasks
- **Scoped Values (preview)** — inheritable thread-locals for virtual threads
- **Generational ZGC** — improved throughput and heap utilization
- **Unnamed classes and instance main methods (preview)** — simplified hello world
- **Unnamed patterns and variables (preview)** — underscore for unused variables
- **Math.clamp** — clamp values to a range
- **Sequenced Map/Set/Collection methods** — getFirst, getLast, reversed, addFirst, addLast
- **StringBuilder.repeat** — append repeated characters
- **HttpClient adds sendAsync with CompletableFuture timeout support**
- **Key encapsulation mechanism API**
- **Structured concurrency improved error propagation**

**Interview Relevance**: VERY HIGH — current LTS, most modern feature set  
**Why**: Virtual threads production-ready. Pattern matching for switch finalized. This is the version to know for 2024-2026 interviews.  
**Sample Interview Question**:  
Q: "How do virtual threads work under the hood?"  
A: Virtual threads are implemented as continuations running on a ForkJoinPool of carrier (platform) threads. When a virtual thread performs a blocking operation (I/O, lock, sleep), the JVM unmounts it from the carrier thread and parks it. The carrier thread picks up another virtual thread. When the blocking operation completes, the virtual thread is rescheduled on any available carrier thread. This allows millions of virtual threads on a small number of platform threads.

```java
// Virtual threads in action (Java 21)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<Result>> futures = urls.stream()
        .map(url -> executor.submit(() -> fetchUrl(url)))
        .toList();
    for (var future : futures) {
        results.add(future.get());
    }
}
```

Q: "What are sequenced collections and what problem do they solve?"  
A: Sequenced collections add a common interface for collections with a defined encounter order. Previously, LinkedList had getFirst/getLast but not from a common interface. SequencedCollection (interface) provides addFirst, addLast, getFirst, getLast, reversed(). SequencedSet and SequencedMap extend this for their respective types.

```java
// New interfaces in Java 21
SequencedCollection<String> seq = new LinkedHashSet<>();
seq.addFirst("a");
seq.addLast("z");
String first = seq.getFirst(); // "a"
SequencedCollection<String> reversed = seq.reversed();
```

Q: "Explain record patterns and pattern matching for switch in Java 21."  
A: Record patterns allow destructuring records in pattern matching. Combined with pattern matching for switch, this enables very expressive data processing. Guards (when clause) add conditions.

```java
record Point(int x, int y) {}
record Line(Point start, Point end) {}
record Circle(Point center, int radius) {}

static String describe(Object obj) {
    return switch (obj) {
        case Point(int x, int y) -> "Point at (" + x + "," + y + ")";
        case Line(Point s, Point e) -> "Line from " + describe(s) + " to " + describe(e);
        case Circle(Point c, int r) when r > 0 -> "Circle at " + describe(c) + " radius " + r;
        case null -> "null object";
        default -> "Unknown";
    };
}
```

**Migration Tip**:  
- Replace Executors.newFixedThreadPool with Executors.newVirtualThreadPerTaskExecutor  
- Add Thread.ofVirtual() for inline virtual thread creation  
- Update to Spring Boot 3.2+, which supports virtual threads  
- Use jlink to create custom runtime images  
- Migrate to records for DTOs and value objects  
- Do NOT adopt string templates: the preview was withdrawn wholesale before JDK 23 — build interpolation on `String.formatted` instead  

**Company Focus**: Any company writing new Java projects in 2024-2026.

---

## Java 22 (March 2024)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Unnamed Variables & Patterns (final)** — finalized from preview
- **Launch multi-file source programs** (java prog.java lib.java without compilation)
- **String Templates (2nd preview)** — refined based on feedback
- **Structured Concurrency (2nd preview)** — refinement
- **Scoped Values (2nd preview)** — refinement
- **Stream Gatherers (preview)** — custom intermediate stream operations
- **Vector API (7th incubator)** — SIMD
- **Foreign Function & Memory API (3rd preview)** — nearing final
- **Class-File API (preview)** — standard API for parsing class files
- **Region Pinning for G1** — improved virtual thread support for GC
- **Implicitly Declared Classes and Instance Main Methods (2nd preview)**
- **Simple source launcher enhancements**
- **Stream.toList() becomes more flexible**

**Interview Relevance**: Medium  
**Why**: Stream Gatherers are interesting for advanced stream processing.  
**Sample Interview Question**:  
Q: "What are Stream Gatherers in Java 22?"  
A: Stream Gatherers (preview) allow custom intermediate stream operations beyond the built-in ones (filter, map, etc.). They define how to process elements one at a time, accumulate state, and produce output elements. Useful for sliding windows, grouping with custom logic, and stateful transformations.

```java
// Stream Gatherer concept (preview API)
var result = stream.gather(Gatherers.windowFixed(3))
    .map(window -> window.stream().mapToInt(Integer::intValue).sum())
    .toList();
```

**Migration Tip**: Enable preview for Stream Gatherers. Most code won't need changes except for enhanced Stream APIs.  
**Company Focus**: Data processing pipelines, ETL, analytics.

---

## Java 23 (September 2024)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- ~~String Templates (3rd preview)~~ — withdrawn before Java 23: the experts group declined to continue the preview
- **Structured Concurrency (3rd preview)** — continued refinement
- **Scoped Values (3rd preview)** — continued refinement  
- **Foreign Function & Memory API (4th preview)** — nearing completion
- **Vector API (8th incubator)** — continued
- **Flexible Constructor Bodies (preview)** — execute statements before super()
- **Publishing Custom Events (JMX improvements)**
- **Deprecate Memory-Access Methods in sun.misc.Unsafe for removal**
- **Deprecate Windows 32-bit x86 port for removal**
- **Performance: hash-based collections improvements**
- **Allows multiple flexible constructor parameters**

**Interview Relevance**: Low-Medium  
**Why**: Flexible constructor bodies are a significant language change for initialization patterns.  
**Sample Interview Question**:  
Q: "What are flexible constructor bodies (preview in Java 23)?"  
A: Flexible constructor bodies allow statements (like validation, field initialization) before super() or this() calls, as long as no reference to `this` is made before the super call. This solves the problem of needing to precompute values before passing them to super().

```java
// Before Java 23: must use static method/temp variable
class Child extends Parent {
    public Child(int value) {
        super(validate(value)); // could not do much pre-computation
    }
    
    // Java 23+:
    public Child(int value) {
        if (value < 0) throw new IllegalArgumentException();
        int processed = preprocess(value);
        super(processed);
    }
}
```

**Migration Tip**: Enable preview features for flexible constructor bodies. This is a minor but welcomed improvement.  
**Company Focus**: Framework/library authors.

---

## Java 24 (March 2025)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **String Templates — absent**: not in Java 24; the preview was withdrawn before Java 23 (no finalized form exists on any JDK)
- **Stream Gatherers (2nd preview)** — continued refinement
- **Class-File API (final)** — standard API for class file processing
- **Foreign Function & Memory API (standard)** — finalized
- **Simple source launcher: mixed source + class files**
- **Module imports (preview)** — import module declarations
- **Floating-point optimizations** (improved Math APIs)
- **AOT-compiled java.base via Leyden (preview)** — instant startup
- **Structured Concurrency (preview continued)** — nearing final
- **Scoped Values (preview continued)** — nearing final
- **Generational ZGC by default**
- **Scoped value support in all thread types**

**Interview Relevance**: Medium  
**Why**: Stream Gatherers and FFMI near completion; String Templates stayed withdrawn (not finalized — use `String.formatted`).  
**Sample Interview Question**:  
Q: "What is the class-file API in Java 24?"  
A: The Class-File API (standardized in Java 24) provides a standard, JDK-maintained API for parsing, transforming, and generating Java class files. Previously only possible with third-party libraries (ASM, ByteBuddy). The API follows a visitor pattern and supports constant pool, attributes, instructions, and annotations.

**Migration Tip**: The FFMI finalization means you can call C libraries without JNI now. Evaluate for native code scenarios.  
**Company Focus**: System programming, frameworks, code generation tools.

---

## Java 25 (September 2025)
**Codename**: (none)  
**LTS**: Yes (next LTS after Java 21)  
**Key Features**:
- **Structured Concurrency (standard)** — finalized
- **Scoped Values (standard)** — finalized
- **Stream Gatherers (standard)** — finalized
- **Flexible Constructor Bodies (standard)** — finalized
- **Module imports (standard)** — finalized
- **Implicitly Declared Classes and Instance Main Methods (standard)** — finalized
- **Value Objects / Primitive Classes (Project Valhalla — preview)** — inline classes with value semantics
- **AOT compilation for startup optimization (Leyden — preview)**
- **Unnamed classes improvements**
- **Enhanced switch for sealed types** (exhaustiveness without default)
- **Universal Generics (preview)** — Project Valhalla generics over primitives
- **Profiling-based optimizations** (JVM learns usage patterns)
- **Heap access optimizations for value types**

**Interview Relevance**: Very High — first LTS in 2 years, major new features  
**Why**: Structured concurrency, scoped values, value objects (Valhalla) — major paradigm shifts.  
**Sample Interview Question**:  
Q: "What are value objects / primitive classes in Project Valhalla?"  
A: Value objects (inline classes) provide the performance of primitives with the abstraction of objects. They have no identity (== compares by value, not reference), cannot be null, and may be flattened in arrays. This eliminates boxing overhead and enables new optimization opportunities.

```java
// Value class (preview)
inline class Point {
    private int x;
    private int y;
    
    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

Point p1 = new Point(1, 2);
Point p2 = new Point(1, 2);
boolean eq = (p1 == p2); // true — value comparison, not identity
```

**Migration Tip**: This is a major release. Start upgrading as soon as library compatibility is verified.  
**Company Focus**: All enterprises — this is the next LTS.

---

## Java 26 (March 2026)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Value Objects (2nd preview)** — API refinements
- **Universal Generics (continued preview)** — generics over primitives
- **AOT compilation (continued preview)** — Leyden optimizations
- **Assortative Matching and Pattern Composition (preview)** — advanced pattern matching
- **Self-referential pattern variables (preview)**
- **Stack-cached Scoped Values** — performance improvements
- **Continued GC improvements** (ZGC + G1 optimizations)
- **Enhanced AOT class loading**
- **Virtual thread scheduling improvements** (work-stealing refinements)
- **String interning improvements**
- **Arithmetic improvements** (vectorized math in standard library)

**Interview Relevance**: Medium  
**Why**: Value objects and universal generics are still incubating but represent Java's future direction.  
**Sample Interview Question**:  
Q: "What is universal generics and why is it significant?"  
A: Universal Generics (Valhalla) allow generics over primitive types: `List<int>`, `Map<String, double>`. Currently, generics only work with reference types, forcing autoboxing over primitives (performance and memory overhead). Universal generics work with value types from Valhalla to provide the full benefits of generics without boxing.

```java
// Universal Generics (preview)
ArrayList<int> numbers = new ArrayList<>();
numbers.add(42);
int x = numbers.get(0); // no boxing! no cast needed.
```

**Migration Tip**: Monitor library support for Valhalla types. This fundamentally changes how collections work.  
**Company Focus**: Performance-critical applications, data science, big data.

---

## Java 27 (September 2026)
**Codename**: (none)  
**LTS**: No  
**Key Features**:
- **Value Objects (standard)** — finalized after preview rounds
- **Universal Generics (standard)** — finalized
- **Exhaustive Switch for value types** — complete pattern matching support
- **AOT Compilation (standard)** — Leyden finalization, near-instant startup
- **Pattern Composition (standard)** — complex pattern matching
- **StructuredTaskScope enhancements** — cancel-and-ignore, resource-scoped tasks
- **Automatic Virtual Thread pinning detection** — JVM warns when virtual thread blocks carrier
- **Concurrent GC as default** (ZGC generational default)
- **Enhanced Foreign Function calls** — improved C/C++ interop
- **Memory safety improvements for Unsafe removal path**
- **Project Leyden AOT default** for java.base module
- **Developer experience improvements** (better error messages, faster compilation)
- **JDK source code uses value types internally** (self-hosting optimization)

**Interview Relevance**: Very High — latest version, shows you stay current  
**Why**: Value objects and universal generics final — Java fundamentally changed.  
**Sample Interview Question**:  
Q: "How has Java changed fundamentally from Java 8 to Java 27?"  
A: Java 27 is nearly a different language from Java 8 while maintaining full backward compatibility. Key shifts: (1) Lambdas/streams to declarative data processing. (2) Modules for strong encapsulation. (3) Records and sealed classes for concise, safe data modeling. (4) Pattern matching across switch, instanceof, and records for expressive destructuring. (5) Virtual threads and structured concurrency for scalable concurrency. (6) Value objects and universal generics for zero-cost abstractions. (7) AOT compilation for startup performance. The JVM is more optimized (ZGC, generational collectors), and the language has absorbed ideas from Scala, Kotlin, and Haskell.

Q: "What's your experience with Java 27's value types in production?"  
A: [Personal answer — but demonstrate understanding:] Value types eliminated boxing overhead in our high-throughput trading system. We replaced `double[]` with `List<double>` using universal generics, reducing memory by 40% and improving cache locality. The transition was smooth because JDK collections were retrofitted.

**Migration Tip**:  
- Plan migration from Java 25 (LTS) or Java 21 to Java 27 within the next cycle  
- Audit code for raw types and enable compilation with -Xlint:rawtypes  
- Evaluate value objects for data-heavy components  
- Test virtual thread workloads with the new pinning detection  

**Company Focus**: Early adopters, startups, companies that pride themselves on using the latest Java.
