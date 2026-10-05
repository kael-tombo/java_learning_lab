# FLASHCARDS — Memory Leak Debugging

| # | Front | Back |
|---|---|---|
| 1 | Define Java memory leak in one sentence | Unintentional live references keep objects reachable so GC cannot reclaim them |
| 2 | GC roots include what 4 things? | Thread stacks, static fields, JNI handles, interned strings / class metadata |
| 3 | Key metric proving a leak? | Old Gen occupancy after Full GC trends upward over time |
| 4 | Shallow vs retained heap? | Shallow = object itself; retained = object + everything freed if it were collected |
| 5 | What is a dominator tree? | MAT view showing which objects dominate (retain) the most heap |
| 6 | `jmap -histo:live` side effect? | Triggers Full GC before histogram — masks garbage, shows only live set |
| 7 | JVM flags for auto heap dump? | `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps` |
| 8 | `jcmd` heap overview command? | `jcmd <pid> GC.heap_info` |
| 9 | Live heap dump command? | `jmap -dump:live,format=b,file=/tmp/heap.hprof <pid>` |
| 10 | `GC overhead limit exceeded` means? | >98% time in GC recovering <2% heap — near-OOM thrash state |
| 11 | Classic static-cache leak fix? | Bound with LRU / TTL: `Caffeine.newBuilder().maximumSize().expireAfterWrite().build()` |
| 12 | ThreadLocal leak cause? | Pooled thread keeps value after task ends; fix with `finally { tl.remove(); }` |
| 13 | Classloader leak example? | JDBC driver or logger registered in static of redeployed WAR never deregistered |
| 14 | Metaspace OOM differs how? | `OutOfMemoryError: Metaspace` — class metadata, check dynamic proxies / redeploys |
| 15 | Container exit 137 means? | OOMKilled by cgroup — RSS exceeded limit, not necessarily JVM heap OOM |
| 16 | GC time ratio alert threshold? | Warn when GC CPU fraction >5% sustained over 15m |
| 17 | Heap usage page threshold? | >92% for 10m pages; >85% for 30m warns |
| 18 | Why take 3 heap dumps? | One dump has no trend; spaced diffs prove growth rate and leaking class |
| 19 | JFR event for GC pauses? | `jdk.GCPhasePause` / `jdk.GarbageCollection` |
| 20 | async-profiler alloc mode? | `./profiler.sh -e alloc -d 60 -f alloc.html <pid>` |
| 21 | Micrometer heap metric name? | `jvm_memory_used_bytes{area="heap"}` vs `jvm_memory_max_bytes` |
| 22 | Promotion failure symptom? | ParNew/CMS or G1 evacuation failure → Full GC + long pause |
| 23 | Listener leak fix? | Use `WeakReference` listeners or explicit deregister on close |
| 24 | First 5-min mitigation? | Capture `heap_info` + histo, then rolling restart / shift traffic |
| 25 | Long-term prevention? | Bounded caches, leak-detection tests, heap-trend dashboards, load-test soak |
| 26 | MAT "path to GC roots" answers? | Which reference chain keeps the leaking object alive |
| 27 | DirectByteBuffer leak signal? | RSS >> heap; track `jdk.DirectBufferStatistics` / NMT |
| 28 | NMT command? | `jcmd <pid> VM.native_memory detail` (needs `-XX:NativeMemoryTracking=detail`) |
| 29 | Safe dump in K8s? | `kubectl exec` dump to emptyDir, then `kubectl cp`; avoid filling overlay |
| 30 | Postmortem must include? | Trend graph, dominator evidence, fix, detection gap, action items |
