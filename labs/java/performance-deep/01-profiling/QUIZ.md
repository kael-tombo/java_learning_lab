# QUIZ — Java Profiling

## 1. What is the typical overhead of async-profiler sampling?
<details><summary>Answer</summary>1-2% CPU overhead in production.
</details>

## 2. Which profiler is built into the JDK?
<details><summary>Answer</summary>JDK Flight Recorder (JFR), available since JDK 8u40.
</details>

## 3. What's the difference between sampling and instrumentation profiling?
<details><summary>Answer</summary>Sampling periodically samples stack traces (low overhead, statistical). Instrumentation modifies bytecode to count every method call (high overhead, exact counts).
</details>

## 3. Which profiler is best for production CPU profiling?
<details><summary>Answer</summary>async-profiler or JFR — both ~1-2% overhead, safe for production.
</details>

## 4. What does a flame graph show?
<details><summary>Answer</summary>Stack trace aggregation: x-axis = stack trace population, y-axis = stack depth. Width = CPU time proportion.
</details>

## 4. How do you identify GC-induced latency spikes?
<details><summary>Answer</summary>Correlate GC logs (pause times) with latency percentiles. Look for pause time correlation with p99 spikes.
</details>

## 5. What allocation rate suggests a memory problem?
<details><summary>Answer</summary>> 100 MB/s sustained, or > 10% of heap/sec. Correlate with GC frequency.
</details>

## 6. How do you profile lock contention?
<details><summary>Answer</summary>Use async-profiler `-e lock` or JFR lock events. Look for high "blocked" time in threads.
</details>

## 5. What's the first step when p99 latency spikes?
<details><summary>Answer</summary>Check correlation: GC pauses? CPU saturation? Lock contention? Thread pool exhaustion? Then profile the bottleneck.
</details>

## 5. When to use JFR vs async-profiler?
<details><summary>Answer</summary>JFR: built-in, rich events, good for long recordings. async-profiler: lower overhead, flame graphs, works on older JDKs.
</details>

## 6. How to profile memory leaks?
<details><summary>Answer</summary>Use JFR or async-profiler allocation profiling. Look for classes with growing live set, heap dumps for retained objects.
</details>

## 6. What does "allocation rate" mean?
<details><summary>Answer</summary>MB/sec of objects allocated. High rate → GC pressure. Correlate with GC frequency.
</details>