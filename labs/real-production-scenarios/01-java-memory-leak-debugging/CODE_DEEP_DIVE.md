# CODE_DEEP_DIVE — Memory Leak Debugging

## 1. Pre-Restart Evidence (run BEFORE restart)
```bash
jcmd 1 GC.heap_info
jcmd 1 VM.flags | grep -i heap
jcmd 1 GC.class_histogram | head -30
jmap -histo:live 1 | head -40   # note: triggers Full GC
```

## 2. Heap Dump Safely
```bash
# auto on OOM (set at startup)
java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps/oom.hprof -jar app.jar
# manual live dump
jmap -dump:live,format=b,file=/tmp/heap-$(date +%s).hprof 1
ls -lh /tmp/*.hprof
# K8s copy out
kubectl exec deploy/api -- jmap -dump:live,format=b,file=/tmp/heap.hprof 1
kubectl cp api-pod:/tmp/heap.hprof ./heap.hprof
```

## 3. GC Logging + JFR
```bash
java -Xlog:gc*,gc+phases=debug:file=/logs/gc.log:time,uptime,level,tags -jar app.jar
jcmd 1 JFR.start name=leak,settings=profile,filename=/tmp/leak.jfr duration=300s
jcmd 1 JFR.dump name=leak filename=/tmp/leak2.jfr
jfr print --events jdk.GarbageCollection,jdk.GCPhasePause /tmp/leak.jfr | head -60
```

## 4. async-profiler Allocation Flame
```bash
./profiler.sh -e alloc -d 60 -f /tmp/alloc.html 1
./profiler.sh -e cpu -d 60 -f /tmp/cpu.html 1   # correlate GC vs app CPU
```

## 5. Native / Direct Memory
```bash
jcmd 1 VM.native_memory detail | head -80
# needs -XX:NativeMemoryTracking=detail at startup
jcmd 1 VM.native_memory baseline && sleep 300 && jcmd 1 VM.native_memory summary.diff
```

## 6. Log Snippets to Recognize
```
# heap exhaustion
java.lang.OutOfMemoryError: Java heap space
	at java.util.Arrays.copyOf(Arrays.java:3237)
	at com.acme.OrderCache.put(OrderCache.java:42)
# thrash
java.lang.OutOfMemoryError: GC overhead limit exceeded
# metaspace (different fix!)
java.lang.OutOfMemoryError: Metaspace
# container kill (no stack — check kubectl)
kubectl describe pod api-xyz  # Last State: Terminated, Reason: OOMKilled, Exit Code: 137
```

## 7. Leaky vs Fixed Code
```java
// LEAKY: unbounded static cache
private static final Map<String, OrderDTO> CACHE = new HashMap<>();
public void put(String k, OrderDTO v) { CACHE.put(k, v); } // never evicted!
// FIXED: bounded with TTL
private final Cache<String, OrderDTO> cache = Caffeine.newBuilder()
  .maximumSize(10_000).expireAfterWrite(Duration.ofMinutes(30))
  .evictionListener((k,v,c)->metrics.increment("cache.eviction")).build();

// LEAKY ThreadLocal
private static final ThreadLocal<byte[]> BUF = ThreadLocal.withInitial(()->new byte[1<<20]);
// FIXED: always clean in pools
try { use(BUF.get()); } finally { BUF.remove(); }
```

## 8. MAT Workflow
1. Open hprof → Dominator Tree → sort by Retained Heap.
2. Right-click suspect → Path to GC Roots → exclude weak refs.
3. Compare 3 dumps: Histogram → Compare Basket → growth % per class.

## 9. Checklist Before You Leave
Heap trend dashboard + auto-dump flags + bounded-cache review in PR checklist.
