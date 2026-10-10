# Exercises: Bloom Filter

## 1. Toy add/query by hand

m=16, k=2 (positions given): add apple {3,9}, pear {9,14}; query apple
(hit), fig {9,14} (false positive), melon {5,11} (absent via bit 5).
Assert each outcome class appears.

## 2. Measure the FPR ladder

```java
// n=10000 random strings, m=95851; sweep k = 1,3,5,7,10
// query 20k fresh strings, record FPR; expect ~9.9/1.9/1.1/1.0/1.3%
// compare against (1-e^(-kn/m))^k computed in code
```

## 3. Derive-and-verify sizing

Implement `m(n,p)`, `k(m,n)`; assert (10000, 0.01) → (95851, 7).
Build, fill to n, measure FPR ≈ 1% and set-bit fraction ≈ 1/2.

## 4. Break it three ways (then fix)

(a) raw hashCode halves without finalizer → FPR overshoot; (b) even h2 →
position histogram clumps on half the array; (c) int position math →
negative/overflow slots. Fix each, show histogram flatten + FPR recovery.

## 5. Union drill

Two filters, same params, disjoint 5k sets each; OR words; assert union
contains all 10k and FPR ≈ design p. Repeat with mismatched m and show
garbage (assert parameter check rejects).

## 6. Gate-and-fallback benchmark

Simulate LSM reads: 1M lookups, 95% absent, filter (12KB) + HashSet
fallback vs HashSet-only. Count avoided fallback probes; compute memory
saved per avoided I/O at your p.
