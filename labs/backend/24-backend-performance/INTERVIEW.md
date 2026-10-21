# Interview: Performance

Q: How to find performance bottlenecks? A: Profiling (async-profiler), APM tools, database query analysis, thread dumps, GC logs.

Q: How to tune GC? A: Set heap size, choose collector (G1GC default), set pause time goal, monitor GC logs, analyze object allocation.

Q: Connection pool sizing? A: Small pool (10-20) often outperforms large pool. Rule: pool = cores * 2 + disk spindles.

Q: How does Caffeine differ from Guava cache? A: Caffeine uses W-TinyLFU for optimal eviction, has near-optimal hit rate, and is generally faster.
