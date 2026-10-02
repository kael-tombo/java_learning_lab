# FLASHCARDS — Profiling

| # | Front | Back |
|---|-------|------|
| 1 | async-profiler overhead? | 1-2% CPU |
| 2 | JFR overhead? | 1-2% |
| 3 | JProfiler overhead? | 10-30% |
| 4 | Sampling vs instrumentation? | Sampling: statistical, low overhead. Instrumentation: exact counts, high overhead. |
| 4 | Flame graph x-axis? | Stack trace population (CPU time proportion) |
| 4 | Flame graph y-axis? | Stack depth |
| 4 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 4 | GC spike correlation? | Correlate GC pause times with p99 latency percentiles |
| 4 | Allocation rate alarm? | > 100 MB/s sustained, or > 10% heap/sec |
| 5 | Lock contention profiling? | async-profiler -e lock, or JFR lock events |
| 5 | Lock contention fix? | Finer locks, lock-free, reduce scope |
| 5 | Flame graph x-axis? | CPU time proportion (population) |
| 5 | Flame graph y-axis? | Stack depth |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |
| 5 | JFR vs async-profiler? | JFR: built-in, rich events. async-profiler: lower overhead, flame graphs, older JDKs. |
| 5 | Memory leak profiling? | JFR/async-profiler alloc profiling → growing live set → heap dump |
| 5 | Allocation rate alarm? | > 100 MB/s or > 10% heap/sec |
| 5 | GC log correlation? | Correlate pause times with latency percentiles |
| 5 | First step on p99 spike? | Check GC / CPU / locks / thread pool |