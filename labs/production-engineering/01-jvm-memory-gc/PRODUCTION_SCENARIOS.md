# PRODUCTION SCENARIOS: JVM Memory & GC
## Lab 01 | Production Engineering Academy

---

## Scenario 1: The Black Friday Full GC Disaster

### Context
E-commerce platform, 50,000 concurrent users on Black Friday. Java 11, G1GC, 4GB heap.

### What Happened
At 10:03 AM, the platform froze for 11 seconds. All requests timed out. Revenue lost: ~$180,000.

### GC Log Evidence
```
[GC(2341)] Pause Full (G1 Compaction Pause) 3892M->1221M(4096M) 11234.789ms
```

### Root Cause Analysis
```
Timeline:
09:45 — Flash sale announced, traffic 10x spikes
09:58 — Session objects (30KB each x 50K users = 1.5GB) tenuring into Old Gen
10:01 — Old Gen occupancy: 95% (3.9GB / 4GB)
10:03 — Concurrent marking fails to reclaim fast enough
10:03 — G1 falls back to Full GC (concurrent mode failure)
10:03:00 — STW Full GC begins, all 50K connections time out
10:03:11 — Full GC completes, service resumes
```

### Fix Applied
```bash
# Before (broken)
-Xmx4g -Xms2g -XX:+UseG1GC

# After (fixed)
-Xmx8g -Xms8g \
-XX:+UseG1GC \
-XX:MaxGCPauseMillis=100 \
-XX:InitiatingHeapOccupancyPercent=35 \  # Start marking earlier (was 45%)
-XX:G1ReservePercent=15 \               # Keep 15% reserve for evacuation
-XX:G1NewSizePercent=20 \               # Ensure young gen doesn't shrink
-XX:G1MaxNewSizePercent=40              # Cap young gen growth
```

**Additionally**: Session objects were moved to Redis. This reduced live heap by 1.5GB.

---

## Scenario 2: The Metaspace Explosion

### Context
Financial services app. Spring Boot application with dynamic plugin loading. Monday morning restarts recover it, but by Friday it OOMs.

### What Happened
`java.lang.OutOfMemoryError: Metaspace` — every Friday after 5 days of uptime.

### Investigation
```bash
# jcmd to inspect class loading
jcmd <pid> VM.classloaders

# Output snippet showing the leak:
ClassLoader: com.company.plugin.PluginClassLoader@7f3a
  Loaded classes: 847
ClassLoader: com.company.plugin.PluginClassLoader@8c2b   ← another one!
  Loaded classes: 847
ClassLoader: com.company.plugin.PluginClassLoader@9d1e   ← and another!
  Loaded classes: 847
# ... 142 more PluginClassLoader instances
```

### Root Cause
Plugin reload feature was creating a new ClassLoader on each plugin update but never calling `close()`. Each CL held 847 classes × metadata. After 5 days × hourly updates = 120 CL instances × 847 classes = 101,640 leaked class definitions.

### Fix
```java
// Before — leaking
public void reloadPlugin(String pluginPath) {
    URLClassLoader cl = new URLClassLoader(new URL[]{pluginUrl}, parent);
    Plugin plugin = cl.loadClass("Plugin").newInstance();
    activePlugins.put(name, plugin);
    // Old CL never closed!
}

// After — proper lifecycle
public void reloadPlugin(String pluginPath) {
    URLClassLoader oldCl = activeClassLoaders.get(name);
    if (oldCl != null) {
        activePlugins.remove(name);
        oldCl.close();  // Close old CL → GC can collect its classes
        System.gc();    // Encourage (not force) class unloading
    }
    URLClassLoader newCl = new URLClassLoader(new URL[]{pluginUrl}, parent);
    activeClassLoaders.put(name, newCl);
    Plugin plugin = (Plugin) newCl.loadClass("PluginImpl").getDeclaredConstructor().newInstance();
    activePlugins.put(name, plugin);
}
```

---

## Scenario 3: The Phantom Memory Growth

### Context
Payment processing microservice. Container (4GB limit) getting OOM-killed by Kubernetes every 48-72 hours. Java heap healthy (max 2GB used), but container RSS keeps growing.

### Investigation
```bash
# Check JVM native memory
jcmd <pid> VM.native_memory detail

# Output:
Native Memory Tracking:
Total: reserved=5.2GB, committed=4.1GB

-                 Java Heap (reserved=2048MB, committed=2048MB)
-                    Class (reserved=384MB, committed=82MB)
-                   Thread (reserved=220MB, committed=220MB)
-                     Code (reserved=256MB, committed=143MB)
-                       GC (reserved=128MB, committed=128MB)
-                 Compiler (reserved=26MB, committed=26MB)
-                 Internal (reserved=512MB, committed=512MB)    ← SUSPICIOUS
-                   Symbol (reserved=23MB, committed=23MB)
-    Native Memory Tracking (reserved=6MB, committed=6MB)
-              Arena Chunk (reserved=222MB, committed=222MB)
-                  Unknown (reserved=1.4GB, committed=1.4GB)    ← !!! THE LEAK
```

### Root Cause
The application was using `sun.misc.Unsafe.allocateMemory()` via a third-party library (custom serialization framework) that never freed native memory. The library had a bug where large object serialization cached native buffers indefinitely.

### Fix
```java
// Replaced the leaking library with standard Java serialization
// Added Direct Memory monitoring alert at 1.5GB
// Set -XX:MaxDirectMemorySize=512m to cap off-heap allocation
```

---

## Scenario 4: Humongous Object Allocation Storm

### Context
Real-time analytics service processing large JSON payloads. G1GC with 16GB heap, but constant "Humongous object allocation" warnings and frequent Mixed GCs.

### GC Log Pattern
```
[gc,heap] Humongous regions: 12->47 (allocated 35 new humongous regions in one minute)
[gc     ] GC(891) Pause Young (Normal) ... 2345.678ms  ← Young GC taking 2+ seconds!
```

### Root Cause
API response deserialization was allocating `byte[]` arrays of 5-15MB per request (larger than G1's 8MB region size). These bypassed Young Gen entirely and went to Old Gen as humongous objects, fragmenting the heap and causing long evacuation pauses.

### Fix
```java
// Before — 1 large byte array per request
byte[] payload = IOUtils.toByteArray(request.getInputStream());
JsonNode root = mapper.readValue(payload, JsonNode.class);

// After — streaming parse, no large byte array
try (InputStream stream = request.getInputStream()) {
    JsonNode root = mapper.readValue(stream, JsonNode.class);  // Zero copy
}

// Also: configured G1 for larger regions
// -XX:G1HeapRegionSize=16m  (makes 15MB objects non-humongous)
```

---

## Scenario 5: The GC That Wasn't GC

### Context
Order management service. "GC pauses" appearing to last 4-8 seconds in monitoring, but GC logs show < 100ms pause times.

### Investigation
```bash
# GC safepoint statistics
-XX:+PrintSafepointStatistics
-XX:PrintSafepointStatisticsCount=1

# Log output:
         vmop                    [threads: total initially_running wait_to_block]  [time: spin block sync cleanup vmop] page_trap_count
5.643: G1CollectFull              [  120    80   8 ]      [0      1  1  0  4523]  1

# spin=0ms, block=1ms, sync=1ms, vmop=4523ms ← GC took 4.5 seconds
# BUT separately:
# Total time for which application threads were stopped: 8.234 seconds
# vs GC time: 4.523 seconds
# → 3.7 seconds just waiting for safepoint!
```

### Root Cause
Background analytics thread running a tight loop processing a large array with no safepoint poll:

```java
// BAD — HotSpot doesn't insert safepoint polls in counted loops by default (pre-Java 14)
void processMetrics(long[] metrics) {
    long sum = 0;
    for (int i = 0; i < metrics.length; i++) {  // JIT may eliminate safepoint poll here!
        sum += metrics[i] * metrics[i];  // Tight arithmetic loop
    }
    this.result = sum;
}
```

### Fix
```java
// Option 1: Use Java 14+ where JVM forces safepoint polls in loops

// Option 2: Add artificial checkpoint
void processMetrics(long[] metrics) {
    long sum = 0;
    for (int i = 0; i < metrics.length; i++) {
        sum += metrics[i] * metrics[i];
        if (i % 10_000 == 0) Thread.yield();  // Forces safepoint check
    }
    this.result = sum;
}

// Option 3: Split into chunks
// Process in batches of 10K, submit each as separate task
```

---

## 📊 Incident Pattern Summary

| Symptom | Likely Cause | Immediate Mitigation | Long-Term Fix |
|---------|-------------|---------------------|---------------|
| Full GC, 10+ second pauses | Old Gen full, concurrent mode failure | Restart, increase heap | Right-size heap, fix memory leak |
| OOM: Java heap | Memory leak or heap too small | Heap dump, restart | Fix leak, increase heap |
| OOM: Metaspace | ClassLoader leak | Restart | Fix CL lifecycle |
| Container OOM-killed | Off-heap/native memory leak | Restart | Find and fix native allocation |
| GC pauses longer than GC log shows | Safepoint delays | Identify blocking threads | Fix long-running native/JNI code |
| Humongous object warnings | Large objects bypassing young gen | Increase G1 region size | Pool or stream large objects |
| GC runs constantly | Eden too small or allocation too high | Increase young gen | Reduce object creation, use pooling |
