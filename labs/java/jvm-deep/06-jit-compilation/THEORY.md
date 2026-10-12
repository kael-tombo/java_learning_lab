# THEORY — JIT Compilation

## Overview

The Just-In-Time (JIT) compiler is the JVM's secret weapon for performance. It transforms hot bytecode into optimized native machine code at runtime, using profiling data gathered during execution.

---

## 1. Compilation Tiers

| Tier | Compiler | Profiling | Role |
|------|----------|-----------|------|
| 0 | Interpreter | collects (invocation + back-edge counters) | first execution, profiling source |
| 1 | C1 | none | quick compile, no profiling overhead |
| 2 | C1 | limited (invocation counters only) | stepping stone, rare to rest here |
| 3 | C1 | full (branch + type profiles) | profile-rich code feeding C2 decisions |
| 4 | C2 | uses profiles gathered at tiers 0–3 | fully optimized, speculative |

(Tier 3 is C1 *with* profiling — not C2. C2 exists only at tier 4.)

### Tier Thresholds (measured defaults, JDK 23 via `PrintFlagsFinal`)

| Transition | Invocation threshold | Back-edge (loop) threshold |
|------------|---------------------|----------------------------|
| → tier 3 (C1 full profile) | 200 (`Tier3InvocationThreshold`) | 60,000 (`Tier3BackEdgeThreshold`) |
| → tier 4 (C2) | 5,000 (`Tier4InvocationThreshold`) | 40,000 (`Tier4BackEdgeThreshold`) |

Compile thresholds (`Tier3CompileThreshold=2000`, `Tier4CompileThreshold=15000`)
scale the raw counters by method size and tier history — small methods
compile sooner. (`CompileThreshold=10000` applies to the *non-tiered*
path, not the default tiered pipeline.) A previous revision of this file
listed 1500/5000/10000-style values — those belong to no current default;
the table above was read off the running JVM.

*Counters decay (not just reset) across GC/safepoints and drop on
redefinition and deoptimization — hotness is a moving average, not a
latch.*

---

## 2. Compilation Pipeline

```
Bytecode → Interpreter → C1 (tiers 1-3) → C2 (tier 4)
              ↓              ↓                  ↓
         Counters +      Quick code;        Speculative,
         branch/type     tiers 2-3 add      profile-driven,
         profiles        profiling          deoptimizable
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

**Heuristics** (measured flag names, JDK 23):
- Hotness (tier-3/tier-4 invocation thresholds above — C1 engages at ~200,
  C2 at ~5000 invocations)
- Method size (< 35 bytes `MaxInlineSize` for regular inlining,
  < 325 bytes `FreqInlineSize` for hot call sites)
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

**Cost**: a deoptimization round-trips through the interpreter and usually
triggers recompilation — microseconds to low milliseconds per event, rare
in steady state (which is why profiles stabilize: uncommon paths stay
uncommon).

---

## 5. Inlining Heuristics

### Inlining Decision Factors

| Factor | C1 | C2 |
|--------|----|----|
| Method size (bytecode) | < 35 bytes (`C1MaxInlineSize`) | < 35 regular / < 325 hot (`MaxInlineSize` / `FreqInlineSize`) |
| Hotness (invocations) | ~200 (tier-3 entry) | ~5000 (tier-4 entry) |
| Call site frequency | High | Very high |
| Recursion | No | Limited depth |
| Synchronization | Yes (lock coarsening/elision apply) | Yes |

### Inline Cache

At polymorphic call sites, C2 builds **inline cache**:
```
if (type == A) A.method()
else if (type == B) B.method()
else slow_path()
```

---

## 6. Graal Compiler

Graal first appeared in OpenJDK as the *experimental* AOT/JIT compiler under
JEP 317 (JDK 10), and that experimental compiler was removed again by JEP 410
(JDK 17). JEP 422 is the Linux/RISC-V port and is unrelated. Graal remains
available via GraalVM, not as a stock OpenJDK component.

### GraalVM JIT

- Written in Java (self-hosted)
- Modular, pluggable
- Advanced optimizations: partial escape analysis, vectorization
- Used in GraalVM; in stock OpenJDK it was experimental (JEP 317) and then removed (JEP 410)

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

# Print deoptimizations (diagnostic; needs UnlockDiagnosticVMOptions)
-XX:+UnlockDiagnosticVMOptions -XX:+TraceDeoptimization

# Disable tiered compilation
-XX:-TieredCompilation

# Force C1 only
-XX:TieredStopAtLevel=1

# Force C2 only
-XX:TieredStopAtLevel=4
```

### JITWatch

Visualize JIT compilation: https://github.com/AdoptOpenJDK/jitwatch