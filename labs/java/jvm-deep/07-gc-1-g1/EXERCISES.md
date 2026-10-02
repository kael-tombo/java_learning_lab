# EXERCISES — G1 GC

## 1. Region Sizing (Beginner)

**Goal**: Calculate region size for various heap sizes.

**Tasks**:
1. Calculate region size and count for heaps: 2GB, 8GB, 32GB, 64GB
2. What happens if you set `-XX:G1HeapRegionSize=4m` on a 4GB heap?
3. Why does G1 target ~2048 regions?

---

## 2. Pause Time Tuning (Beginner)

**Goal**: Tune G1 pause target.

```bash
# Test different pause targets
-XX:MaxGCPauseMillis=50
-XX:MaxGCPauseMillis=200  # default
-XX:MaxGCPauseMillis=500
```

**Tasks**:
1. Run a load test with different pause targets
2. Measure: young GC frequency, mixed GC frequency, throughput
3. Find the sweet spot for your workload

---

## 2. RSet Size Analysis (Beginner)

**Goal**: Monitor RSet sizes.

```bash
-XX:+PrintGCDetails -XX:+PrintGCDetails -XX:+PrintReferenceGC
```

**Tasks**:
1. Enable GC logging with RSet stats
2. Plot RSet size per region over time
3. Correlate RSet size with young GC duration

---

## 2. RSet Monitoring (Beginner)

**Goal**: Monitor Remembered Set sizes.

```bash
-XX:+PrintGCDetails -XX:+PrintGCDetails -XX:+PrintReferenceGC
```

**Tasks**:
1. Enable GC logging with RSet stats
2. Plot RSet size per region over time
3. Correlate RSet size with young GC duration

---

## 3. Humongous Object Handling (Intermediate)

**Goal**: Understand humongous object impact.

```bash
# Create humongous objects
-XX:G1HeapRegionSize=4m  # 4MB regions
# Allocate 3MB object → humongous
```

**Tasks**:
1. Create objects of various sizes (2MB, 4MB, 8MB, 16MB) with 4MB regions
2. Observe allocation behavior (humongous vs regular)
3. Measure allocation cost difference

---

## 3. Humongous Object Impact (Intermediate)

**Goal**: Measure humongous object overhead.

```bash
# 4MB regions → 2MB humongous threshold
# Allocate 3MB, 4MB, 8MB objects
```

**Tasks**:
1. Create objects at sizes: 2MB, 3MB, 4MB, 8MB with 4MB regions
2. Measure allocation latency
3. Observe humongous region allocation vs regular allocation

---

## 3. Humongous Object Tuning (Intermediate)

**Goal**: Optimize humongous object handling.

```bash
# Tune region size for humongous objects
-XX:G1HeapRegionSize=16m  # Larger regions = fewer humongous objects
```

**Tasks**:
1. Test with 4MB vs 16MB regions for workload with large objects
2. Measure allocation throughput and GC pause impact
3. Determine optimal region size for your object size distribution

---

## 4. Mixed GC Tuning (Intermediate)

**Goal**: Tune mixed GC behavior.

```bash
# Tune mixed GC trigger
-XX:InitiatingHeapOccupancyPercent=30  # earlier mixed GCs

# Tune liveness threshold
-XX:G1MixedGCLiveThresholdPercent=75  # more aggressive
```

**Tasks**:
1. Reduce `InitiatingHeapOccupancyPercent` to 30, observe mixed GC frequency
2. Lower `G1MixedGCLiveThresholdPercent` to 75, observe old gen reclamation
3. Monitor: mixed GC frequency, old gen occupancy, pause times

---

## 4. Mixed GC Tuning (Intermediate)

**Goal**: Tune mixed GC aggressiveness.

```bash
# Earlier mixed GCs
-XX:InitiatingHeapOccupancyPercent=30

# More aggressive old gen reclamation
-XX:G1MixedGCLiveThresholdPercent=75
```

**Tasks**:
1. Reduce `InitiatingHeapOccupancyPercent` to 30, observe mixed GC frequency
2. Lower `G1MixedGCLiveThresholdPercent` to 75, observe old gen reclamation
3. Monitor: mixed GC frequency, old gen occupancy, pause times

---

## 4. SATB Barrier Overhead (Advanced)

**Goal**: Measure SATB overhead.

```bash
# Compare with/without SATB (requires custom JVM build or -XX:-UseSATBBarrier)
# Not directly testable in stock JDK, but can approximate:
```

**Tasks**:
1. Profile SATB queue size during GC
2. Measure barrier overhead with `-XX:+PrintSATBStatistics` (if available)
3. Estimate overhead: queue size × flush frequency

---

## 4. SATB Barrier Overhead (Advanced)

**Goal**: Measure SATB overhead.

```bash
# Not directly testable in stock JDK, but can approximate:
-XX:+PrintSATBStatistics  # if available in debug builds
```

**Tasks**:
1. Profile SATB queue size during GC
2. Measure barrier overhead with custom JVM build or approximation
3. Correlate queue flushes with GC pause time

---

## 5. Mixed GC Tuning (Advanced)

**Goal**: Optimize mixed GC behavior.

```bash
# Earlier mixed GCs
-XX:InitiatingHeapOccupancyPercent=30

# More aggressive old gen reclamation
-XX:G1MixedGCLiveThresholdPercent=75
```

**Tasks**:
1. Reduce `InitiatingHeapOccupancyPercent` to 30, observe mixed GC frequency
2. Lower `G1MixedGCLiveThresholdPercent` to 75, observe old gen reclamation
3. Monitor: mixed GC frequency, old gen occupancy, pause times