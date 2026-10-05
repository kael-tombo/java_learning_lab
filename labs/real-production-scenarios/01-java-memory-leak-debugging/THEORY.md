# THEORY — Java Memory Leak Debugging (Incident Mechanics)

## 1. Incident in One Paragraph
A Java memory leak is not C-style lost `free()` — it is **unintentional object retention**: live references prevent GC from reclaiming objects. Heap grows steadily, GC runs longer and more often, Old Gen fills, and the service eventually hits `OutOfMemoryError: Java heap space` or prolonged stop-the-world pauses. In production this looks like a slow-burn incident: latency climbs over hours/days, then sudden cascading restarts.

## 2. Mechanics: Why the Heap Grows
### 2.1 GC Roots and reachability
Objects survive if reachable from GC roots (thread stacks, statics, JNI handles, interned strings). A leak = accidental path from a root (e.g., `static Map` cache without eviction).

### 2.2 Generational heap behavior
Eden → Survivor → Old Gen promotion. Leaked objects promote to Old Gen and never die. Old Gen occupancy trend is the key signal — a sawtooth that never drops after Full GC means leak.

### 2.3 Common leak shapes
- Unbounded static collections (`HashMap` cache, listener lists never deregistered).
- `ThreadLocal` not removed in pooled threads.
- Classloader leaks (redeploys in same JVM, JDBC driver registered twice).
- Forgotten `close()` on resources holding buffers.
- String interning / Metaspace growth (distinct from heap but similar symptom).

### 2.4 GC pressure cascade
As heap fills: Young GC frequency rises → promotion failures → Full GC → long STW pauses (seconds) → readiness probe timeouts → K8s kills pod → restart loop. One pod's death shifts load, accelerating neighbors.

### 2.5 OOMKiller vs OOMError
`OutOfMemoryError` is thrown inside the JVM (heap/metaspace/native). Container OOMKilled (exit 137) happens when RSS exceeds cgroup limit — often caused by heap + direct buffers + thread stacks exceeding the limit.

## 3. Detection Signals
| Signal | Tool | Threshold / pattern |
|---|---|---|
| Old Gen after Full GC rising | JMX / Micrometer `jvm_memory_used_bytes{area="heap"}` | +10% per hour over 6h |
| GC time ratio rising | GC logs (`-Xlog:gc*`), JFR `jdk.GCPhasePause` | >5% CPU in GC sustained |
| Allocation rate spike | JFR allocation profiling, async-profiler `alloc` | 2× baseline |
| Heap dump dominator growth | Eclipse MAT, `jmap -histo` diffs | same class +20% per dump |
| Pod restarts + 137 / OOMError in logs | `kubectl`, log aggregator | any occurrence pages |

## 4. Alert Rules That Work
- `increase(jvm_gc_pause_seconds_sum[15m]) / 900 > 0.05` → warn.
- `jvm_memory_used_bytes / jvm_memory_max_bytes > 0.85 for 30m` → warn; `>0.92 for 10m` → page.
- Log alert on `OutOfMemoryError` or `GC overhead limit exceeded` → page immediately.

## 5. Triage Lifecycle (First 15 Minutes)
1. Confirm scope: one pod or all? Check deploy time correlation.
2. Capture evidence before restart: `jcmd <pid> GC.heap_info`, `jmap -histo:live`, heap dump if safe.
3. Mitigate: rolling restart / traffic shift / increase heap temporarily.
4. Root-cause: MAT dominator tree + path-to-GC-roots.
5. Fix + prevent: bound the cache, fix `ThreadLocal.remove()`, add JMX alert.

## 6. Common Misdiagnoses
- Blaming "GC tuning" when it is a retention bug — tuning only delays OOM.
- Taking one heap dump with no baseline — always take 2–3 spaced dumps and diff.
- Running `jmap -histo:live` triggering Full GC and masking the leak — note the side effect.

## 7. Interview Angle
Explain dominator tree, shallow vs retained heap, and how you would prove a leak from metrics before opening MAT. Mention `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps`.

## 8. Takeaway
Memory incidents are trend incidents. The mechanic is retention; the signal is Old Gen after Full GC; the proof is dump diffs. Mitigate fast, diagnose from retained evidence.
