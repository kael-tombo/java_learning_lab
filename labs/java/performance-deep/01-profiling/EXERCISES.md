# EXERCISES — Java Profiling

## 1. Baseline Profiling (Beginner)

**Goal**: Profile a simple CPU-intensive program with async-profiler.

```bash
# Build and run
java -jar target/benchmark.jar

# Profile for 30 seconds
./profiler.sh -d 30 -e cpu -f flamegraph.html <pid>
```

**Tasks**:
1. Identify top 3 methods by CPU time
2. Generate flame graph, identify hot path
3. Modify code to reduce top method's complexity
4. Re-profile, compare flame graphs

**Deliverable**: Before/after flame graphs + 3-line summary

---

## 2. Memory Allocation Profiling (Beginner)

**Goal**: Find allocation hotspots.

```bash
./profiler.sh -d 30 -e alloc -f alloc.html <pid>
```

**Tasks**:
1. Identify top 3 allocation sites
2. Calculate allocation rate (MB/s)
3. Propose one optimization (object reuse, pooling, escape analysis)
4. Re-profile, measure allocation rate reduction

---

## 3. Lock Contention Analysis (Intermediate)

**Goal**: Find lock contention hotspots.

```bash
./profiler.sh -d 30 -e lock -f locks.html <pid>
```

**Tasks**:
1. Identify top 3 contended locks
2. Calculate contention ratio (blocked time / total time)
3. Propose fix: finer-grained locks, lock-free, or reduced scope
4. Re-profile, measure throughput improvement

---

## 4. GC Analysis (Intermediate)

**Goal**: Correlate GC behavior with latency spikes.

```bash
# Enable GC logging
-Xlog:gc*:file=gc.log:time,uptime,level,tags

# Or use JFR
./profiler.sh -d 60 -e gc -f gc.jfr <pid>
```

**Tasks**:
1. Parse GC logs: young/old frequency, pause times
2. Identify if latency spikes correlate with GC
3. Propose GC tuning (heap size, GC algorithm, sizing)
4. Validate with load test

---

## 5. Flame Graph Comparison (Advanced)

**Goal**: Quantify optimization impact.

1. Run baseline profile, save flame graph
2. Apply optimization (e.g., cache, algorithm change)
3. Re-profile, generate new flame graph
4. Use `difffolded.pl` to generate diff flame graph
4. Quantify: "Method X reduced from 40% to 15% CPU"

---

## 6. Production Profiling Checklist

Create a runbook for production profiling:

```
[ ] Alert fires (p99 latency > SLA)
[ ] Check dashboards: CPU, GC, threads, latency
[ ] Start async-profiler (30s, CPU)
[ ] Download flame graph
[ ] Identify top 3 methods
[ ] Check recent deploy correlation
[ ] Rollback or hotfix
[ ] Document in incident report
```