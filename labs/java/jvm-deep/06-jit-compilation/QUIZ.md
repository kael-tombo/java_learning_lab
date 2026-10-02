# QUIZ — JIT Compilation

## 1. What are the compilation tiers in tiered compilation?
<details><summary>Answer</summary>0: Interpreter, 1: C1 (Client), 2: C1 (profiled), 3: C2 (Server), 4: C2 (fully optimized).
</details>

## 2. What triggers compilation from tier 0 to tier 1?
<details><summary>Answer</summary>Invocation counter reaches threshold (~1,500 by default).
</details>

## 2. What triggers C1 → C2 compilation?
<details><summary>Answer</summary>Invocation counter + back-edge counter exceed thresholds (e.g., 10k/20k).
</details>

## 3. What is the primary difference between C1 and C2?
<details><summary>Answer</summary>C1: fast compilation, basic optimizations. C2: aggressive optimizations with profiling data, speculative optimizations.
</details>

## 3. What is the main difference between C1 and C2?
<details><summary>Answer</summary>C1: fast compilation, basic optimizations. C2: aggressive optimizations with profiling data, speculative optimizations.
</details>

## 4. What is escape analysis?
<details><summary>Answer</summary>Determines if an object escapes the method/thread. If not, enables scalar replacement (eliminates allocation).
</details>

## 4. What is scalar replacement?
<details><summary>Answer</summary>Replaces object allocation with scalar variables (fields become local variables), eliminating allocation and GC pressure.
</details>

## 5. What is speculative optimization?
<details><summary>Answer</summary>C2 assumes invariants (monomorphic call, null check always true) and optimizes; if wrong, deoptimizes.
</details>

## 5. What is deoptimization?
<details><summary>Answer</summary>When speculative assumption fails, JVM discards compiled code, reverts to interpreter, recompiles with weaker assumptions.
</details>

## 6. What is the "breaking latency" metric?
<details><summary>Answer</summary>Point where latency grows exponentially with throughput; used by Atlassian as JIT benchmark metric.
</details>

## 5. What is an uncommon trap?
<details><summary>Answer</summary>Deoptimization trigger when speculative assumption fails; transfers control to interpreter.
</details>

## 6. What is tiered compilation?
<details><summary>Answer</summary>Multiple compilation levels (Interpreter → C1 → C2) with increasing optimization; balances startup vs peak performance.
</details>

## 6. What is `TieredStopAtLevel`?
<details><summary>Answer</summary>JVM flag to stop compilation at specific tier (0=interpreter, 1=C1, 4=full C2).
</details>

## 7. What is `PrintCompilation`?
<details><summary>Answer</summary>JVM flag to log compilation events (method, tier, size, time).
</details>

## 7. What is `PrintInlining`?
<details><summary>Answer</summary>JVM flag to log inlining decisions (what was inlined, what wasn't, why).
</details>

## 8. What is an uncommon trap?
<details><summary>Answer</summary>Deoptimization trigger when speculative assumption fails; transfers to interpreter.
</details>

## 8. What is an uncommon trap?
<details><summary>Answer</summary>Deoptimization trigger when speculative assumption fails; transfers control to interpreter.
</details>

## 9. What is `PrintAssembly`?
<details><summary>Answer</summary>Prints generated assembly code (requires hsdis library).
</details>

## 9. What is `PrintAssembly`?
<details><summary>Answer</summary>Prints generated assembly code (requires hsdis library).
</details>

## 10. What is `TieredStopAtLevel`?
<details><summary>Answer</summary>JVM flag to stop compilation at specific tier (0=interpreter, 1=C1, 4=full).
</details>