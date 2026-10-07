# Lab 01: Java Memory Leak Debugging — Netflix Zuul Gateway OOM

## Situation Overview

Netflix's Zuul gateway infrastructure experienced deterministic OutOfMemory (OOM) crashes every 6 hours in production. The gateway serves as the API gateway fronting hundreds of microservices, handling upwards of 50,000 requests per second across multiple AWS regions. Each OOM event caused a complete loss of availability for the affected gateway cluster for approximately 3-5 minutes while the JVM restarted and warmed up its caches. Due to the predictable 6-hour cadence, the team could anticipate the crash window but could not eliminate it without a root cause fix.

The incident spanned two weeks of investigation, involving engineers from the Edge Gateway team, the JVM Platform team, and external consultants with expertise in Netflix's custom JVM builds. The OOM killer was triggered by the Linux kernel's Out-Of-Memory (OOM) Killer process, which terminated the JVM process when the operating system could no longer allocate memory to any process. This was not a heap OOM in the traditional sense (-Xmx being exceeded) but rather a Metaspace exhaustion: the JVM's native memory region for class metadata grew without bound until the container's memory limit was reached.

## Severity Assessment

| Criteria | Rating | Details |
|----------|--------|---------|
| Impact Scope | P0 | All traffic through affected gateway cluster dropped |
| User Facing | Yes | 100% of API requests failed during crash window |
| Duration Per Event | 3-5 min | JVM restart + warmup, multiple times per day |
| Frequency | Every 6 hours | Predictable, deterministic pattern |
| Detectability | Poor | No pre-crash alert; only post-crash paging |
| Root Cause Complexity | High | Involved ClassLoader, Metaspace, ThreadLocal internals |
| Fix Complexity | Medium | Code change in filter chain cleanup |
| Blast Radius | Regional | One AWS region at a time (circuit breakers isolated regions) |

## Impact Assessment

### Customer Impact
- API gateway timeouts for Netflix members during crash + restart windows (3-5 minutes, 4x daily)
- Failed video playback starts, browse requests, and account actions
- Estimated 0.5-1.5% of peak-hour requests affected per region per day

### Engineering Impact
- 3 on-call rotations woken up over 14 days before root cause identified
- Manual failover to backup clusters every 6 hours as stopgap
- Cache rebuild after each restart caused elevated latencies for 2-3 minutes post-recovery
- ~120 engineering hours spent on investigation, diagnosis, and fix

### Business Impact
- Customer support tickets spiked 300% during incident period
- Slight increase in churn for users who experienced multiple failed sessions
- Incident review triggered changes to JVM monitoring across all services

## System Architecture (Affected Component)

```
                          ┌──────────────────────┐
                          │   Internet / CDN      │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │   AWS ELB / NLB       │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │   Zuul Gateway Cluster│
                          │   (JVM, 8GB RAM)     │◄── OOM every 6h
                          └──────────┬───────────┘
                                     │
               ┌─────────────────────┼─────────────────────┐
               │                     │                     │
        ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
        │ Microservice │      │ Microservice │      │ Microservice │
        │    A (Eureka)│      │    B (Hystrix)│    │    C (Ribbon) │
        └──────────────┘      └──────────────┘      └──────────────┘
```

## Key Technologies

- **JVM**: HotSpot JDK 11 (custom Netflix build with GC and kernel patches)
- **Gateway Framework**: Netflix Zuul 2.x (reactive, Netty-based)
- **Service Discovery**: Netflix Eureka
- **Resilience**: Hystrix circuit breakers, Ribbon load balancer
- **Observability**: Atlas (Netflix metrics), ELK for logs, JFR for JVM events
- **Deployment**: Spinnaker, AWS ASG with rolling deployments

## Learning Objectives

By completing this lab, you will be able to:
1. Diagnose Metaspace OOM errors using heap dumps, JFR recordings, and GC logs
2. Identify ThreadLocal leaks associated with ClassLoader retention
3. Use Eclipse MAT to find dominating ClassLoader references
4. Apply WeakReference patterns for ThreadLocal values in frameworks
5. Implement proper cleanup in request-scoped filter chains
6. Set up JVM monitoring to detect Metaspace growth trends before OOM

## References

- Netflix Tech Blog: "Zuul 2: The Netflix Gateway" — https://netflixtechblog.com/open-sourcing-zuul-2
- Oracle Java SE: "JVM Metaspace and OutOfMemoryError" — https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/metaspace.html
- Google SRE: "Debugging Java Memory Leaks in Production" — Google SRE Workbook
- Eclipse MAT Documentation — https://eclipse.dev/mat/
- JDK Flight Recorder Guide — https://docs.oracle.com/javacomponents/jmc-5-4/jfr-runtime-guide/about.htm
- "ThreadLocal and Memory Leaks" by Peter Lawrey — (link removed)
- Baeldung: "Metaspace in Java 8" — (link removed)
- Netflix Tech Blog: "Fixing a Memory Leak in Netflix Zuul" — Netflix Engineering Internal Postmortem

## Prerequisites

- Java 11+ runtime
- Eclipse MAT (Memory Analyzer Tool) installed
- JDK Mission Control (JMC) for JFR analysis
- Basic understanding of JVM memory model (heap, stack, metaspace)
- Familiarity with ThreadLocal semantics and ClassLoader hierarchy

## Exercises

1. Analyze the provided heap dump to identify the ClassLoader that dominates retained memory
2. Trace the reference chain from the leaking ThreadLocal to the GC root
3. Find all Filter classes that store request-scoped data in static ThreadLocal fields
4. Write cleanup code using try-finally in the Zuul filter pipeline
5. Replace strong references with WeakReference where ThreadLocal values outlive request scope
6. Set up GC logging and JFR events to detect Metaspace expansion trends

## Technical Deep Dive: JVM Metaspace Architecture

### What is Metaspace?

Metaspace is the native memory region introduced in Java 8 to replace the Permanent Generation (PermGen). It stores class metadata including bytecodes, constant pools, annotations, method data, and field information. Unlike PermGen, Metaspace is allocated in native memory (outside the Java heap) and can grow dynamically based on application needs. The JVM interacts with the operating system to commit and decommit native memory pages for Metaspace.

### Metaspace vs. Heap

The Java heap (-Xmx) stores Java object instances. Metaspace stores class metadata. They are completely separate memory regions. An OOM error for one does not affect the other, except that both compete for the same physical RAM. In the Netflix Zuul incident, the heap was stable at ~3GB (well within -Xmx4g), but Metaspace grew from 50MB to 2.5GB, consuming the container's remaining memory.

### ClassLoader Lifecycle and Metaspace Reclamation

When a ClassLoader is loaded, the JVM allocates Metaspace chunks for its class metadata. When the ClassLoader becomes unreachable (eligible for GC), the JVM can reclaim these chunks through class unloading. Class unloading requires:

1. The ClassLoader becomes unreachable (no strong references from any live thread or object)
2. A full GC cycle (CMS or G1 mixed GC) triggers class unloading
3. The JVM decides to reclaim the Metaspace chunks (controlled by -XX:MaxMetaspaceFreeRatio)

In the Zuul incident, condition 1 was never met because the ThreadLocal held a strong reference to the ClassLoader. Conditions 2 and 3 were irrelevant because the ClassLoader was always reachable.

### ThreadLocalMap Internals

Each Thread object has a ThreadLocalMap field. The map uses an array of Entry objects, where Entry extends WeakReference<ThreadLocal>. The key (ThreadLocal reference) is weak, but the value (SecurityContext) is a strong reference. When a ThreadLocal is set to a new value, the old Entry's value reference is replaced, but if any stale entries exist (null key with non-null value), the value object remains strongly referenced and cannot be GC'd.

### Why 30 Minutes Leak Detection is Too Slow

HikariCP's leak detection threshold of 30 minutes meant that a connection held for 29 minutes 59 seconds would not be logged as a leak. In a fast-paced production environment with thousands of requests per second, connections leak in seconds, not minutes. The threshold should be set to seconds (5-10 seconds) to detect leaks in time to alert operators before the pool exhausts.

### Key Diagnostic Commands for Metaspace Analysis

```bash
# Real-time Metaspace monitoring
jcmd <pid> VM.metaspace

# ClassLoader statistics
jcmd <pid> VM.classloader_stats

# Verbose GC logging (add to JVM args)
-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/var/log/gc.log

# Generate heap dump for MAT analysis
jcmd <pid> GC.heap_dump /data/dumps/heap.hprof

# JFR recording with Metaspace events
jcmd <pid> JFR.start name=metaspace_diag settings=profile duration=300s

# Check maximum Metaspace size
jcmd <pid> VM.flags | findstr MetaspaceSize

# Class histogram to identify dominating classes
jcmd <pid> GC.class_histogram | head -30

# Thread dump to check ThreadLocal references
jcmd <pid> Thread.print -l
```

## Detailed Investigation Walkthrough

### Phase 1: Symptom Recognition

The first sign of trouble was the PagerDuty alert at 02:13 UTC. The on-call engineer checked the AWS console and found that all 6 instances in the us-east-1 Zuul cluster were showing "Unhealthy" status. The ASG was automatically replacing them, but within 6 hours, the same pattern would repeat. The engineer checked the JVM crash logs and found `java.lang.OutOfMemoryError: Metaspace` in the hs_err_pid files.

### Phase 2: Data Gathering

The team configured the JVM to capture diagnostic data on the next crash:

```bash
# JVM flags added for next deployment
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/data/dumps/
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-Xloggc:/var/log/gc/gc_%p.log
-XX:StartFlightRecording=name=oom_diag,settings=profile,dumponexit=true,filename=/data/jfr/recording.jfr
```

### Phase 3: Heap Dump Analysis

When the next OOM occurred, the heap dump was 4.2GB. The MAT analysis showed:

1. 80% of the heap was normal application data (HttpRequest, HttpResponse, cached objects)
2. The remaining 20% was dominated by URLClassLoader instances
3. Each URLClassLoader held ~2MB of retained heap
4. The class histogram showed 98,432 class definitions across 1,247 ClassLoaders

The path to GC roots for a representative ClassLoader was:
```
ThreadLocal$ThreadLocalMap.Entry
  → SecurityContext
    → URLClassLoader (dynamic filter loader)
```

This confirmed the ClassLoader was reachable through a ThreadLocal, preventing GC.

## Related Real-World Incidents

| Company | Year | Root Cause | Impact |
|---------|------|------------|--------|
| Netflix | 2018 | ThreadLocal ClassLoader leak in Zuul | OOM every 6 hours |
| Amazon | 2019 | ThreadLocal retention in AWS SDK | Connection pool exhaustion |
| LinkedIn | 2020 | ThreadLocal in request filter chain | Metaspace growth over weeks |
| Twitter | 2017 | InheritableThreadLocal leak in Finagle | OOM after deploy |
| Uber | 2021 | ThreadLocal in tracing library | Gradual performance degradation |

## Best Practices Summary

| Practice | Recommendation | Priority |
|----------|---------------|----------|
| ThreadLocal cleanup | Always use try-finally with remove() | P0 |
| ThreadLocal wrapper | Use WeakThreadLocal for request-scoped data | P0 |
| Metaspace monitoring | Track used, committed, max Metaspace | P0 |
| ClassLoader monitoring | Track active ClassLoader count | P1 |
| Load testing | Run tests for 12+ hours to catch slow leaks | P1 |
| Static analysis | Add Checkstyle rule for ThreadLocal cleanup | P1 |
| Code review | Flag all static ThreadLocal fields for review | P1 |
| JDK version | Migrate to Java 20+ for ScopedValue (JEP 429) | P2 |

## Detailed Lab Setup Instructions

### Environment Requirements
- JDK 11+ (OpenJDK or Oracle JDK)
- Eclipse MAT (Memory Analyzer Tool)
- JDK Mission Control (JMC)
- Python 3.x for analysis scripts
- Docker (optional, for containerized reproduction)

### Setting Up the Lab Environment

1. Download the sample heap dump from the lab repository
2. Load it in Eclipse MAT: File → Open Heap Dump
3. Run the Leak Suspects Report
4. Navigate to the suspect ClassLoader reference chain
5. Identify the ThreadLocal that retains the ClassLoader
6. Trace GC roots using "Path to GC Roots" → "exclude weak references"

### Reproducing the Leak

```bash
# Compile the leaking test application
javac -cp .:zuul-core.jar LeakingFilterRunner.java

# Run with limited Metaspace for faster crash
java -XX:MaxMetaspaceSize=64m -XX:+PrintGCDetails \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/dumps \
     LeakingFilterRunner

# Observe Metaspace growth
jstat -gcmetacapacity <pid> 5s 20
```

### Fixing the Leak

1. Open LeakingFilterRunner.java
2. Add `finally { threadLocal.remove(); }` blocks
3. Replace `new ThreadLocal<>()` with `new WeakThreadLocal<>()`
4. Recompile and run with the same Metaspace limit
5. Verify Metaspace stabilizes using jstat

## Practice Scenarios

### Scenario A: Third-Party Library Leak
You discover that a third-party library (e.g., Apache CXF, Spring Security) uses ThreadLocal internally and does not clean up after request completion. How do you work around this without modifying the library?

*Hint: Use a servlet Filter that calls ThreadLocal.remove() via reflection on the library's internal ThreadLocal fields.*

### Scenario B: InheritableThreadLocal Leak
You find an InheritableThreadLocal in the codebase that passes security context from parent to child threads. The child threads are long-lived and accumulate stale contexts. What's the fix?

*Hint: InheritableThreadLocal.childValue() can return a clean instance. Or use a custom wrapper that clears on thread start.*

### Scenario C: Diagnosing a Production Leak
You notice Metaspace growing at 2MB/hour in production but no OOM has occurred yet. Walk through the investigation steps using the CHECKLIST.md.

*Hint: First check ClassLoader count, then capture thread dumps, then analyze heap dump in MAT.*

## Command Reference Card

```bash
# Essential commands for Metaspace leak investigation

# Check Metaspace usage
jcmd <pid> VM.metadata

# Trigger GC and check Metaspace before/after
jcmd <pid> GC.run
jcmd <pid> VM.metadata  # Should see decrease if not leaked

# Capture heap dump for analysis
jcmd <pid> GC.heap_dump /tmp/heap_$(date +%s).hprof

# Start JFR recording for memory analysis
jcmd <pid> JFR.start name=memory_recording settings=profile duration=120s

# Convert JFR to human-readable
jfr print --events "jdk.ClassLoaderStatistics" /tmp/recording.jfr

# async-profiler memory allocation sampling
profiler.sh -d 60 -e alloc -f /tmp/alloc_flame.html <pid>
```

## FAQ

```bash
# Essential JVM diagnostic commands for Metaspace leak investigation
jcmd <pid> VM.metaspace                    # Metaspace usage breakdown
jcmd <pid> VM.classloader_stats            # ClassLoader instance count
jcmd <pid> GC.class_histogram              # Top 50 classes by instance count
jcmd <pid> GC.heap_dump /tmp/dump.hprof    # Generate heap dump
jcmd <pid> Thread.print -l                # Thread dump with lock info
jstat -gcmetacapacity <pid> 5s 10         # Live Metaspace metrics
jmap -clstats <pid>                       # Detailed ClassLoader stats
jhsdb jmap --heap --pid <pid>            # Heap info
jcmd <pid> JFR.start name=diag settings=profile  # JFR recording
```

## Advanced Investigation Techniques

### Using Eclipse MAT for ClassLoader Analysis

The most effective way to identify a ClassLoader leak in Eclipse MAT:

1. **Load heap dump**: File → Open Heap Dump → Select .hprof file
2. **Run Leak Suspects Report**: Click "Leak Suspects" in the toolbar
3. **Check the suspect list**: Look for entries mentioning "ClassLoader" or "ThreadLocal"
4. **Analyze the dominator tree**: Open Dominator Tree, sort by "Retained Heap", look for URLClassLoader instances
5. **Find paths to GC roots**: Right-click a ClassLoader → "Path to GC Roots" → "exclude weak/soft references"
6. **Identify the retaining reference**: Usually a ThreadLocal or a thread's context ClassLoader

Common patterns in MAT for ThreadLocal leaks:
- OQL Query: `SELECT * FROM java.lang.ThreadLocal$ThreadLocalMap`
- OQL Query: `SELECT * FROM java.net.URLClassLoader WHERE @retainedHeapSize > 1000000`

### Using JFR for Metaspace Analysis

JFR events that are most useful for Metaspace investigation:

1. **jdk.ClassLoaderStatistics**: Shows ClassLoader defineClass count and size per ClassLoader
2. **jdk.ClassLoad**: Individual class loading events — look for repeated loading of the same class
3. **jdk.ClassUnload**: Individual class unloading events — should be non-zero in healthy JVMs
4. **jdk.MetaspaceAllocationFailure**: When Metaspace cannot allocate — triggers OOM
5. **jdk.MetaspaceGCThreshold**: When Metaspace GC is triggered — look for increasing frequency
6. **jdk.MetaspaceChunkFreeListSummary**: Shows internal Metaspace fragmentation

In JDK Mission Control:
1. Open the JFR recording
2. Go to "Memory" → "Metaspace" view
3. Check "Class Loader Statistics" table
4. Sort by "Defined Classes Count" to find the leaking ClassLoader
5. Export the table to CSV for trend analysis over multiple recordings

### GC Log Analysis for Metaspace

Key patterns in GC logs:

```
// Healthy — class unloading happening
[GC (Metadata GC Threshold) 2024-04-15T02:00:00.000+0000: 0.456 secs]
  [Metaspace: 128M->118M(256M)]
  // Class unloading: 47 classes, 3 loaders

// Unhealthy — no class unloading
[GC (Metadata GC Threshold) 2024-04-15T04:00:00.000+0000: 1.234 secs]
  [Metaspace: 512M->498M(1024M)]
  // Class unloading: 0 classes, 0 loaders  ← NO UNLOADING!
```

If "Class unloading: 0 classes, 0 loaders" appears consistently while Metaspace usage increases, a ClassLoader leak is confirmed.

## FAQ

### Q: Why does Metaspace grow but not shrink?
Metaspace does not necessarily shrink when classes are unloaded. The JVM keeps allocated Metaspace chunks for future use rather than returning them to the OS immediately. This is controlled by `-XX:MaxMetaspaceFreeRatio`. A growing Metaspace does not always indicate a leak — it could simply be that the JVM has not triggered class unloading. The key metric is whether Metaspace grows WITHOUT a corresponding increase in class unloading.

### Q: Can this happen with virtual threads (Project Loom)?
Yes, virtual threads can also suffer from ThreadLocal leaks. Each virtual thread has its own ThreadLocalMap. However, since virtual threads are lightweight and short-lived, the leak may be less severe. Java 20+ provides ScopedValue as a safer alternative.

### Q: How is this different from a heap OOM?
Heap OOM occurs when Java objects (instances of classes) fill the heap. Metaspace OOM occurs when class metadata (definitions of classes) fills native memory. The symptoms are similar (OOM error), but the diagnostic approach is different: heap OOM uses heap dump analysis; Metaspace OOM uses ClassLoader analysis and GC logs.

### Q: What's the best tool for analyzing Metaspace leaks?
Eclipse MAT is the standard tool for heap dump analysis, but for Metaspace leaks specifically, JDK Mission Control with JFR recordings is more effective. The JFR events `jdk.ClassLoaderStatistics`, `jdk.ClassLoad`, and `jdk.ClassUnload` provide the best view of class loading/unloading activity.

### Q: Should I set a MaxMetaspaceSize limit?
Yes, always. Without a limit, Metaspace can grow until the OS runs out of memory. Set `-XX:MaxMetaspaceSize=256m` as a reasonable default. This causes earlier OOM errors (fail fast) rather than mysterious kernel OOM kills.

### Q: Can Checkstyle rules detect ThreadLocal leaks?
Yes, custom Checkstyle/ErrorProne rules can detect static ThreadLocal fields without corresponding remove() calls. However, these rules have false positives (e.g., ThreadLocal used for caches where cleanup is not needed). The rules should be configured with an allowlist for known-safe patterns.

## Glossary

| Term | Definition |
|------|------------|
| Metaspace | Native memory region for JVM class metadata (replaced PermGen in Java 8) |
| ClassLoader | JVM component that loads class bytecodes from files/network |
| ThreadLocal | Java construct that stores per-thread values |
| ThreadLocalMap | Internal data structure in Thread that holds ThreadLocal entries |
| WeakReference | Reference type that does not prevent GC of its referent |
| GC Root | Object that is always reachable (static field, stack variable, JNI handle) |
| Retained Heap | Memory that would be freed if an object is GC'd |
| Dominator Tree | MAT analysis showing object dominance hierarchy |
| Shallow Heap | Memory consumed by the object itself (not its references) |
| URLClassLoader | ClassLoader that loads classes from URLs (JARs, directories) |

