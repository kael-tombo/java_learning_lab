# EXERCISES — JIT Compilation

## 1. Observing Compilation (Beginner)

**Goal**: Observe JIT compilation in action.

```bash
# Run with compilation logging
java -XX:+PrintCompilation -XX:+PrintInlining MyApp

# Run with tiered compilation disabled (C1 only)
java -XX:TieredStopAtLevel=1 MyApp

# Run with C2 only
java -XX:TieredStopAtLevel=4 MyApp
```

**Tasks**:
1. Run a simple benchmark with `-XX:+PrintCompilation`
2. Identify which methods get compiled at which tier
3. Observe inlining decisions in output
4. Compare startup time with/without tiered compilation

---

## 2. Inlining Analysis (Intermediate)

**Goal**: Understand inlining decisions.

```bash
# Detailed inlining output
java -XX:+PrintCompilation -XX:+PrintInlining MyApp

# Focus on specific method
java -XX:+PrintCompilation -XX:+PrintInlining -XX:CompileCommand=inline,MyClass.myMethod MyApp
```

**Tasks**:
1. Run a benchmark with `-XX:+PrintInlining`
2. Identify which methods get inlined vs not
3. Use `-XX:MaxInlineSize=100` to force more inlining, observe effect
4. Use `-XX:MaxInlineSize=10` to restrict inlining, measure impact

---

## 3. Escape Analysis & Scalar Replacement (Intermediate)

**Goal**: Observe escape analysis and scalar replacement.

```bash
# Enable escape analysis logging
-XX:+UnlockDiagnosticVMOptions -XX:+PrintEscapeAnalysis

# Or use JFR
-XX:StartFlightRecording:filename=profile.jfr
```

**Tasks**:
1. Write a benchmark that creates objects in a loop
2. Run with `-XX:+DoEscapeAnalysis` (default on) and `-XX:-DoEscapeAnalysis`
3. Compare allocation rates and GC pressure
3. Use JFR to visualize allocation sites

---

## 4. Deoptimization Analysis (Advanced)

**Goal**: Observe deoptimization events.

```bash
# Log deoptimizations
java -XX:+PrintDeoptimizationDetails -XX:+UnlockDiagnosticVMOptions MyApp

# Or with JFR
-XX:StartFlightRecording:filename=profile.jfr,duration=60s
```

**Tasks**:
1. Write code that triggers deoptimization (e.g., polymorphic call site that becomes megamorphic)
2. Observe deoptimization events
3. Measure recompilation overhead

---

## 5. Tiered Compilation Experiments (Advanced)

**Goal**: Compare compilation tiers.

```bash
# Interpreter only
java -Xint MyApp

# C1 only
java -XX:TieredStopAtLevel=1 MyApp

# C1 + C2 (default)
java -XX:TieredStopAtLevel=4 MyApp

# C2 only (after warmup)
java -XX:TieredStopAtLevel=4 -XX:InitialCodeCacheSize=64m MyApp
```

**Tasks**:
1. Benchmark same workload at each tier
2. Measure startup time, peak throughput, steady-state throughput
3. Plot compilation activity over time (use JFR)

---

## 6. Assembly Output (Advanced)

**Goal**: Read generated assembly.

```bash
# Requires hsdis library
java -XX:+UnlockDiagnosticVMOptions -XX:+PrintAssembly MyApp

# Focus on specific method
-XX:CompileCommand=print,MyClass.myMethod
```

**Tasks**:
1. Install hsdis for your platform
2. Print assembly for a hot method
3. Identify: loop unrolling, vectorization, bounds check elimination
4. Compare C1 vs C2 output for same method