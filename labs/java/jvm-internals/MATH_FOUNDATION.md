# MATH_FOUNDATION — JVM Internals

## 1. Probability & Statistics for GC Analysis

### Pause Time Distribution

GC pauses follow a **heavy-tailed distribution** (often log-normal or Weibull).

```math
P(X > x) ~ x^{-α}  (power law tail)
```

**Key Metrics:**
- **p50**: Median pause (typical case)
- **p95/p99**: Tail latency (SLA critical)
- **Max**: Worst-case (capacity planning)

### Little's Law for Heap Sizing

```math
L = λ × W

L = Live set size (bytes)
λ = Allocation rate (bytes/sec)
W = Object lifetime (sec) = Time in heap before GC
```

**Derivation for heap sizing:**
```math
Heap_{min} = λ × T_{gc} × (1 + safety\_margin)
```
Where `T_{gc}` = time between GCs

---

## 2. Queueing Theory for Safepoints

### M/G/1 Queue Model

Safepoint requests arrive as Poisson process, service time is general.

```math
ρ = λ / μ  (utilization)

W_q = ρ / (2μ(1-ρ)) × (1 + C_s²)
```
Where `C_s` = coefficient of variation of service time

**Application:** High `C_s` (variable safepoint duration) → large queue buildup

---

## 3. Amdahl's Law for JIT Speedup

```math
S = 1 / ((1 - P) + P/N)

P = fraction of execution time in hot code
N = speedup factor of compiled vs interpreted (~10-50x)
```

**Example:** If 90% time in hot code (P=0.9), N=20x:
```math
S = 1 / (0.1 + 0.9/20) = 1 / 0.145 = 6.9x overall speedup
```

---

## 4. Cache Performance Modeling

### Cache Miss Rate (3C Model)

```math
Miss Rate = Compulsory + Capacity + Conflict
```

**For object access patterns:**
- **Sequential access** (array): ~1 miss per cache line (64B)
- **Random access** (linked list): ~1 miss per object
- **Strided access**: Depends on stride vs cache line

### False Sharing Cost

```math
Cost = (Cache line ping-pong) × (Coherence protocol latency)

Typical: 50-300 cycles per false sharing event
```

**Padding calculation:**
```math
Padding = Cache line size - (Object size % Cache line size)
= 64 - (24 % 64) = 40 bytes for 24-byte object
```

---

## 5. Compressed OOPs Math

### Address Calculation

```math
Heap Base + (Compressed OOP << Shift) = Real Address
```

**Shift values:**
- 0: Up to 4 GB (no shift)
- 3: Up to 32 GB (8-byte alignment)
- 4: Up to 64 GB (16-byte alignment)

### Max Heap Formula

```math
Max Heap = 2^{32} × Alignment
= 4 GB × Alignment
```

---

## 6. TLAB Sizing Model

### Optimal TLAB Size

```math
TLAB_{optimal} = √(2 × Allocation Rate × TLAB Refill Cost / GC Cost)

Simplified: TLAB ~ 1-2% of Eden size
```

### Refill Rate

```math
Refills/sec = Allocation Rate / TLAB Size

Target: < 1000 refills/sec per thread
```

---

## 6. Code Cache Capacity

### Compilation Rate Model

```math
Code Cache Pressure = (Compilation Rate × Avg Code Size) / Code Cache Size

Steady state: Compilation Rate = Flush Rate (rare)
```

**Typical values:**
- C1: ~1-2 KB per method
- C2: ~2-5 KB per method
- 256 MB cache → ~50K-100K compiled methods

---

## 7. Lock Contention Probability

### Contention Model (M/M/m)

```math
P(wait) = C(m, ρ) = (mρ)^m / (m! (1-ρ)) × P_0

ρ = λ / (mμ)  (utilization per server)
m = number of threads contending
```

**Simplified for biased locking:**
```math
P(revoke) = 1 - (1 - p)^{n-1}
p = probability another thread accesses
n = thread count
```

---

## 8. Escape Analysis Conditions

### Scalar Replacement Criteria

Object `O` can be scalar replaced iff:
1. **No global escape**: Not stored in static field, not returned
2. **No argument escape**: Not passed to unknown code
3. **No synchronization**: Not used in `synchronized(O)`
4. **No identity-sensitive ops**: No `System.identityHashCode`, `==` with external ref

---

## 9. Inlining Decision Math

### Inline Heuristic

```math
Benefit = Call frequency × (Call overhead - Inlined body cost)
Cost = Code size increase × ICache pressure factor

Inline if: Benefit > Cost × Threshold
```

**HotSpot formula:**
```math
Inline if: (Freq × (CallOverhead - BodyCost)) > (Size × ICacheFactor)
```

---

## 10. GC Throughput Formula

### GC Time Fraction

```math
GC Fraction = Total GC Time / (Total GC Time + Application Time)

Throughput = 1 - GC Fraction
```

### Optimal Heap for Throughput

```math
d(Throughput)/d(Heap) = 0

At optimum: Marginal GC time reduction = Marginal allocation rate increase
```

---

## 11. Allocation Rate Estimation

```math
Allocation Rate = (Young Gen Size × Young GC Frequency) / (1 - Survival Rate)

Example: 500 MB Eden, GC every 2 sec, 10% survival
= (500 MB × 0.5/sec) / 0.9 = 277 MB/sec
```

---

## 12. Promotion Rate

```math
Promotion Rate = Allocation Rate × Survival Rate × Tenuring Threshold Factor

Survival Rate = Objects surviving young GC / Total allocated
Tenuring Threshold Factor = Avg age at promotion / MaxTenuringThreshold
```

---

## Summary: Key Formulas Reference

| Concept | Formula |
|---------|---------|
| Little's Law | L = λW |
| Amdahl's Law | S = 1/((1-P)+P/N) |
| Cache Miss (sequential) | 1 miss / 64 bytes |
| Compressed OOPs max heap | 4GB × Alignment |
| TLAB optimal | ~1-2% Eden |
| GC Fraction | GC Time / (GC + App Time) |
| Allocation Rate | YoungSize × GCPreq / (1-Survival) |
| Promotion Rate | AllocRate × Survival × AgeFactor |
| False sharing cost | 50-300 cycles/event |
| Safepoint queue | W_q = ρ/(2μ(1-ρ)) × (1+C_s²) |