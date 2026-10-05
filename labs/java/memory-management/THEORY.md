# THEORY — Memory Management

## Overview

Fundamentals of Java memory management: heap, stack, garbage collection basics, and common memory issues.

---

## Memory Areas

### Heap (Shared)

- All objects allocated here
- Managed by GC
- Sized by `-Xms` (initial) and `-Xmx` (max)
- Generational: Young + Old

### Stack (Per Thread)

- Method frames, local variables, operand stack
- Fixed size per thread (`-Xss`, default 1MB)
- LIFO, auto-managed
- StackOverflowError if exceeded

### Metaspace (Native, Shared)

- Class metadata (Klass, methods, annotations)
- Replaced PermGen in Java 8
- Sized by `-XX:MetaspaceSize` / `-XX:MaxMetaspaceSize`

### Code Cache (Native, Shared)

- JIT compiled code
- Sized by `-XX:ReservedCodeCacheSize`

### Direct Memory (Native)

- `ByteBuffer.allocateDirect()`
- `FileChannel.map()`
- Not in heap, limited by `-XX:MaxDirectMemorySize`

---

## Object Lifecycle

### Allocation

```java
// Fast path: TLAB bump pointer
MyObject obj = new MyObject();

// Slow path: shared allocation, may trigger GC
```

### Reference Types

| Type | GC Behavior | Use Case |
|------|-------------|----------|
| Strong | Never collected | Normal references |
| Soft | Collected if memory needed | Caches |
| Weak | Collected next GC | Canonical maps |
| Phantom | Collected after finalization | Cleanup actions |

```java
// SoftReference - cache
Map<String, SoftReference<Bitmap>> cache = new HashMap<>();

// WeakReference - canonical map
WeakHashMap<Class<?>, Metadata> metadata = new WeakHashMap<>();

// PhantomReference - cleanup
ReferenceQueue<Resource> queue = new ReferenceQueue<>();
PhantomReference<Resource> ref = new PhantomReference<>(resource, queue);
```

### Finalization (Deprecated)

```java
// Avoid - unpredictable timing, performance cost
@Override
protected void finalize() throws Throwable {
    try { cleanup(); } finally { super.finalize(); }
}

// Use Cleaner instead (Java 9+)
Cleaner cleaner = Cleaner.create();
cleaner.register(this, () -> cleanup());
```

---

## Garbage Collection

### Reachability

```
GC Roots → Strong References → Live Objects
     ├─ Local variables
     ├─ Static fields
     ├─ JNI references
     └─ Thread stacks
```

### Generational Hypothesis

1. Most objects die young
2. Few references from old → young

### Basic Collectors

| Collector | Algorithm | Use Case |
|-----------|-----------|----------|
| Serial | Copying (young), Mark-Sweep-Compact (old) | Single-threaded, small heaps |
| Parallel | Parallel copying, Parallel compacting | Throughput, batch |
| G1 | Regional, concurrent marking | Balanced, large heaps |
| ZGC | Concurrent, colored pointers | Low latency, huge heaps |

---

## Common Issues

### OutOfMemoryError Types

```java
// Java heap space
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/dumps/

// Metaspace
-XX:MaxMetaspaceSize=512m

// GC overhead limit exceeded
-XX:-UseGCOverheadLimit  // Disable (not recommended)

// Unable to create native thread
-Xss512k  // Reduce stack size
// Or reduce thread count

// Requested array size exceeds VM limit
// Max array size: Integer.MAX_VALUE - 8
```

### Memory Leaks

```java
// 1. Static collection growth
static List<Object> leak = new ArrayList<>();
leak.add(new BigObject()); // Never removed

// 2. Unclosed resources
try (FileInputStream fis = new FileInputStream(file)) { }

// 3. ThreadLocal in pooled threads
ThreadLocal<Connection> tl = ThreadLocal.withInitial(() -> getConnection());
// Fix: tl.remove() in finally

// 4. Listener accumulation
button.addActionListener(e -> doWork()); // Never removed
```

---

## Monitoring

### Basic Commands

```bash
jcmd <pid> GC.heap_info
jcmd <pid> GC.class_histogram
jstat -gc <pid> 1000
jmap -histo <pid>
```

### VisualVM / JConsole

- Heap usage over time
- GC frequency and duration
- Thread count
- Class loading

---

## Best Practices

1. **Right-size heap**: `-Xms = -Xmx` for production
2. **Avoid finalizers**: Use `Cleaner` or try-with-resources
3. **Close resources**: Try-with-resources for `AutoCloseable`
4. **Limit caches**: Use `Caffeine`, `Guava Cache`, or `WeakHashMap`
5. **Profile allocations**: JFR, async-profiler
6. **Monitor GC**: Log GC, alert on pause times