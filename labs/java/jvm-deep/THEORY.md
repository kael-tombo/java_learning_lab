# THEORY — JVM Deep Dive

## Overview

Comprehensive coverage of JVM internals: class loading, bytecode, JIT compilation, garbage collection, and performance tuning.

---

## JVM Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      JVM Process                             │
├─────────────────────────────────────────────────────────────┤
│  Class Loader Subsystem                                     │
│  ├── Bootstrap ClassLoader (native)                         │
│  ├── Platform ClassLoader                                   │
│  └── Application ClassLoader                                │
├─────────────────────────────────────────────────────────────┤
│  Runtime Data Areas                                         │
│  ├── Heap (shared) ── Young Gen (Eden, S0, S1) + Old Gen   │
│  ├── Metaspace (shared, native) ── Class metadata          │
│  ├── Thread Stacks (per-thread) ── Frames, locals, ops     │
│  ├── PC Register (per-thread)                               │
│  └── Native Method Stack (per-thread)                       │
├─────────────────────────────────────────────────────────────┤
│  Execution Engine                                           │
│  ├── Interpreter                                            │
│  ├── JIT Compiler (C1/C2)                                   │
│  └── GC Threads                                             │
├─────────────────────────────────────────────────────────────┤
│  Native Interface (JNI)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Class Loading

### Delegation Model

```
Bootstrap (rt.jar, jmods)
    ↓ delegates to
Platform (extension modules)
    ↓ delegates to
Application (classpath, modulepath)
    ↓ delegates to
Custom ClassLoaders
```

### ClassLoader API

```java
// Custom classloader
public class PluginLoader extends ClassLoader {
    public PluginLoader(ClassLoader parent) {
        super(parent);
    }
    
    @Override
    protected Class<?> findClass(String name) {
        byte[] bytes = loadFromPlugin(name);
        return defineClass(name, bytes, 0, bytes.length);
    }
}

// Module-aware loading (Java 9+)
ClassLoader loader = ClassLoader.getPlatformClassLoader();
ModuleLayer layer = ModuleLayer.boot();
```

### Class Loading Phases

1. **Loading** - Find binary, create Class object
2. **Linking**
   - Verification - bytecode validity
   - Preparation - allocate static fields, default values
   - Resolution - symbolic refs → direct refs
3. **Initialization** - `<clinit>`, static initializers

---

## Bytecode Fundamentals

### Stack-Based Execution

```java
// Java
int add(int a, int b) { return a + b; }

// Bytecode
int add(int, int);
  Code:
   0: iload_1        // load local 1 (a)
   1: iload_2        // load local 2 (b)
   2: iadd           // integer add
   3: ireturn        // return int
```

### Instruction Categories

| Prefix | Types | Examples |
|--------|-------|----------|
| `i` | int | `iload`, `iadd`, `istore` |
| `l` | long | `lload`, `ladd` |
| `f` | float | `fload`, `fadd` |
| `d` | double | `dload`, `dadd` |
| `a` | reference | `aload`, `astore` |
| (none) | multi | `nop`, `dup`, `swap` |

### Constant Pool

```java
// Symbolic references resolved at linking
ConstantPool:
  #1 = Methodref  #10.#20  // java/lang/Object."<init>":()V
  #2 = Fieldref   #11.#21  // MyClass.field:I
  #3 = String     #22      // "hello"
  #4 = Class      #23      // MyClass
  #5 = Utf8       field
  #6 = Utf8       I
```

---

## JIT Compilation

### Tiered Compilation (Default)

```
Tier 0: Interpreter (profiling)
    ↓
Tier 1: C1 (Client) - simple optimizations
    ↓
Tier 2: C1 + profiling
    ↓
Tier 3: C2 (Server) - aggressive optimizations
    ↓
Tier 4: C2 + profiling
```

### Compiler Flags

```bash
# Disable tiered
-XX:-TieredCompilation

# Compile threshold
-XX:CompileThreshold=10000      # C2
-XX:Tier3CompileThreshold=200   # C1

# Code cache
-XX:InitialCodeCacheSize=16m
-XX:ReservedCodeCacheSize=256m

# Print compilation
-XX:+PrintCompilation
-XX:+PrintInlining
```

### Key Optimizations

| Optimization | Description |
|--------------|-------------|
| Inlining | Replace call with body |
| Escape Analysis | Stack allocation, lock elision |
| Loop Unrolling | Reduce branch overhead |
| Dead Code Elimination | Remove unreachable code |
| Constant Folding | Compute at compile time |
| Devirtualization | Convert virtual to direct call |
| Scalar Replacement | Break objects into fields |

### Deoptimization

```bash
# Causes: class loading, uncommon traps, OSR
-XX:+PrintDeoptimizationDetails
-XX:+UnlockDiagnosticVMOptions
```

---

## Garbage Collection

### Generational Hypothesis

- **Young Gen**: Most objects die young
- **Old Gen**: Long-lived objects
- **Metaspace**: Class metadata (native)

### GC Algorithms

| Collector | Type | Heap | Latency | Throughput |
|-----------|------|------|---------|------------|
| Serial | Stop-the-world | Small | High | Low |
| Parallel | Stop-the-world | Medium | Medium | High |
| G1 | Concurrent + STW | Large | Low | Medium |
| ZGC | Concurrent | Very Large | **Very Low** | High |
| Shenandoah | Concurrent | Large | Very Low | Medium |
| Epsilon | No GC | Testing | N/A | N/A |

### G1 GC Details

```
Heap: Regions (1-32MB each)
     Eden regions → Survivor regions → Old regions
     
Collection:
  Young GC: Eden + some survivors → survivors/old
  Mixed GC: Young + some old regions
  Full GC: Serial fallback (avoid!)
```

### ZGC

```
- Colored pointers (load barriers)
- Concurrent marking, relocation, remapping
- No generations (single contiguous heap)
- Heap: 8MB - 16TB
- Pause times: < 1ms typically
```

---

## Memory Model (JMM)

### Happens-Before

| Action | Happens-Before |
|--------|----------------|
| Thread.start() | Thread's first action |
| Thread.join() | Thread's last action |
| volatile write | volatile read |
| unlock(m) | lock(m) |
| end of constructor | final field read |

### Visibility Guarantees

```java
// Without volatile - may see stale value
class Worker {
    boolean running = true;
    void stop() { running = false; }
}

// With volatile - guaranteed visibility
class Worker {
    volatile boolean running = true;
}

// Final fields - safe publication
class Immutable {
    final int value;
    Immutable(int v) { value = v; } // Freeze
}
```

---

## Performance Tuning

### Heap Sizing

```bash
# Fixed heap
-Xms4g -Xmx4g

# Generational
-XX:NewRatio=2          # Old:Young = 2:1
-XX:SurvivorRatio=8     # Eden:Survivor = 8:1

# G1
-XX:MaxGCPauseMillis=200
-XX:G1HeapRegionSize=16m

# ZGC
-XX:+UseZGC
-XX:ZCollectionInterval=10
```

### Monitoring

```bash
# JMX
-Dcom.sun.management.jmxremote
-Dcom.sun.management.jmxremote.port=9010

# GC logs
-Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=10m

# JFR (Java Flight Recorder)
-XX:StartFlightRecording=duration=60s,filename=recording.jfr
```

### Analysis Tools

| Tool | Purpose |
|------|---------|
| `jcmd` | Diagnostic commands |
| `jstat` | GC/compiler stats |
| `jmap` | Heap dump |
| `jhat` | Heap analysis (deprecated) |
| `jhsdb` | HotSpot debugger |
| `jfr` | Flight recorder analysis |
| VisualVM | GUI profiling |
| JMC | Mission Control (JFR) |
| async-profiler | Low-overhead sampling |

---

## Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| OOM: Heap | Leak, undersized | Analyze heap dump, increase -Xmx |
| OOM: Metaspace | Classloader leak | Fix classloader, increase MaxMetaspace |
| Long GC pauses | Wrong collector, large heap | G1/ZGC, tune regions |
| High CPU | Spin loops, bad regex | Profile, fix algorithms |
| Thread starvation | Blocking in virtual threads | Use ReentrantLock, avoid synchronized |