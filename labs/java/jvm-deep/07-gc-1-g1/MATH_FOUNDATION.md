# MATH_FOUNDATION — G1 GC Mathematics

## 1. Region Sizing

### Region Size Calculation

```
Region_Size = Heap_Size / 2048  (target ~2048 regions)
Clamped to [1MB, 32MB]
```

| Heap Size | Region Size | Region Count |
|-----------|-------------|--------------|
| 4 GB      | 2 MB        | 2048         |
| 8 GB      | 4 MB        | 2048         |
| 16 GB     | 8 MB        | 2048         |
| 32 GB     | 16 MB       | 2048         |
| 64 GB     | 32 MB       | 2048         |

---

## 1. Region Sizing Mathematics

### Region Count Formula

```
Target_Regions = 2048 (default)
Region_Size = Heap_Size / Target_Regions
Clamped to [1MB, 32MB]
```

### Region State Machine

```
Free → Eden → Survivor → Old → Humongous
     ↓
   Free (after GC)
```

---

## 1. Region Sizing Mathematics

### Region Count Formula

```
Target_Regions = 2048 (default)
Region_Size = Heap_Size / Target_Regions
Clamped to [1MB, 32MB]
```

### Example Calculations

| Heap Size | Region Size | Region Count |
|-----------|-------------|--------------|
| 4 GB      | 2 MB        | 2048         |
| 8 GB      | 4 MB        | 2048         |
| 16 GB     | 8 MB        | 2048         |
| 32 GB     | 16 MB       | 2048         |
| 64 GB     | 32 MB       | 2048         |

---

## 2. Pause Time Model

### Pause Time Components

```
Total_Pause = Scan_Roots + Update_RSets + Copy_Live + Update_Refs + Post_GC
```

### Target Pause Time

```
Target_Pause = MaxGCPauseMillis (default 200ms)
```

G1 adjusts young generation size to meet target:
```
Young_Gen_Size = f(Live_Data, Target_Pause, Throughput_Goal)
```

### Young GC Pause Model

```
Young_Pause ≈ (Eden_Size + Survivor_Size) / Copy_Rate + RS_Update
```

---

## 1. Pause Time Model

### Pause Time Components

```
Total_Pause = Root_Scan + RS_Update + Copy + Ref_Update + Cleanup
```

### Target Pause Time

```
Target_Pause = MaxGCPauseMillis (default 200ms)
```

G1 adjusts young generation size to meet target:
```
Young_Gen_Size ≈ Target_Pause × Copy_Rate / (1 + Survivor_Ratio)
```

---

## 2. Mixed GC Mathematics

### Old Region Selection

Old regions selected for mixed GC based on **liveness**:

```
Liveness = 1 - (Free_Space / Region_Size)

Region selected if: Liveness < G1MixedGCLiveThresholdPercent (default 85%)
```

### Mixed GC Region Count

```
Max_Regions_Per_Mixed = (Target_Pause - Young_Pause) / Avg_Old_Region_Pause
```

---

## 2. Mixed GC Mathematics

### Liveness Threshold

```
Liveness = 1 - (Free_Space / Region_Size)

Region selected if: Liveness < G1MixedGCLiveThresholdPercent (default 85%)
```

### Regions Per Mixed GC

```
Regions_Per_Mixed = (Target_Pause - Young_Pause) / Avg_Old_Region_Time
```

---

## 2. RSet Mathematics

### RSet Cardinality

```
RSet_Size ≈ Outgoing_Refs / Region_Size
```

Typical: 1-100 entries per region.

### RSet Scan Cost

```
Young_GC_Cost ≈ Σ Young_Region_RSet_Size
```

---

## 2. Remembered Set (RSet) Mathematics

### RSet Cardinality

```
RSet_Size ≈ Outgoing_Refs / Region_Size
```

Typical: 1-100 entries per region.

### RSet Scan Cost

```
Young_GC_Cost ≈ Σ Young_Region_RSet_Size
```

---

## 2. Humongous Object Mathematics

### Humongous Threshold

```
Humongous_Threshold = Region_Size / 2
```

### Region Count for Humongous Object

```
Regions_Needed = ceil(Object_Size / Region_Size)
```

---

## 2. Humongous Object Mathematics

### Humongous Threshold

```
Humongous_Threshold = Region_Size / 2
```

### Regions Needed

```
Regions_Needed = ceil(Object_Size / Region_Size)
```

---

## 2. SATB Barrier Cost

### Snapshot-At-The-Beginning

```
Pre-Write Barrier:
  if (field != new_value) {
      SATB_Queue.enqueue(old_value);
  }
```

### Queue Processing

```
Queue_Capacity = Threads × Buffer_Size
Flush_Threshold = 75% capacity
```

---

## 2. SATB Barrier Cost

### Snapshot-At-The-Beginning

```
Pre-Write Barrier:
  if (field != new_value) SATB_Queue.enqueue(old_value);
```

### Queue Sizing

```
Queue_Capacity = Threads × Buffer_Size
Flush_Threshold = 75% capacity
```

---

## 3. Pause Time Prediction

### Young GC Pause Prediction

```
Young_Pause ≈ (Eden_Size + Survivor_Size) / Copy_Rate + RS_Update_Time
```

Target: `Pause ≤ MaxGCPauseMillis` (default 200ms)

---

## 2. Pause Time Model

### Young GC Pause Prediction

```
Young_Pause ≈ (Eden_Size + Survivor_Size) / Copy_Rate + RS_Update_Time
```

Target: `Pause ≤ MaxGCPauseMillis` (default 200ms)

G1 adjusts young gen size:
```
Young_Gen_Size ≈ Target_Pause × Copy_Rate / (1 + Survivor_Ratio)
```

---

## 3. Mixed GC Region Selection

### Liveness Calculation

```
Liveness = 1 - (Free_Space / Region_Size)

Region selected if: Liveness < G1MixedGCLiveThresholdPercent (default 85%)
```

### Regions Per Mixed GC

```
Regions_Per_Mixed = (Target_Pause - Young_Pause) / Avg_Old_Region_Time
```

---

## 3. Mixed GC Region Selection

### Liveness Threshold

```
Liveness = 1 - (Free_Space / Region_Size)

Selected if: Liveness < G1MixedGCLiveThresholdPercent (default 85%)
```

### Regions Per Mixed GC

```
Regions_Per_Mixed = (Target_Pause - Young_Pause) / Avg_Old_Region_Time
```

---

## 4. Humongous Object Mathematics

### Threshold

```
Humongous_Threshold = Region_Size / 2
```

### Region Count

```
Regions_Needed = ceil(Object_Size / Region_Size)
```

### Allocation Cost

```
Cost = Regions_Needed × Region_Size + Metadata_Overhead
```

---

## 3. Humongous Object Mathematics

### Humongous Threshold

```
Humongous_Threshold = Region_Size / 2
```

### Regions Needed

```
Regions_Needed = ceil(Object_Size / Region_Size)
```

### Allocation Cost

```
Cost = Regions_Needed × Region_Size + Metadata_Overhead
```

---

## 3. RSet Mathematics

### RSet Cardinality

```
RSet_Size ≈ Outgoing_Refs / Region_Size
```

Typical: 1-100 entries per region.

### RSet Scan Cost

```
Young_GC_Cost ≈ Σ Young_Region_RSet_Size
```

---

## 3. RSet Mathematics

### RSet Cardinality

```
RSet_Size ≈ Outgoing_Refs / Region_Size
```

Typical: 1-100 entries per region.

### RSet Scan Cost

```
Young_GC_Cost ≈ Σ Young_Region_RSet_Size
```

---

## 3. SATB Barrier Cost

### Snapshot-At-The-Beginning

```
Pre-Write Barrier:
  if (field != new_value) {
      SATB_Queue.enqueue(old_value);
  }
```

### Queue Processing

```
Queue_Capacity = Threads × Buffer_Size
Flush_Threshold = 75% capacity
```

---

## 3. SATB Barrier Cost

### Snapshot-At-The-Beginning

```
Pre-Write Barrier:
  if (field != new_value) {
      SATB_Queue.enqueue(old_value);
  }
```

### Queue Sizing

```
Queue_Capacity = Threads × Buffer_Size
Flush_Threshold = 75% capacity
```

---

## 4. Predictive Pause Model

### Young GC Pause

```
Pause = (Eden + Survivor) / Copy_Rate + RS_Update
```

Target: ≤ `MaxGCPauseMillis` (default 200ms)

---

## 3. Pause Time Prediction

### Young GC Pause Prediction

```
Pause = (Eden + Survivor) / Copy_Rate + RS_Update
```

Target: `Pause ≤ MaxGCPauseMillis` (default 200ms)

---

## 4. Humongous Object Mathematics

### Humongous Threshold

```
Humongous_Threshold = Region_Size / 2
```

### Regions Needed

```
Regions_Needed = ceil(Object_Size / Region_Size)
```

### Allocation Cost

```
Cost = Regions_Needed × Region_Size + Metadata_Overhead
```

---

## 4. Humongous Object Mathematics

### Humongous Threshold

```
Humongous_Threshold = Region_Size / 2
```

### Regions Needed

```
Regions_Needed = ceil(Object_Size / Region_Size)
```

### Allocation Cost

```
Cost = Regions_Needed × Region_Size + Metadata_Overhead
```

---

## 5. Predictive Pause Model

### Young GC Pause

```
Pause = (Eden + Survivor) / Copy_Rate + RS_Update
```

Target: `Pause ≤ MaxGCPauseMillis` (default 200ms)

---

## 5. Predictive Pause Model

### Young GC Pause

```
Pause = (Eden + Survivor) / Copy_Rate + RS_Update
```

Target: `Pause ≤ MaxGCPauseMillis` (default 200ms)