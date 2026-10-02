# Lab 01 — Java Memory Leak Debugging: Quiz

## Instructions
Answer 10 questions to test your knowledge of Java memory leak debugging. Each has one correct answer. Answers and explanations are at the end.

---

## Questions

### Q1: What is the primary difference between a Java heap memory leak and a Metaspace memory leak?
- A) Heap leaks affect old generation; Metaspace leaks affect young generation
- B) Heap leaks are caused by unreachable objects; Metaspace leaks are caused by reachable ClassLoaders
- C) Heap leaks fill the Java heap (-Xmx); Metaspace leaks fill native memory outside the heap
- D) Heap leaks require heap dumps to diagnose; Metaspace leaks require thread dumps

### Q2: A ThreadLocal with a static field stores a reference to a request-scoped SecurityContext. The application uses a fixed thread pool. After 24 hours, the application crashes with OutOfMemoryError: Metaspace. What is the root cause?
- A) The SecurityContext objects are too large
- B) The ThreadLocal values are never removed, preventing ClassLoader garbage collection
- C) The thread pool is too large
- D) The SecurityContext holds too many permissions

### Q3: Which JVM flag combination is MOST appropriate for capturing a heap dump on OutOfMemoryError while also logging GC details to a rotating file?
- A) `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps -Xlog:gc:gc.log`
- B) `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps -Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=100m`
- C) `-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:gc.log`
- D) `-XX:StartFlightRecording=dumponexit=true -XX:+HeapDumpOnOutOfMemoryError`

### Q4: You run `jcmd <pid> VM.classloader_stats` and see 500+ URLClassLoader instances, each with 2000+ loaded classes. The application uses dynamic class loading for plugins. What does this indicate?
- A) Normal operation for a plugin-based system
- B) A ClassLoader leak — ClassLoaders are not being garbage collected
- C) The JVM needs more Metaspace
- D) The plugin system is loading duplicate classes

### Q5: In a heap dump analyzed with Eclipse MAT, a URLClassLoader shows 2GB retained heap. The "Path to GC Roots" shows: `ThreadLocal$ThreadLocalMap.Entry → SecurityContext → URLClassLoader`. What is the fix?
- A) Increase MaxMetaspaceSize to 4GB
- B) Add `threadLocal.remove()` in a finally block after each request
- C) Switch to a cached thread pool
- D) Use `-XX:+UseCompressedClassPointers`

### Q6: The GC log shows: `Metaspace: 128M->118M(256M)` with `Class unloading: 0 classes, 0 loaders`. Is this healthy?
- A) Yes, Metaspace decreased by 10MB
- B) No, class unloading count of 0 indicates a ClassLoader leak
- C) Yes, as long as Metaspace is below MaxMetaspaceSize
- D) No, Metaspace should never decrease

### Q7: Which Java 20+ feature provides bounded-lifetime per-thread context that automatically clears on scope exit, eliminating ThreadLocal leaks?
- A) Virtual Threads (JEP 444)
- B) ScopedValue (JEP 429)
- C) Record Patterns (JEP 405)
- D) Structured Concurrency (JEP 453)

### Q8: You cannot modify a third-party library that has a ThreadLocal leak. Which mitigation strategy is MOST appropriate for production?
- A) Increase MaxMetaspaceSize to 2GB and restart weekly
- B) Use a servlet Filter that calls ThreadLocal.remove() via reflection after each request
- C) Disable the library's functionality
- D) Switch to a different JVM implementation

### Q9: What metric should you alert on to detect a Metaspace leak BEFORE an OutOfMemoryError occurs?
- A) Heap usage after GC > 80%
- B) Metaspace growth rate > 50MB/hour for 2+ hours
- C) GC pause duration > 500ms
- D) Thread count > 500

### Q10: In a production monitoring system for 10,000 JVM instances, what is the recommended approach for fleet-wide Metaspace leak detection?
- A) Capture daily heap dumps from all instances
- B) Export JMX Metaspace metrics to Prometheus, alert on growth rate and ClassLoader count trends
- C) Run jcmd VM.classloader_stats via SSH on all instances hourly
- D) Enable JFR on all instances and analyze centrally

---

## Answer Key

| Question | Answer | Explanation |
|---|---|---|
| 1 | **C** | Heap leaks fill the Java heap (managed by -Xmx); Metaspace leaks fill native memory for class metadata, outside the heap. |
| 2 | **B** | ThreadLocal values are strongly referenced in ThreadLocalMap. If never removed, they keep the SecurityContext (and its ClassLoader) reachable, preventing Metaspace reclamation. |
| 3 | **B** | Uses modern unified logging (`-Xlog:gc*`) with rotation (filecount, filesize) and proper heap dump path. |
| 4 | **B** | Continuously increasing ClassLoader count with many classes each indicates ClassLoaders are not being GC'd — a ClassLoader leak. |
| 5 | **B** | The ThreadLocal holds the SecurityContext which holds the ClassLoader. Must call `remove()` in finally block to break the reference chain. |
| 6 | **B** | Zero class unloading despite Metaspace churn means ClassLoaders are not being collected — classic ClassLoader leak signature. |
| 7 | **B** | ScopedValue (JEP 429) provides automatic cleanup on scope exit via try-with-resources, eliminating the root cause of ThreadLocal leaks. |
| 8 | **B** | Reflection-based cleanup in a servlet Filter is a practical mitigation when you cannot modify the library code directly. |
| 9 | **B** | Metaspace growth rate and ClassLoader count trends are leading indicators; heap/GC metrics are lagging for Metaspace leaks. |
| 10 | **B** | Agent-less JMX metric export scales to 10K+ instances; heap dumps and JFR are too heavy for continuous fleet-wide collection. |

---

## Scoring Guide
- **10/10**: Expert — ready to lead memory leak investigations
- **8-9/10**: Strong — solid understanding of leak patterns and tools
- **6-7/10**: Developing — review ThreadLocal/ClassLoader leak mechanics
- **<6/10**: Needs study — revisit JVM memory architecture and diagnostic tools