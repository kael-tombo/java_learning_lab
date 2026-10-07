# JVM Interview Guide — Deep Preparation

> **Master the JVM for FAANG-level interviews**
> Covers: Class loading, bytecode, JIT, GC, memory model, profiling, tuning, Java 21+

---

## Table of Contents
1. [Class Loading Mechanism](#class-loading-mechanism)
2. [Bytecode Instruction Set](#bytecode-instruction-set)
3. [JIT Compilation](#jit-compilation)
4. [GC Algorithms](#gc-algorithms)
5. [Memory Model](#memory-model)
6. [Profiling & Observability](#profiling--observability)
7. [Performance Tuning](#performance-tuning)
8. [Java 21+ JVM Features](#java-21-jvm-features)
9. [Interview Questions by Level](#interview-questions-by-level)

---

## Class Loading Mechanism

### Three Built-in Class Loaders

| Class Loader | Loads From | Key Property |
|-------------|------------|--------------|
| **Bootstrap** | `rt.jar`, `java.base` (Java 9+) | Native implementation (C++), no parent |
| **Extension / Platform** | `lib/ext` (Java 8) / `java.base` module (Java 9+) | Parent: Bootstrap |
| **Application / System** | Classpath (`-cp`), module path | Parent: Platform |

### Delegation Model

```
Request to load class
        ↓
Application ClassLoader
        ↓  (delegates to parent)
Platform ClassLoader
        ↓  (delegates to parent)
Bootstrap ClassLoader
        ↓  (tries to load)
    [class found?] → return
        ↓
Platform ClassLoader tries to load
    [class found?] → return
        ↓
Application ClassLoader tries to load
    [class found?] → return
        ↓
ClassNotFoundException
```

**Key Rules**:
- Parent-first delegation ensures core Java classes are never replaced
- Visible classes: child can see parent's classes, parent cannot see child's
- Classes loaded by different class loaders are different types (even from same .class file)

### Custom Class Loaders

```java
public class CustomClassLoader extends ClassLoader {
    @Override
    public Class<?> findClass(String name) throws ClassNotFoundException {
        byte[] classBytes = loadClassFromCustomSource(name);
        return defineClass(name, classBytes, 0, classBytes.length);
    }
}
```

**Use Cases**:
- Plugin systems (Eclipse, IntelliJ, Tomcat)
- Dynamic code reloading (development servers)
- Encrypted class files (security)
- Bytecode manipulation at load time (AOP, instrumentation)

**Common Mistakes**:
- Breaking the delegation model by overriding `loadClass()` instead of `findClass()`
- Memory leaks: each loaded class is pinned by its ClassLoader
- PermGen/Metaspace: each ClassLoader creates metadata that lives until ClassLoader is GC'd

### Class Linking — Three Phases

1. **Verification**: Checks .class file structure (magic number 0xCAFEBABE, version, constant pool integrity)
2. **Preparation**: Allocates static fields with default values (not initialized yet)
3. **Resolution**: Resolves symbolic references to direct references (may be deferred until use)

### Class Initialization

- Static initializers run in order
- Triggered by: `new`, `getstatic`, `putstatic`, `invokestatic`, `Class.forName()`
- Not triggered by: accessing compile-time constants (`static final` primitives/Strings)

**Interview Question**:
> *"What happens when you call `Class.forName("com.example.Driver")`? Walk through loading, linking, and initialization. What if you use `Class.forName("com.example.Driver", false, classLoader)`?"*

---

## Bytecode Instruction Set

### Stack-Based Architecture

The JVM is a stack-based machine (not register-based). Each frame has:
- **Local variable array** (indexed from 0 — `this` for instance methods)
- **Operand stack** (push/pop for computations)
- **Frame data** (constant pool resolution, exception table)

### Key Instruction Categories

| Category | Instructions | Purpose |
|----------|-------------|---------|
| Load/Store | `iload`, `aload`, `istore`, `astore`, `ldc` | Move data between locals and stack |
| Arithmetic | `iadd`, `isub`, `imul`, `idiv`, `irem`, `iinc` | ALU operations |
| Object | `new`, `getfield`, `putfield`, `getstatic`, `putstatic`, `instanceof`, `checkcast` | Object creation and field access |
| Array | `newarray`, `anewarray`, `arraylength`, `iaload`, `iastore` | Array operations |
| Control Flow | `ifeq`, `ifne`, `if_icmpeq`, `goto`, `tableswitch`, `lookupswitch` | Branching and switching |
| Method Invocation | `invokevirtual`, `invokespecial`, `invokestatic`, `invokeinterface`, `invokedynamic` | Method dispatch |
| Return | `ireturn`, `areturn`, `return` | Return from methods |
| Synchronization | `monitorenter`, `monitorexit` | Thread synchronization |
| Exception | `athrow` | Throw exceptions |

### Method Invocation Deep Dive

| Instruction | Dispatch | Examples |
|-------------|----------|----------|
| `invokevirtual` | Virtual dispatch (vtable lookup) | `obj.method()` — most instance methods |
| `invokespecial` | Non-virtual / compile-time | `<init>`, `super.method()`, `private` methods |
| `invokestatic` | Static (no receiver) | `Class.staticMethod()` |
| `invokeinterface` | Interface dispatch (itable lookup) | `interface.method()` |
| `invokedynamic` | Bootstrap method (JSR 292) | Lambdas, string concatenation, dynamic languages |

**invokedynamic (Java 7+)**: The most complex invocation instruction.
- Bootstrap method returns a CallSite (with MethodHandle)
- Enables lambda expressions: `() -> System.out.println()` → `invokedynamic` with `LambdaMetafactory`
- Enables dynamic languages on JVM (JRuby, Jython, Nashorn/GraalVM)

### Bytecode for Common Java Constructs

```java
// Source: String s = "hello" + name;
// Compiled to:
// NEW java/lang/StringBuilder
// DUP
// INVOKESPECIAL java/lang/StringBuilder.<init>()V
// LDC "hello"
// INVOKEVIRTUAL java/lang/StringBuilder.append(Ljava/lang/String;)Ljava/lang/StringBuilder;
// ALOAD name
// INVOKEVIRTUAL java/lang/StringBuilder.append(Ljava/lang/String;)Ljava/lang/StringBuilder;
// INVOKEVIRTUAL java/lang/StringBuilder.toString()Ljava/lang/String;
// ASTORE s

// Source: switch(value) { case 1: ...; case 1000: ... }
// Compiled to: LOOKUPSWITCH (sparse values need search)

// Source: switch(value) { case 1: ...; case 2: ...; case 3: ... }
// Compiled to: TABLESWITCH (dense values get O(1) jump table)
```

---

## JIT Compilation

### C1 vs C2 Compiler

| Aspect | C1 (Client) | C2 (Server) |
|--------|-------------|-------------|
| Optimization Level | Moderate | Aggressive |
| Compilation Speed | Fast | Slow |
| Code Quality | Good | Excellent |
| Typical Use | Short-lived apps, GUI | Long-running servers |
| Threshold | Default: 1500 invocations | Default: 10000 invocations |

### Tiered Compilation (Default since Java 7)

```
Level 0: Interpreter
Level 1: Simple C1 (no profiling)
Level 2: Limited C1 (minor profiling)
Level 3: Full C1 (full profiling)
Level 4: C2 (aggressive — uses profiling from Level 3)
```

**Tier Progression**:
- Hot methods: 0 → 3 → 4 (interpreter → profiling C1 → optimized C2)
- Trivial methods: 0 → 1 → 4 (skip profiling, go straight to simple C1 then C2)
- Methods that become less hot: may deoptimize C2 → C1

### Key JIT Optimizations

| Optimization | Description | Example |
|-------------|-------------|---------|
| **Method Inlining** | Replaces call site with method body | `getX()` → just read the field |
| **Escape Analysis** | Determines if object escapes scope | Stack allocation, scalar replacement |
| **Lock Elision** | Removes unnecessary locks | Single-threaded `StringBuffer` |
| **Lock Coarsening** | Merges adjacent locks | Multiple synchronized calls merged |
| **Biased Locking** | Optimizes for single-thread access | First thread gets bias |
| **Loop Unrolling** | Repeats loop body to reduce branch overhead | |
| **Null Check Elimination** | Removes redundant null checks | |
| **Range Check Elimination** | Removes array bounds checks | |
| **Common Subexpression Elimination** | Recomputes shared values | |
| **Dead Code Elimination** | Removes unreachable code | |

### Escape Analysis Deep Dive

```java
int sum() {
    Point p = new Point(1, 2);  // Does 'p' escape?
    return p.x + p.y;
}
```

If `p` doesn't escape:
1. **Stack allocation**: Object allocated on stack (no GC pressure)
2. **Scalar replacement**: Fields `x` and `y` stored in registers
3. **Lock elision**: Synchronized methods on non-escaping objects lose locks

**Limitations**:
- Only works for non-escaping objects
- Limited by analysis scope (method boundaries)
- Requires C2 compilation
- Arrays are rarely stack-allocated

### Inlining Decisions

```java
// Candidate for inlining (small, hot)
int getX() { return x; }

// Not inlined (large, complex)
void complexOperation() { ... 1000 lines ... }
```

**JVM Flags**:
- `-XX:MaxInlineSize=35` (default: 35 bytes of bytecode)
- `-XX:FreqInlineSize=325` (default: 325 bytes for hot methods)
- `-XX:InlineSmallCode=1000` (default: 1000 bytes of native code)
- `-XX:+PrintInlining` (see what got inlined)

---

## GC Algorithms

### Quick Comparison

| GC | Java Version | Focus | Heap Size | Pause Time | Throughput |
|----|-------------|-------|-----------|------------|------------|
| Serial | 1.2+ | Single-thread, small heaps | <100MB | Long (STW) | Low |
| Parallel | 1.4+ | Throughput, multi-thread | 1-8GB | Long (STW) | Highest |
| CMS | 1.5-14 (deprecated) | Low latency | 2-16GB | Short (concurrent) | Moderate |
| G1 | 7+ (default 9+) | Balanced, large heaps | 1-100GB | Configurable | Good |
| ZGC | 11+ (production 15+) | Ultra-low latency | 8MB-16TB | <1ms (any heap) | Good |
| Shenandoah | 12+ (backport to 11) | Ultra-low latency | 100MB-2TB | <10ms | Moderate |

### G1 Garbage Collector (Default since Java 9)

**Heap Layout**: Heap divided into ~2048 regions (1-32MB each). Regions are Eden, Survivor, Old, or Humongous (>50% region size).

**Phases**:
1. **Young GC** (STW but fast): Copy live objects from Eden to Survivor/Old
2. **Concurrent Marking** (concurrent): Identify reachable objects across heap
3. **Mixed GC** (STW, incremental): Evacuate selected old-gen regions
4. **Full GC** (STW, fallback): Serial compaction when concurrent collection fails

**Tuning**:
```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200        # Target pause time (default: 200ms)
-XX:G1HeapRegionSize=4m          # Region size (1-32MB)
-XX:G1NewSizePercent=5           # Initial young gen (% of heap)
-XX:G1MaxNewSizePercent=60       # Max young gen (% of heap)
-XX:+UnlockExperimentalVMOptions -XX:G1MixedGCLiveThresholdPercent=85
```

### ZGC (JDK 15+ Production)

**Core Innovation**: Colored pointers — 42-bit address space with metadata bits in pointer.

```
Object Pointer: [62-44: metadata bits] [43-0: address]
                - Finalizable bit
                - Remapped bit
                - Marked0 / Marked1 bit (alternating between GC cycles)
```

**Phases** (All concurrent except initial mark):
1. **Pause Mark Start** (STW, short): Identify GC roots
2. **Concurrent Mark/Trace** (concurrent): Traverse object graph
3. **Pause Mark End** (STW, short): Process weak references
4. **Concurrent Prepare Relocation** (concurrent): Find fragmented regions
5. **Pause Relocate Start** (STW, short): Relocate roots
6. **Concurrent Relocate** (concurrent): Relocate objects, remap pointers

**Tuning**:
```bash
-XX:+UseZGC
-XX:ConcGCThreads=2         # Concurrent threads
-XX:ParallelGCThreads=6     # Parallel threads
-Xmx=32g                    # Heap size
-XX:SoftMaxHeapSize=28g     # Soft max (ZGC prefers GC before hitting Xmx)
```

### Shenandoah (JDK 12+)

**Core Innovation**: Brooks forwarding pointer — each object has an extra pointer field for forwarding.

```
Object Header: [mark word] [klass pointer] [forwarding pointer] [fields...]
```

**Phases**:
1. **Init Mark** (STW): Roots marking
2. **Concurrent Mark** (concurrent): Traverse graph
3. **Final Mark** (STW): Finish marking, evacuate planning
4. **Concurrent Evacuation** (concurrent): Copy objects
5. **Init Update Refs** (STW): Prepare reference update
6. **Concurrent Update Refs** (concurrent): Update all references
7. **Final Update Refs** (STW): Finalize

**Tuning**:
```bash
-XX:+UseShenandoahGC
-XX:ShenandoahGCMode=iu     # Interval update (lower pause, lower throughput)
-XX:ShenandoahUncommitDelay=1000  # Uncommit heap memory after 1s idle
```

### When to Use Each GC

| Scenario | Recommended GC | Reason |
|----------|---------------|--------|
| Batch processing, 8GB heap | Parallel | Max throughput |
| Web service, 16GB heap, 200ms SLA | G1 | Balanced, predictable |
| Trading system, 64GB heap, <1ms SLA | ZGC | Sub-millisecond pauses |
| Interactive app, 4GB heap, 10ms SLA | Shenandoah | Concurrent evacuation |
| Microservice, 256MB heap, fast startup | Serial/G1 | Small footprint |
| Big data (Spark), 512GB heap | G1 or ZGC | Large heap handling |

---

## Memory Model

### The Java Memory Model (JLS §17.4)

The JMM defines when one thread's writes are visible to another thread. It doesn't specify the actual memory architecture — it defines legal behaviors.

**Key Concept**: If two operations are not ordered by happens-before, the JVM is free to reorder them.

### Happens-Before Rules

| Rule | Description |
|------|-------------|
| **Program Order Rule** | Each action in a thread happens-before every later action in that thread. |
| **Monitor Lock Rule** | Unlock on a monitor happens-before every subsequent lock on that same monitor. |
| **Volatile Variable Rule** | Write to a volatile field happens-before every subsequent read of that field. |
| **Thread Start Rule** | `Thread.start()` happens-before any action in the started thread. |
| **Thread Join Rule** | Last action in a thread happens-before `Thread.join()` returns. |
| **Transitivity** | If A happens-before B and B happens-before C, then A happens-before C. |
| **Interruption Rule** | `interrupt()` happens-before detection of interruption. |
| **Finalizer Rule** | Constructor finishes happens-before finalizer starts. |

### Volatile Semantics

```java
volatile boolean flag = false;

// Thread 1:
data = 42;        // normal write
flag = true;      // volatile write (store barrier — flush all writes)

// Thread 2:
if (flag) {       // volatile read (load barrier — invalidate cache)
    System.out.println(data);  // guaranteed to see 42
}
```

**Memory Barrier Insertion**:
- On x86: volatile reads are essentially free (no barrier needed for reads with StoreLoad)
- On ARM: volatile reads/writes need DMB (Data Memory Barrier)
- `VarHandle` provides finer-grained barriers: `acquireFence()`, `releaseFence()`, `fullFence()`

### Final Field Semantics

```java
class ImmutableObject {
    private final int x;
    private static ImmutableObject instance;
    
    ImmutableObject(int x) { this.x = x; }
    
    static void init(int x) { instance = new ImmutableObject(x); }
    static int getX() { return instance.x; }
}
```

**JMM Guarantees**: 
- A thread that sees a reference to an object with a `final` field is guaranteed to see the correctly constructed value of that field (even without synchronization)
- This is achieved by a `store-store` barrier after the constructor's final field stores
- Only works if the object reference doesn't escape the constructor (no `this` reference leak)

### Synchronized Block Semantics

```java
synchronized (lock) {
    // Critical section
    // On entry: acquire monitor (load barrier)
    // On exit: release monitor (store barrier)
}
```

- Compiled to `monitorenter` / `monitorexit` bytecodes
- **Biased Locking**: First thread to acquire lock gets "biased" — subsequent acquires are CAS-free
- **Thin Locking**: Contended lock uses CAS to set lock word
- **Heavy Locking**: OS mutex/pthread lock when contention persists

### JMM and Reordering

| Type | Load-Load | Load-Store | Store-Load | Store-Store |
|------|-----------|------------|------------|-------------|
| x86 | No | No | Yes (only type) | No |
| ARM | Yes | Yes | Yes | Yes |
| JMM (required) | Yes | Yes | Yes | Yes |

The JVM inserts barriers as needed for the target architecture. x86 is strong: only Store-Load reordering is observable. ARM is weak: all reorderings possible.

---

## Profiling & Observability

### JDK Flight Recorder (JFR)

**Event-Driven Profiling**: Built into HotSpot, very low overhead (<1%)

**Key Events**:
- `jdk.GarbageCollection` — GC pause duration, cause, heap sizes
- `jdk.AllocationRequiringGC` — TLAB allocation causing GC
- `jdk.JavaMonitorEnter` — Thread waiting on monitor
- `jdk.ThreadPark` — Thread parking
- `jdk.ClassLoading` — Class loading events
- `jdk.ExecutionSample` — Stack traces for CPU profiling
- `jdk.ActiveRecording` — Recording metadata

**Usage**:
```bash
# Record for 60 seconds
jcmd <pid> JFR.start name=profile duration=60s filename=profile.jfr

# Or with Java flags
-XX:StartFlightRecording=name=profile,duration=60s,filename=profile.jfr
```

### JDK Mission Control (JMC)

GUI tool for analyzing JFR recordings. Key views:
- **Memory**: GC pauses, heap usage by region, allocation rate (TLAB)
- **Threads**: Thread states, lock contention, thread dumps at safepoints
- **Code**: Hot methods, compilation queue, inlining decisions
- **Events**: Custom event browser and analysis

### async-profiler

Low-overhead sampling profiler using `perf_events` (Linux) or `perf` API on macOS.
```bash
# CPU profiling
./profiler.sh -e cpu -d 30 -f profile.html <pid>

# Allocation profiling
./profiler.sh -e alloc -d 30 -f alloc.html <pid>

# Wall-clock profiling (for IO-bound)
./profiler.sh -e wall -d 30 -f wall.html <pid>
```

### JMH (Java Microbenchmark Harness)

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@State(Scope.Thread)
@Fork(value = 2, warmups = 1)
public class MyBenchmark {
    
    @Param({"10", "100", "1000"})
    private int size;
    
    private List<Integer> list;
    
    @Setup
    public void setup() {
        list = new ArrayList<>(size);
        for (int i = 0; i < size; i++) list.add(i);
    }
    
    @Benchmark
    public int sumWithStream() {
        return list.stream().mapToInt(Integer::intValue).sum();
    }
    
    @Benchmark
    public int sumWithLoop() {
        int sum = 0;
        for (int v : list) sum += v;
        return sum;
    }
}
```

**Important**: Warmup, fork count, blackholes, dead code elimination — JMH handles these. Never write manual benchmarks.

### Heap Dump Analysis (Eclipse MAT)

```bash
# Trigger heap dump
jcmd <pid> GC.heap_dump /path/to/dump.hprof
jmap -dump:live,file=/path/to/dump.hprof <pid>

# In Eclipse MAT:
# - Leak Suspects Report → Most likely memory leak
# - Dominator Tree → Largest objects by retained heap
# - OQL → SQL-like queries: "SELECT * FROM java.lang.String s WHERE s.value.length > 1000"
```

---

## Performance Tuning

### Essential JVM Flags

```bash
# Heap sizing
-Xms8g                           # Initial heap (start here, avoid resizing)
-Xmx8g                           # Max heap (same as Xms for production)
-XX:MetaspaceSize=256m           # Initial metaspace (avoid GC-triggered resize)
-XX:MaxMetaspaceSize=256m        # Max metaspace

# GC selection
-XX:+UseG1GC                     # Default since Java 9
-XX:+UseZGC                      # Low-latency (Java 15+)
-XX:+UseShenandoahGC             # Low-latency (Java 12+)
-XX:+UseParallelGC               # High throughput

# GC logging (Java 9+ unified logging)
-Xlog:gc*:file=gc.log:time,level,tags
-Xlog:gc+ergo*=trace            # Verbose ergonomics
-Xlog:gc+age=trace              # Age table
-Xlog:gc+phases=trace           # Phase timing

# Code cache
-XX:ReservedCodeCacheSize=256m   # Avoid code cache full warning
-XX:+PrintCodeCache              # Monitor code cache usage

# JIT logging
-XX:+PrintCompilation            # Print compilation events
-XX:+PrintInlining               # Print inlining decisions
-XX:+UnlockDiagnosticVMOptions -XX:+LogCompilation

# OOM / diagnostics
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/path/to/dumps/
-XX:+ExitOnOutOfMemoryError      # Exit on OOM (for container environments)
-XX:+CrashOnOutOfMemoryError     # Generate crash file
```

### GC Log Analysis (Java 9+ Unified Logging)

```
[2024-03-15T10:30:00.123+0000][info][gc,start] GC(1) Pause Young (Normal) (G1 Evacuation Pause)
[2024-03-15T10:30:00.456+0000][info][gc,phases] GC(1)   Pre Evacuate Collection Set: 0.5ms
[2024-03-15T10:30:00.789+0000][info][gc,phases] GC(1)   Evacuate Collection Set: 245.3ms
[2024-03-15T10:30:00.790+0000][info][gc,phases] GC(1)   Post Evacuate Collection Set: 5.2ms
[2024-03-15T10:30:00.790+0000][info][gc] GC(1) Pause Young (Normal) (G1 Evap) 2048M->512M(8192M) 251.0ms
```

**Key Metrics**:
- **Pause duration**: 251ms → Should be below target (default 200ms)
- **Heap before → after**: 2048M → 512M (75% garbage, healthy)
- **Evacuation time**: 245ms → Dominant phase, consider larger region size
- **Trigger**: Allocation failure in Eden

### String Deduplication (G1)

```bash
-XX:+UseStringDeduplication  # G1 only — default: disabled
```

Deduplicates String `char[]` backend arrays that have identical content. Benefits:
- Applications with many duplicate strings (caches, JSON keys)
- Can reduce heap usage by 10-30%
- Minor CPU overhead during GC

### Class Data Sharing (CDS)

```bash
# Create archive
java -Xshare:dump -XX:SharedArchiveFile=app.jsa -cp app.jar

# Use archive
java -Xshare:auto -XX:SharedArchiveFile=app.jsa -jar app.jar
```

- Pre-loads class metadata to improve startup time
- AppCDS (Application CDS, Java 10+) archives application classes
- Significant for microservices (50% faster startup reported)

---

## Java 21+ JVM Features

### Virtual Threads (Project Loom, JEP 444)

**JVM Implementation**:
- Virtual threads are not OS threads — they're Java objects managed by the JVM
- Each virtual thread is mounted on a **carrier thread** (platform thread from `ForkJoinPool`)
- When virtual thread blocks (I/O, `park()`), it unmounts from carrier — carrier continues
- Deep stack: virtual threads can have millions of frames (growable stack)
- **Pinning**: If virtual thread performs blocking operation while holding a monitor, it pins to carrier

**JVM Changes in Java 21**:
- `java.lang.VirtualThread` — new class in JDK
- `ForkJoinPool` modification: new `ForkJoinPool` for virtual thread scheduling (FIFO mode)
- `java.io` changes: `InputStream`/`OutputStream` readers/writers are interruptible for virtual threads
- Stack introspection: `StackWalker` works with virtual thread stacks

### Structured Concurrency (JEP 453 — Preview in 21)

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> user = scope.fork(() -> fetchUser(id));
    Future<Integer> order = scope.fork(() -> fetchOrder(id));
    scope.join();           // Waits for both, or shuts down if one fails
    scope.throwIfFailed();  // Propagates exceptions
    return new Response(user.resultNow(), order.resultNow());
}
```

**JVM Support**: Structured concurrency ensures:
- If a subtask fails, all other subtasks are cancelled
- No thread leakage — all subtasks complete before scope closes
- Clear error propagation

### Scoped Values (JEP 446 — Preview in 21; incubator in 20 as JEP 429; final in 25 as JEP 506)

Replacement for `ThreadLocal` that works with virtual threads:
```java
private static final ScopedValue<String> USER = ScopedValue.newInstance();

// Parent
ScopedValue.where(USER, "alice").run(() -> handleRequest());

// Child (can see parent's scoped value)
String user = USER.get();  // "alice" — immutable, no mutation
```

**JVM Implementation**:
- Scoped values are stored in the call stack (not in ThreadLocal map)
- No per-thread map lookup — faster than ThreadLocal
- Immutable by design — can't call `.set()`
- Works correctly with virtual threads (no pinning, no inheritance issues)

### Pattern Matching (JEP 441, 443, 440)

**JVM Level**: `instanceof` with pattern matching and `switch` with patterns require changes to:
- `tableswitch`/`lookupswitch` bytecode for type patterns
- `invokedynamic` to implement pattern matching efficiently
- `Record` pattern matching uses `getComponent` via `invokedynamic`

```java
// Compiled using invokedynamic for efficient type checking
if (obj instanceof String s && s.length() > 5) {
    System.out.println(s.toUpperCase());
}

// Switch on type patterns — compiled with invokedynamic
return switch (obj) {
    case String s -> s.length();
    case Integer i -> i;
    case null -> -1;
    default -> 0;
};
```

---

## Interview Questions by Level

### Junior (0-2 years)

1. "What is the difference between JDK, JRE, and JVM?"
2. "How does Java achieve platform independence?"
3. "What is the difference between stack and heap memory?"
4. "Explain the garbage collection process in simple terms."
5. "What is a class loader? What are the three built-in class loaders?"
6. "What happens when you call `new MyClass()`?"
7. "What is a JIT compiler?"
8. "Explain the difference between `==` and `.equals()` in terms of memory."
9. "What is a stack trace and how do you read it?"
10. "What is the `static` keyword? How does it affect memory allocation?"

### Mid-Level (3-5 years)

1. "Explain the class loading delegation model. Why is it used?"
2. "Describe the JVM memory areas (heap, stack, metaspace, code cache, etc.)."
3. "How does the JIT compiler decide which methods to compile?"
4. "What is the difference between G1 and Parallel GC?"
5. "Explain `volatile` in terms of the Java Memory Model."
6. "What is a safepoint? When does it occur?"
7. "How does `synchronized` work at the JVM level?"
8. "What is a memory leak in Java? How do you detect one?"
9. "Explain tiered compilation and the levels involved."
10. "What is a biased lock? When is it beneficial?"

### Senior (5-8 years)

1. "Walk through the class linking process: verification, preparation, resolution."
2. "Explain the difference between `invokevirtual`, `invokespecial`, `invokeinterface`, and `invokedynamic`."
3. "How does ZGC achieve sub-millisecond pause times? Explain colored pointers."
4. "Describe the Shenandoah GC algorithm. How does Brooks forwarding pointer work?"
5. "Explain the happens-before relationship with all 8 rules. Give concrete examples."
6. "How does escape analysis enable stack allocation and lock elision? What are the limitations?"
7. "Design a monitoring system using JFR. What events would you track for latency issues?"
8. "How would you tune G1 for a 64GB heap with a 100ms pause target?"
9. "Explain how virtual threads are implemented in the JVM. What is pinning?"
10. "How would you diagnose a production OutOfMemoryError? Walk through the complete process."

### Staff (8+ years)

1. "Compare G1, ZGC, and Shenandoah at the implementation level. How does each handle concurrent relocation?"
2. "Design a JIT compiler. What optimizations would you prioritize and why?"
3. "Explain the complete virtual thread JVM implementation. How does continuations work in HotSpot?"
4. "How would you modify the JVM to support a new GC algorithm? What interfaces would you implement?"
5. "What changes would you make to the JMM to better support modern hardware (ARM, NUMA, CXL)?"
6. "Design a zero-overhead profiling system for production. How do you minimize safepoint bias?"
7. "Explain the GraalVM compilation pipeline. How does it differ from C2?"
8. "How does CDS work at the JVM level? How would you improve it for microservices?"
9. "Design a thread pool that works efficiently with both platform and virtual threads."
10. "How would you implement `ScopedValue` at the JVM level? What are the performance implications?"

### Principal / Distinguished (12+ years)

1. "You're designing a new JVM for a post-Moore's-law world. What architecture choices do you make?"
2. "Design a GC that can handle 10TB heaps with <100ms pauses on commodity hardware."
3. "How would you redesign the JMM for a future with non-volatile memory (PMEM) and CXL?"
4. "Design a language feature that requires new bytecodes and JVM changes. Walk through JEP process."
5. "How would you eliminate the performance gap between Java and C++ for HFT applications?"
6. "Design a profile-guided optimization system for a microservice deployment (not just monolithic JVMs)."
7. "How would you redesign class loading for a module system that works at cloud scale?"
8. "Design a debugging API that works correctly with virtual threads, structured concurrency, and continuations."
9. "Propose changes to HotSpot to better support AI/ML workloads (tensors, GPU offload, etc.)."
10. "How would you build a polyglot VM that maintains Java performance while supporting dynamic languages?"

---

## Common JVM Pitfalls in Interviews

1. **Conflating spec vs implementation**: "The JVM does X" — actually, the spec allows it, but HotSpot does Y
2. **Assuming all GCs are the same**: Stop saying "the garbage collector" — be specific
3. **Forgetting Java 9+ changes**: Module system removed `rt.jar`, unified logging changed GC flags
4. **Memory model confusion**: "volatile is about caching" — no, it's about the happens-before guarantee
5. **JIT over-mystification**: "The JIT optimizes everything" — no, it only compiles hot methods and has limits
6. **Outdated knowledge**: CMS was deprecated in Java 9, removed in Java 14. Biased locking deprecated in Java 15 for some GCs
7. **ClassLoaderLeak**: "Unloading classes is impossible" — possible, but requires ClassLoader garbage collection
8. **Safepoint ignorance**: Many profiling tools are biased toward safepoints — you're not seeing true runtime

---

## Interview Response Framework

When asked a JVM question, structure your answer:

1. **Define the concept** — What is it in one sentence?
2. **How it works** — Step-by-step mechanical explanation
3. **Why it matters** — Practical implications
4. **Trade-offs** — What's gained vs sacrificed
5. **Example** — Concrete scenario or code
6. **JVM specific** — How HotSpot implements it
7. **Tuning** — How to observe/configure it

---

> *"The JVM is not magic. It's a carefully engineered piece of software with well-defined behaviors. Know the spec, understand the implementation, and you can reason about any Java program."*
