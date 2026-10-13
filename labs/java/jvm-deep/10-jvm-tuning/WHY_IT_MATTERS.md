# Why It Matters: JVM Tuning

Every production JVM you operate inherits this lab's numbers: 256M/4G
ergonomics at 16 GB, young as one third of heap, Eden at eight tenths of
young, TLAB allocation at ~10 instructions, compressed references below
32 GB, 240 MB of code cache, unbounded Metaspace. Defaults are the
starting posture of every service; tuning literacy is operating literacy.

The TLAB measurement (~35 vs ~250 ms, ~8x) justifies the single most
common allocation question: no, you should not pool small short-lived
objects — the allocator already beats your pool by removing the lock.
Pooling helps only large, expensive, or humongous-adjacent buffers where
the win is lifecycle control, not allocation speed. The flag stays on;
the pool designs around it.

Capacity-plane separation prevents the costliest misdiagnosis: a
`Metaspace` exhaustion graphed as heap growth buys bigger `-Xmx` for a
classloader leak, and a full code cache graphed as GC pressure buys heap
for a compilation cliff. Pool-level graphs (heap vs CodeHeap vs
Metaspace) route each symptom to its plane before any flag changes.

The one-flag experiment is the transferable skill across labs 06-09:
tier caps isolate JIT effects, pinned heaps isolate collector effects,
interval flags isolate timer effects. Teams that internalize "changed X,
observed Y move, therefore mechanism Z" stop accumulating flag folklore
and start producing reproducible tuning records — the difference between
a runbook and a rumor collection.

The compression cliff deserves its own line in every capacity review:
heaps sized just over 32 GB pay double reference footprint for marginal
extra room, the worst bytes-per-GB trade in the sizing space. Checking
`UseCompressedOops` after every heap resize costs one grep and prevents
the quietest regression this lab covers.

Explicit-GC posture belongs in the same review: one unrestricted
`System.gc()` path hands any caller a full-STW pause button, undoing the
carefullest heap and collector work in a single call. Gate it, log its
cause tokens, and alert on them — posture, not just flags, is the tuning
surface.
