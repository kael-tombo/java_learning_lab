# THEORY — JIT Compilation

## Overview

The Just-In-Time (JIT) compiler is the JVM's secret weapon for performance. It transforms hot bytecode into optimized native machine code at runtime, using profiling data gathered during execution.

---

## 1. Compilation Tiers

| Tier | Compiler | Trigger | Optimization Level |
|------|----------|---------|-------------------|
| 0 | Interpreter | First execution | None |
| 1 | C1 (Client) | Low threshold | Basic optimizations |
| 2 | C1 (Client) | Higher threshold | More optimizations |
| 3 | C2 (Server) | High threshold | Aggressive optimizations |
| 4 | C2 (Server) | Highest threshold | Full optimization + profiling |

### Tier Thresholds (Default)

| Tier | Invocation Counter | Back-edge Counter |
|------|-------------------|-------------------|
| 0 → 1 | 1,500 | N/A |
| 1 → 2 | 5,000 | 10,000 |
| 2 → 3 | 10,000 | 20,000 |
| 3 → 4 | 15,000 | 30,000 |

*Counters reset on class redefinition, GC, deoptimization.*

---

## 2. Compilation Pipeline

```
Bytecode → Interpreter → C1 (Client) → C2 (Server)
              ↓              ↓           ↓
         Profiling       Light opts    Aggressive opts
         Collection      (no profiling)  + profiling data
```

### C1 (Client Compiler)

- Fast compilation, low overhead
- Basic optimizations: inlining, constant folding, dead code elimination
- No speculative optimization
- Good for short-lived apps, fast startup

### C2 (Server Compiler)

- Aggressive optimizations
- Uses profiling data (type profiles, branch frequencies, call targets)
- Speculative optimizations with deoptimization fallback
- Escape analysis, scalar replacement, loop optimizations

---

## 3. Key Optimizations

### Inlining

```
Original:           Inlined:
foo() { bar(); }    foo() { ...bar body... }
```

**Benefits**: Eliminates call overhead, enables further optimizations (constant propagation, dead code elimination).

**Heuristics**:
- Hotness (invocation count)
- Method size (< 35 bytes default for C1, < 325 for C2)
- Recursion depth
- Hotness of caller

### Escape Analysis & Scalar Replacement

```
Object o = new Object();
o.field = 42;
use(o.field);
```

→ If `o` doesn't escape:
```
int temp = 42;
use(temp);  // Scalar replacement: object eliminated!
```

**Benefits**: No allocation, no GC pressure, better cache locality.

### Loop Optimizations

| Optimization | Description |
|--------------|-------------|
| Loop unrolling | Reduce branch overhead |
| Loop invariant code motion | Hoist invariants out of loop |
| Induction variable elimination | Simplify loop counters |
| Loop unswitching | Move invariant condition out |
| Vectorization | SIMD instructions |

---

## 4. Speculative Optimization & Deoptimization

### Speculative Optimization

C2 makes optimistic assumptions based on profiling:

| Assumption | Example |
|------------|---------|
| Monomorphic call site | `obj.method()` always same type |
| Null check elimination | `if (x != null)` always true |
| Range check elimination | Array index always in bounds |
| Integer overflow | `i + 1` never overflows |

### Deoptimization

When assumption fails:
1. **Uncommon trap** → Transfer to interpreter
2. **Recompile** → Without failed assumption
3. **Resume** → Continue execution

```
Compiled code → Uncommon trap → Interpreter → Recompile (less aggressive) → Compiled
```

**Cost**: ~100-500μs per deoptimization. Rare in steady state.

---

## 5. Inlining Heuristics

### Inlining Decision Factors

| Factor | C1 Threshold | C2 Threshold |
|--------|--------------|--------------|
| Method size (bytecode) | < 35 bytes | < 325 bytes |
| Hotness (invocations) | > 1,500 | > 10,000 |
| Call site frequency | High | Very high |
| Recursion | No | Limited depth |
| Synchronization | No | Yes (with bias) |

### Inline Cache

At polymorphic call sites, C2 builds **inline cache**:
```
if (type == A) A.method()
else if (type == B) B.method()
else slow_path()
```

---

## 6. Graal Compiler (JEP 422+)

### GraalVM JIT

- Written in Java (self-hosted)
- Modular, pluggable
- Advanced optimizations: partial escape analysis, vectorization
- Used in GraalVM, optional in OpenJDK (JEP 422)

```bash
-XX:+UnlockExperimentalVMOptions -XX:+UseJVMCICompiler
```

---

## 7. Debugging JIT

### Useful Flags

```bash
# Print compilation
-XX:+PrintCompilation

# Print inlining decisions
-XX:+PrintInlining

# Print assembly (requires hsdis)
-XX:+PrintAssembly

# Print deoptimizations
-XX:+PrintDeoptimizationDetails

# Disable tiered compilation
-XX:-TieredCompilation

# Force C1 only
-XX:TieredStopAtLevel=1

# Force C2 only
-XX:TieredStopAtLevel=4
```

### JITWatch

Visualize JIT compilation: https://github.com/AdoptOpenJDK/jitwatch