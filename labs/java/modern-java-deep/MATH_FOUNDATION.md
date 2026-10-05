# MATH_FOUNDATION — Modern Java Deep Dive

## 1. Concurrency Mathematics

### Virtual Thread Scalability Model

**Little's Law for Virtual Threads:**
```math
L = λ × W

L = Average virtual threads in system
λ = Arrival rate (requests/sec)
W = Average time in system (service + wait)
```

**Maximum Sustainable Throughput:**
```math
λ_max = N_carriers / (S + W_blocking)

N_carriers = Carrier threads (typically CPU cores)
S = CPU service time per request
W_blocking = Blocking I/O wait time
```

**Example Calculation:**
- 16 vCPU → 16 carrier threads
- CPU work: 2ms/request
- DB wait: 50ms/request
- `λ_max = 16 / (0.002 + 0.050) = 307 req/sec`

With platform threads (1 thread per request, 200 max):
- `λ_max = 200 / 0.052 = 3,846 req/sec` (but 200 thread limit!)

With virtual threads (10,000 concurrent):
- `λ_max = 16 / 0.002 = 8,000 req/sec` (CPU bound) or `16 / 0.052 = 307 req/sec` (I/O bound)

---

### Amdahl's Law for Virtual Thread Adoption

```math
Speedup = 1 / ((1 - P) + P / N)

P = Fraction of workload that benefits from virtual threads
N = Concurrency multiplier (virtual threads / platform threads)
```

**Example:** 80% I/O-bound workload (P=0.8), 100x more concurrency:
```math
Speedup = 1 / (0.2 + 0.8/100) = 1 / 0.208 = 4.8x
```

---

### Queueing Theory: M/M/c Model

**Thread Pool as M/M/c Queue:**
```math
ρ = λ / (c × μ)  (utilization)

P_wait = (cρ)^c / (c! (1-ρ)) × P_0
P_0 = [Σ_{k=0}^{c-1} (cρ)^k/k! + (cρ)^c/(c!(1-ρ))]^{-1}

W_q = P_wait / (cμ(1-ρ))
```

**Virtual threads eliminate queueing delay** by making `c` effectively infinite (bounded only by memory).

---

## 2. Memory Efficiency

### Object Layout Comparison

**Traditional Class (Java 8 style):**
```java
class Point {
    private final int x;
    private final int y;
    // + header (16B) + padding = 24 bytes minimum
}
```

**Record (Java 16+):**
```java
record Point(int x, int y) { }
// Same layout but: compact, final fields, no setters
// Enables: scalar replacement, better escape analysis
```

**Memory per 1M Points:**
| Type | Heap Size |
|------|-----------|
| Class with getters | ~40 MB (object + header + padding) |
| Record | ~32 MB (no extra overhead) |
| Primitive arrays | ~8 MB (`int[2_000_000]`) |

---

### String Template vs Concatenation

**Allocation Analysis:**
```java
// Concatenation (per iteration)
String s = "User: " + name + ", ID: " + id;  // 3 String objects + StringBuilder

// StringBuilder (explicit)
String s = new StringBuilder("User: ").append(name).append(", ID: ").append(id).toString();
// 1 StringBuilder + 1 String

// String Template (STR)
String s = STR."User: \{name}, ID: \{id}";  // 1 String (processor optimizes)
```

**Allocation Rate Comparison (1M ops/sec):**
| Method | Allocations/sec | Heap Pressure |
|--------|-----------------|---------------|
| `+` concat | ~4M objects | High |
| StringBuilder | ~2M objects | Medium |
| String Template | ~1M objects | Low |

---

## 3. Structured Concurrency Mathematics

### Failure Probability

**Independent Task Failure:**
```math
P(system_failure) = 1 - (1 - p)^n

p = individual task failure probability
n = number of parallel tasks
```

**With StructuredTaskScope (cancellation on failure):**
```math
Expected_work_saved = Σ (1 - P(completed_before_failure)) × work_per_task
```

**Example:** 3 services, each 1% failure rate, 100ms avg work:
- Without cancellation: 300ms wasted on failed request
- With cancellation: ~100ms (only failed task completes)

---

### Timeout Optimization

**Optimal Timeout for Parallel Tasks:**
```math
T_optimal = argmin_T [ P(all_complete_by_T) × T + P(timeout) × penalty ]

For exponential service time with rate μ:
P(all_complete_by_T) = (1 - e^{-μT})^n
```

---

## 4. Pattern Matching Performance

### Switch vs If-Else Chain

**Branch Prediction Model:**
```math
Cycles = Base + Misprediction_Penalty × Misprediction_Rate

If-else chain: Misprediction rate ~ 50% for random input
Switch (jump table): Misprediction rate ~ 0% for dense cases
Switch (decision tree): Misprediction rate ~ log₂(n) × 0.5%
```

**Performance Ratio (10 cases):**
```
If-else:  ~5 mispredictions × 15 cycles = 75 cycles overhead
Switch:   ~1 misprediction × 15 cycles = 15 cycles overhead
Ratio:    5x faster for switch
```

---

### Pattern Matching Compilation

**Bytecode Size Reduction:**
```java
// If-else chain
if (x instanceof A) { ... }
else if (x instanceof B) { ... }
else if (x instanceof C) { ... }

// Pattern switch
return switch (x) {
    case A a -> ...
    case B b -> ...
    case C c -> ...
};
```

**Bytecode Comparison:**
| Approach | Bytecode Size | Tableswitch/Lookupswitch |
|----------|---------------|--------------------------|
| If-else chain | O(n) | Multiple if_acmpne |
| Pattern switch | O(n) | Single tableswitch on type ordinal |

---

## 5. Record Serialization Efficiency

### Serialization Overhead

**Traditional POJO + JSON:**
```java
// Object: 40 bytes (header + fields + padding)
// JSON: ~60 bytes (field names repeated)
// Total: ~100 bytes per object
```

**Record + JSON:**
```java
// Object: 24 bytes (compact, no getters/setters)
// JSON: ~60 bytes (same)
// Total: ~84 bytes per object
```

**Binary (Protobuf):**
```protobuf
message Point { int32 x = 1; int32 y = 2; }
// Wire format: ~8 bytes (varint encoding)
```

---

## 6. Virtual Thread Throughput Model

### Throughput Formula

```math
Throughput = min(
    N_carriers / CPU_time_per_request,
    Memory / Stack_per_virtual_thread,
    File_descriptors / Connections_per_request
)
```

**Typical Constraints:**
| Resource | Limit | Virtual Threads Supported |
|----------|-------|---------------------------|
| Carrier threads | 16 (cores) | CPU-bound: 16 concurrent |
| Heap (4GB) | 4GB | ~4M (1KB stack each) |
| File descriptors | 1M | 1M connections |
| Kernel threads | N/A | Not limiting |

**Practical Maximum:**
```math
Max_Virtual_Threads ≈ Heap_GB × 1,000,000  (with 1KB stacks)
                     ≈ 4M for 4GB heap
```

---

## 7. Structured Concurrency Reliability

### Mean Time to Recovery (MTTR)

**Without Structured Concurrency:**
```math
MTTR = T_detect + T_diagnose + T_fix + T_deploy
     = 5min + 30min + 60min + 10min = 105min
```

**With Structured Concurrency (automatic cancellation):**
```math
MTTR = T_detect + T_fix + T_deploy
     = 5min + 60min + 10min = 75min  (30% improvement)
```

---

## 8. Sealed Class Pattern Matching Optimization

### Compiler Optimization

**Exhaustive Switch on Sealed Type:**
```java
sealed interface Shape permits Circle, Square, Triangle { }
record Circle(double r) implements Shape { }
record Square(double s) implements Shape { }
record Triangle(double b, double h) implements Shape { }

double area(Shape s) {
    return switch (s) {
        case Circle c -> Math.PI * c.r() * c.r();
        case Square sq -> sq.s() * sq.s();
        case Triangle t -> t.b() * t.h() / 2;
    };
}
```

**Compiled to:**
```java
// Single tableswitch on ordinal
// No instanceof checks needed
// Direct jump to case handler
```

**Performance:**
| Approach | Cycles per call |
|----------|-----------------|
| Visitor pattern | ~50 (virtual calls) |
| If-else instanceof | ~30 |
| Sealed switch | ~10 (direct jump) |

---

## 9. Foreign Function Interface Overhead

### JNI vs FFI Call Cost

| Call Type | Overhead | Notes |
|-----------|----------|-------|
| JNI (direct) | ~50-100ns | Requires JNIEnv, critical sections |
| JNI (with allocation) | ~200-500ns | NewLocalRef, etc. |
| FFI (downcall) | ~10-20ns | Direct MethodHandle invoke |
| FFI (with memory copy) | ~50-100ns | Arena allocation + copy |

**Speedup:** 5-10x faster than JNI for simple calls

---

## 10. ScopedValue vs ThreadLocal Memory

### Memory Leak Analysis

**ThreadLocal in Thread Pool:**
```java
ThreadLocal<Context> tl = ThreadLocal.withInitial(Context::new);

// In thread pool: 200 threads × 1KB Context = 200KB leaked per pool recycle
// If pool never shrinks: permanent leak
```

**ScopedValue:**
```java
ScopedValue<Context> sv = ScopedValue.newInstance();
// No ThreadLocalMap entry
// Automatic cleanup on scope exit
// Zero memory leak risk
```

**Memory per 10,000 requests:**
| Approach | Leaked Memory |
|----------|---------------|
| ThreadLocal (pooled) | ~10 MB (if not cleaned) |
| ScopedValue | 0 bytes |

---

## Summary: Key Formulas

| Concept | Formula |
|---------|---------|
| Virtual thread throughput | `min(N_carriers/CPU_time, Heap/stack_size)` |
| Speedup (Amdahl) | `1 / ((1-P) + P/N)` |
| M/M/c wait probability | `P_wait = (cρ)^c / (c!(1-ρ)) × P_0` |
| Switch misprediction | `log₂(n) × 0.5%` vs `50%` for if-else |
| Serialization size (record) | `header + fields + padding` |
| FFI call overhead | ~10-20ns (downcall) |
| ScopedValue leak | 0 bytes vs ThreadLocal ~1KB/thread |
| Structured concurrency work saved | `Σ (1-P(complete)) × work` |
| Record memory | `16B header + fields` (no padding waste) |
| String template allocation | 1 String vs 3+ for concatenation |