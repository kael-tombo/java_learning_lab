# THEORY — Java Module System & Foreign Function Interface

## Overview

Two major Java 9+ features: **JPMS (Modules)** for strong encapsulation and **FFI (Foreign Function & Memory API)** for native interop.

## Part 1: Java Platform Module System (JPMS)

### Module Declaration (module-info.java)

```java
module com.example.app {
    // Exported packages (public API)
    exports com.example.api;
    exports com.example.spi to com.example.impl;  // qualified export
    
    // Required modules
    requires java.sql;
    requires transitive java.logging;   // consumers get logging too
    requires static java.xml;           // optional at runtime
    
    // Services
    uses com.example.spi.Service;
    provides com.example.spi.Service with com.example.impl.ServiceImpl;
    
    // Deep reflection access
    opens com.example.internal to com.example.test;
}
```

### Module Directives

| Directive | Readability | Deep Reflection |
|-----------|-------------|-----------------|
| `requires` | ✅ | ❌ |
| `requires transitive` | ✅ (transitive) | ❌ |
| `exports` | ✅ | ❌ |
| `opens` | ✅ | ✅ |
| `uses` / `provides` | Service loading | — |

### Module Resolution

- JVM builds module graph at startup
- Fails fast on: missing modules, cycles, split packages
- Unnamed module (classpath) reads all, exports all, **cannot be required**

### Migration Strategies

1. **Bottom-up**: Convert leaf modules first
2. **Automatic modules**: JARs on module path without module-info
3. **Tools**: `jdeps --print-module-deps`, `jlink`, `jmod`

---

## Part 2: Foreign Function & Memory API (Java 22+)

### Memory Segments

```java
// Native memory allocation
try (Arena arena = Arena.ofConfined()) {
    MemorySegment segment = arena.allocate(1024);
    segment.setAtIndex(ValueLayout.JAVA_INT, 0, 42);
    int value = segment.getAtIndex(ValueLayout.JAVA_INT, 0);
}

// Memory-mapped file
try (Arena arena = Arena.ofConfined()) {
    MemorySegment mapped = arena.mapFile(path, 0, size, READ_WRITE);
}
```

### Layouts & ValueLayout

```java
// Primitive layouts
ValueLayout.JAVA_INT    // 4 bytes
ValueLayout.JAVA_LONG   // 8 bytes
ValueLayout.JAVA_DOUBLE // 8 bytes
ValueLayout.ADDRESS     // platform address size

// Struct layout
MemoryLayout struct = MemoryLayout.structLayout(
    ValueLayout.JAVA_INT.withName("id"),
    MemoryLayout.sequenceLayout(10, ValueLayout.JAVA_BYTE).withName("name"),
    ValueLayout.JAVA_DOUBLE.withName("salary")
);
```

### Function Linking

```java
Linker linker = Linker.nativeLinker();

// C function: int strlen(const char *s)
MethodHandle strlen = linker.downcallHandle(
    linker.defaultLookup().find("strlen").orElseThrow(),
    FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.ADDRESS)
);

// Call from Java
try (Arena arena = Arena.ofConfined()) {
    MemorySegment cString = arena.allocateFrom("Hello World");
    int len = (int) strlen.invokeExact(cString);
}
```

### Native Calls with JNI Alternative

```java
// Traditional JNI: requires C code, javah, compilation
// FFI: pure Java, no C compilation needed

// Example: calling POSIX open
MethodHandle open = linker.downcallHandle(
    linker.defaultLookup().find("open").orElseThrow(),
    FunctionDescriptor.of(ValueLayout.JAVA_INT, 
        ValueLayout.ADDRESS,  // pathname
        ValueLayout.JAVA_INT, // flags
        ValueLayout.JAVA_INT  // mode
    )
);
```

### Callbacks (Upcalls)

```java
// C function: void qsort(void *base, size_t nmemb, size_t size, 
//                        int (*compar)(const void *, const void *))

MethodHandle qsort = linker.downcallHandle(
    linker.defaultLookup().find("qsort").orElseThrow(),
    FunctionDescriptor.ofVoid(
        ValueLayout.ADDRESS,      // base
        ValueLayout.JAVA_LONG,    // nmemb
        ValueLayout.JAVA_LONG,    // size
        ValueLayout.ADDRESS       // compar (function pointer)
    )
);

// Java comparator as function pointer
MemorySegment comparFunc = linker.upcallStub(
    MethodHandles.lookup().findStatic(MyClass.class, "compare", 
        MethodType.methodType(int.class, MemorySegment.class, MemorySegment.class)
    ),
    FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.ADDRESS, ValueLayout.ADDRESS),
    arena
);

qsort.invokeExact(arraySegment, count, elementSize, comparFunc);
```

### Safety & Performance

| Aspect | JNI | FFI (Panama) |
|--------|-----|--------------|
| Safety | Unsafe (crash JVM) | MemorySegment bounds-checked |
| Performance | Good | Comparable, less overhead |
| Build | Requires C compiler | Pure Java |
| Portability | Platform-specific | Abstracted layouts |
| GC interaction | Manual | Arena-scoped lifetimes |

### Arena Lifecycles

```java
// Confined: single-threaded, auto-free on close
Arena.ofConfined()

// Shared: multi-threaded, manual close
Arena.ofShared()

// Global: JVM lifetime, never freed
Arena.global()

// Automatic: try-with-resources
try (Arena arena = Arena.ofConfined()) {
    // allocations tied to arena
}
```

## Integration

```java
module com.example.native {
    requires java.base;           // FFI in java.base since 22
    requires transitive java.foreign; // if exposing native APIs
    
    // For JNI interop during migration
    // requires jdk.incubator.foreign; // preview/incubator
}
```