# EXERCISES — JVM Internals

## Exercise 1: Object Layout Analysis

### Task
Use JOL (Java Object Layout) to analyze the memory layout of various objects.

### Steps
1. Add JOL dependency
2. Analyze these classes:
   - Simple POJO with 3 fields
   - Class with inheritance
   - Array of primitives vs objects
   - Class with `volatile` fields

### Code Template
```xml
<dependency>
    <groupId>org.openjdk.jol</groupId>
    <artifactId>jol-core</artifactId>
    <version>0.16</version>
</dependency>
```

```java
ClassLayout layout = ClassLayout.parseInstance(new MyClass());
System.out.println(layout.toPrintable());
```

### Expected Output Analysis
- Identify header size (12/16 bytes)
- Field ordering and padding
- Reference compression effects

---

## Exercise 2: Lock Inflation Observation

### Task
Observe lock inflation from biased → lightweight → heavyweight.

### Steps
1. Create a class with synchronized method
2. Run with `-XX:+PrintBiasedLockingStatistics -XX:+PrintLockingStatistics`
3. Use multiple threads to trigger inflation
4. Analyze thread dump with `jstack`

### Code
```java
public class LockInflationDemo {
    private final Object lock = new Object();
    
    public void biasedLock() {
        synchronized(lock) { /* single thread */ }
    }
    
    public void lightweightLock() {
        synchronized(lock) { /* low contention */ }
    }
    
    public void heavyweightLock() {
        synchronized(lock) { Thread.sleep(1000); } // high contention
    }
}
```

### JVM Flags
```bash
-XX:+UnlockDiagnosticVMOptions
-XX:+PrintBiasedLockingStatistics
-XX:+PrintLockingStatistics
-XX:BiasedLockingStartupDelay=0
```

---

## Exercise 3: Safepoint Latency Measurement

### Task
Measure safepoint latency using JFR.

### Steps
1. Start JFR recording with safepoint events
2. Run allocation-heavy workload
3. Analyze safepoint duration and frequency

### JFR Configuration
```bash
-XX:StartFlightRecording=duration=60s,filename=safepoints.jfr,settings=profile
```

### Analysis
```bash
# In JMC or jfr tool
jfr print --events jdk.SafepointBegin,jdk.SafepointEnd safepoints.jfr
```

---

## Exercise 4: Code Cache Monitoring

### Task
Monitor code cache usage and compilation activity.

### Steps
1. Run application with `-XX:+PrintCompilation -XX:+PrintCodeCache`
2. Observe tiered compilation transitions
3. Monitor code cache occupancy

### Analysis Commands
```bash
jcmd <pid> Compiler.codecache
jcmd <pid> Compiler.directives_print
```

---

## Exercise 5: Metaspace GC Behavior

### Task
Trigger and analyze Metaspace garbage collection.

### Steps
1. Create dynamic classes (using ClassLoader or ByteBuddy)
2. Monitor Metaspace usage with `jstat -gcmetacapacity`
3. Force class unloading
4. Analyze Metaspace GC logs

### Code
```java
// Generate many classes dynamically
for (int i = 0; i < 10000; i++) {
    String className = "DynamicClass" + i;
    byte[] bytecode = generateClassBytecode(className);
    defineClass(className, bytecode);
}
```

### JVM Flags
```bash
-XX:+TraceClassLoading
-XX:+TraceClassUnloading
-XX:MetaspaceSize=10m
-XX:MaxMetaspaceSize=50m
-Xlog:gc+metaspace=debug
```

---

## Exercise 6: Thread Stack Analysis

### Task
Analyze thread stack sizes and states.

### Steps
1. Create threads with different stack sizes (`-Xss`)
2. Use `jstack` to capture thread dumps
3. Analyze stack frame count and native vs Java frames
4. Compare virtual threads vs platform threads

### Commands
```bash
jstack -l <pid> > threaddump.txt
jcmd <pid> Thread.print -l
```

---

## Exercise 7: Escape Analysis Verification

### Task
Verify scalar replacement and lock elision.

### Code
```java
public class EscapeAnalysisDemo {
    public void noEscape() {
        Point p = new Point(1, 2); // Should be scalar replaced
        System.out.println(p.x + p.y);
    }
    
    public void globalEscape() {
        points.add(new Point(1, 2)); // Escapes
    }
    
    public void argEscape() {
        process(new Point(1, 2)); // Escapes via method call
    }
}
```

### Flags
```bash
-XX:+DoEscapeAnalysis
-XX:+EliminateAllocations
-XX:+EliminateLocks
-XX:+PrintEscapeAnalysis
```

---

## Exercise 8: Inline Cache Observation

### Task
Observe inline cache behavior (monomorphic → bimorphic → megamorphic).

### Code
```java
interface Processor { void process(); }

class ProcA implements Processor { public void process() {} }
class ProcB implements Processor { public void process() {} }
class ProcC implements Processor { public void process() {} }

// Test different call site polymorphism
void test(Processor p) { p.process(); }
```

### Flags
```bash
-XX:+PrintInlining
-XX:MaxInlineSize=35
-XX:FreqInlineSize=325
```

---

## Exercise 9: Compressed OOPs Boundary

### Task
Test compressed OOPs behavior at heap boundary.

### Steps
1. Run with `-Xmx31g -XX:+UseCompressedOops` (should work)
2. Run with `-Xmx33g -XX:+UseCompressedOops` (may fail or disable)
3. Observe object alignment effects

### Flags
```bash
-XX:+UseCompressedOops
-XX:ObjectAlignmentInBytes=16
-XX:+PrintCompressedOopsMode
```

---

## Exercise 10: JFR Profiling Session

### Task
Complete profiling workflow for a sample application.

### Steps
1. Start application with JFR continuous recording
2. Apply load for 5 minutes
3. Stop recording and analyze in JMC
4. Identify:
   - Hot methods
   - Allocation sites
   - Lock contention
   - GC pauses
   - Safepoint latency

### Report Template
```
Application: _______
JDK Version: _______
Heap Size: _______
Load Profile: _______

Top 5 Hot Methods:
1. _______ (% CPU)
2. _______ (% CPU)
...

Allocation Rate: _______ MB/s
GC Pause (p99): _______ ms
Safepoint Count: _______
Code Cache Usage: _______%
```