# MATH_FOUNDATION — JIT Compilation Mathematics

## 1. Compilation Tier Mathematics

### Compilation Thresholds

| Transition | Counter | Default Threshold |
|------------|---------|-------------------|
| 0 → 1 (Interp → C1) | Invocation count | 1,500 |
| 1 → 2 (C1 profiled) | Invocation + back-edge | 5,000 / 10,000 |
| 2 → 3 (C1 → C2) | Invocation + back-edge | 10,000 / 20,000 |
| 3 → 4 (C2 → Full C2) | Invocation + back-edge | 15,000 / 30,000 |

### Counter Mathematics

```
Invocation Counter: increments on method entry
Back-edge Counter: increments on loop back-edge (branch to loop header)

Total Score = Invocation_Count + Back_Edge_Count
```

---

## 1. Compilation Thresholds

### Invocation Counting

```
Interpreter → C1:  invocation_count > CompileThreshold (default 1500)
C1 → C2: invocation_count > CompileThreshold * 10 (default 10,000)
```

### Back-Edge Counting

```
Loop back-edge counter increments on each backward branch.
C1 → C2 when: back_edge_count > BackEdgeThreshold (default 10,000)
```

---

## 2. Inlining Mathematics

### Inlining Decision Function

```
Inline if: (benefit > cost) AND (size < threshold) AND (hotness > threshold)

Benefit ≈ call_overhead_saved × frequency
Cost = code_size_increase
```

### Inlining Thresholds

| Compiler | Max Inline Size | Frequent Threshold |
|----------|----------------|-------------------|
| C1 | 35 bytes | 1,500 invocations |
| C2 | 325 bytes | 10,000 |

### Inlining Benefit Formula

```
Benefit = Call_Overhead × Frequency × Inline_Probability
Cost = Code_Size_Increase × ICache_Pressure

Inline if: Benefit > Cost × Threshold_Factor
```

---

## 1. Inlining Decision Mathematics

### Inlining Benefit/Cost Model

```
Benefit = Call_Overhead_Saved × Execution_Frequency
Cost = Code_Size_Increase × I_Cache_Pressure

Inline if: Benefit > Cost × Threshold
```

### Inlining Thresholds (Default)

| Compiler | Max Inline Size | Frequent Threshold |
|----------|----------------|-------------------|
| C1 | 35 bytes | 1,500 calls |
| C2 | 325 bytes | 10,000 calls |

### Inlining Benefit Formula

```
Benefit = Call_Overhead_Saved × Execution_Frequency
Cost = Code_Size_Increase × I_Cache_Pressure

Inline if: Benefit > Cost × Threshold_Factor
```

---

## 2. Escape Analysis Mathematics

### Escape State Lattice

```
NoEscape < ArgEscape < GlobalEscape
```

- **NoEscape**: Object doesn't escape method → scalar replacement
- **ArgEscape**: Passed as argument but not stored globally
- **GlobalEscape**: Stored in heap, returned, or thrown

### Scalar Replacement Benefit

```
Allocation Eliminated = Object_Size × Allocation_Frequency
GC_Pressure_Reduction = Allocation_Rate × Object_Size
```

---

## 2. Escape Analysis Mathematics

### Escape State Lattice

```
NoEscape < ArgEscape < GlobalEscape
```

- **NoEscape**: Object never escapes method → scalar replacement
- **ArgEscape**: Passed as argument but not stored
- **GlobalEscape**: Stored in heap, returned, or thrown

### Scalar Replacement Benefit

```
Allocation_Eliminated = Object_Size × Allocation_Rate
GC_Pressure_Reduction = Allocation_Rate × Object_Size
```

---

## 2. Amdahl's Law for JIT Optimization

### Speedup Formula

```
Speedup = 1 / ((1 - f) + f/s)

f = fraction of execution time in optimized code
s = speedup factor for optimized portion
```

### Example: Inlining Hotspot

If a method takes 30% of runtime (f=0.3) and inlining gives 2x speedup (s=2):
```
Speedup = 1 / (0.7 + 0.3/2) = 1 / 0.85 = 1.176x (17.6% faster)
```

---

## 2. Amdahl's Law for JIT

### Speedup Formula

```
Speedup = 1 / ((1 - f) + f/s)

f = fraction of time in optimized code
s = speedup factor of optimized portion
```

### Example

| Hotspot % (f) | Speedup (s=2) | Speedup (s=10) |
|---------------|---------------|----------------|
| 10% | 1.05x | 1.11x |
| 30% | 1.23x | 1.43x |
| 50% | 1.33x | 1.82x |
| 80% | 1.60x | 5.00x |
| 90% | 1.82x | 9.1x |

**Lesson**: Profile first — small hotspots give diminishing returns.

---

## 2. Amdahl's Law for Optimization

### Speedup Formula

```
Speedup = 1 / ((1 - f) + f/s)

f = fraction of runtime in optimized code
s = speedup factor of optimized portion
```

### Example: Inlining 30% Hotspot at 2x

```
Speedup = 1 / (0.7 + 0.3/2) = 1 / 0.85 = 1.176x (17.6% faster)
```

### Inlining Benefit Calculation

```
Benefit = Call_Overhead × Frequency × Inline_Probability
Cost = Code_Size_Increase × I_Cache_Pressure

Inline if: Benefit > Cost × Threshold
```

---

## 3. Queueing Theory for Thread Pools

### M/M/c Queue Model

Thread pool = M/M/c queue:
- Arrival: λ (Poisson)
- Service: μ (exponential)
- Servers: c threads

**Key metrics**:
- Utilization: ρ = λ / (cμ)
- Queue probability: Erlang C formula
- Mean wait: Wq = P(queue) / (cμ - λ)

---

## 3. Queueing Theory for Thread Pools

### M/M/c Model

```
Utilization: ρ = λ / (cμ)
Queue Probability: Erlang C formula
Mean Wait: Wq = P(queue) / (cμ - λ)
```

**Profiling insight**: If ρ > 0.7, queue builds rapidly. Thread pool scaling needed.

---

## 3. Queueing Theory for Thread Pools

### M/M/c Queue Model

Thread pool = M/M/c queue:
- Arrival: Poisson (λ)
- Service: Exponential (μ)
- Servers: c threads

**Metrics**:
- Utilization: `ρ = λ / (cμ)`
- Queue prob: Erlang C formula
- Wait time: `Wq = P(queue) / (cμ - λ)`

**Profiling insight**: If ρ > 0.7, queue builds rapidly → scale threads.

---

## 3. Queueing Theory for Thread Pools

### M/M/c Queue Model

Thread pool = M/M/c queue:
- Arrival: Poisson (λ)
- Service: Exponential (μ)
- Servers: c threads

**Key metrics**:
- Utilization: `ρ = λ / (cμ)`
- Queue prob: Erlang C formula
- Mean wait: `Wq = P(queue) / (cμ - λ)`

**Profiling insight**: If `ρ > 0.7`, queue builds rapidly → scale threads.