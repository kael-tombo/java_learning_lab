# Math Foundation — Records / Sealed / Patterns

## 1. Variant Count
Sealed with n variants → switch arms ≥ n (+null if nullable).
Coverage = `arms / (n + nullable?1:0)` must be 1.0.

## 2. Branch Complexity
Cyclomatic `V = arms + guards`. Keep V ≤ 7 per switch; split beyond.

## 3. Memory: Record vs Class
Record header 12B + components; no extra builder. `size = 12 + Σ fields + pad8`.
Box<Integer> vs int: boxing +16B — prefer primitives.

## 4. equals Cost
Component-wise: `O(k)` field compares. k=5 strings → 5 equals calls.

## 5. Switch Dispatch
tableswitch O(1); instanceof-chain O(n). Prefer switch for n>4.

## 6. Guard Ordering
P(match) ordered; expected checks = `Σ i·p_i`. Put hot variant first.

## 7. Exhaustiveness Proof
Permits closure finite → compiler proves total. Open (non-sealed) → needs default.

## 8. Deconstruction Depth
Cost O(depth). Depth 3 nested → 3 accessor calls; fine.

## Recap
```
coverage = arms/(n+null)
V = arms+guards ≤ 7
size = 12+Σ+pad
E[checks] = Σi·pᵢ
```
Drill: 6-variant Shape, null allowed → arms? Order 3 guards with p=.7/.2/.1.
